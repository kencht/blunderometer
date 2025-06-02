#!/usr/bin/env python3

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import asyncio
from datetime import datetime, UTC
from sqlalchemy import func
from database_multiuser import db_manager, Game, Move
from main import BlunderTracker
import threading
import json
import os

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)  # Allow all origins for development

# Serve React frontend in production
@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    if os.path.exists('frontend/build/index.html'):
        return app.send_static_file('index.html')
    else:
        return "Frontend not built. Run 'cd frontend && npm run build' first."

# Global state for tracking operations
operation_status = {
    'fetching': False,
    'analyzing': False,
    'last_operation': None,
    'progress': {}
}

@app.route('/api/stats')
def get_stats():
    """Get current database statistics for a specific user with optional time control filtering"""
    username = request.args.get('username', 'default')
    time_control_filter = request.args.get('time_control')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    db = db_manager.get_db(username)
    
    try:
        # Base queries
        games_query = db.query(Game)
        moves_query = db.query(Move)
        
        # Apply time control filter if specified
        if time_control_filter and time_control_filter != 'All':
            games_query = games_query.filter(Game.time_control == time_control_filter)
            moves_query = moves_query.filter(Move.time_control == time_control_filter)
        
        # Game stats
        total_games = games_query.count()
        analyzed_games = games_query.filter(Game.fully_analyzed == True).count()
        unanalyzed_games = total_games - analyzed_games
        
        # Get latest and oldest game dates
        latest_game = games_query.order_by(Game.played_at.desc()).first()
        oldest_game = games_query.order_by(Game.played_at.asc()).first()
        
        # Move stats
        total_moves = moves_query.count()
        blunders = moves_query.filter(Move.is_blunder == True).count()
        mistakes = moves_query.filter(Move.is_mistake == True).count()
        inaccuracies = moves_query.filter(Move.is_inaccuracy == True).count()
        
        # Calculate percentages
        blunder_rate = (blunders / total_moves * 100) if total_moves > 0 else 0
        mistake_rate = (mistakes / total_moves * 100) if total_moves > 0 else 0
        inaccuracy_rate = (inaccuracies / total_moves * 100) if total_moves > 0 else 0
        
        # Time control breakdown (always show all time controls)
        time_controls = db.query(Game.time_control, func.count(Game.id)).group_by(Game.time_control).all()
        
        # Time control specific stats for comparison
        time_control_stats = {}
        for tc_name in ['bullet', 'blitz', 'rapid', 'classical']:
            # Match time controls by common patterns
            tc_filter = None
            if tc_name == 'bullet':
                # Bullet: 120+1 and below (60+0, 60+1, 120+1, etc.)
                tc_filter = (Game.time_control.in_(['60+0', '60+1', '120+1', '180+0']))
            elif tc_name == 'blitz':
                # Blitz: 3+2 to 5+3 typically (but exclude bullet range)
                tc_filter = (Game.time_control.in_(['180+2', '300+0', '300+3']))
            elif tc_name == 'rapid':
                # Rapid: 10-30 minute games
                tc_filter = (Game.time_control.in_(['600+0', '600+5', '900+10', '1800+0']))
            elif tc_name == 'classical':
                # Classical: 30+ minute games
                tc_filter = (Game.time_control.in_(['1800+0', '1800+30', '3600+0']))
            
            if tc_filter is not None:
                # Count games with this time control
                tc_games = db.query(Game).filter(tc_filter).count()
                
                # Count moves from games with this time control - need to join properly
                tc_moves = db.query(Move).join(Game, Move.game_lichess_id == Game.lichess_id).filter(tc_filter).count()
                tc_blunders = db.query(Move).join(Game, Move.game_lichess_id == Game.lichess_id).filter(tc_filter, Move.is_blunder == True).count()
                tc_mistakes = db.query(Move).join(Game, Move.game_lichess_id == Game.lichess_id).filter(tc_filter, Move.is_mistake == True).count()
                
                time_control_stats[tc_name] = {
                    'games': tc_games,
                    'moves': tc_moves,
                    'blunders': tc_blunders,
                    'mistakes': tc_mistakes,
                    'blunder_rate': (tc_blunders / tc_moves * 100) if tc_moves > 0 else 0,
                    'mistake_rate': (tc_mistakes / tc_moves * 100) if tc_moves > 0 else 0
                }
        
        return jsonify({
            'username': username,
            'games': {
                'total': total_games,
                'analyzed': analyzed_games,
                'unanalyzed': unanalyzed_games,
                'analysis_progress': (analyzed_games / total_games * 100) if total_games > 0 else 0,
                'latest_date': latest_game.played_at.isoformat() if latest_game else None,
                'oldest_date': oldest_game.played_at.isoformat() if oldest_game else None
            },
            'moves': {
                'total': total_moves,
                'blunders': blunders,
                'mistakes': mistakes,
                'inaccuracies': inaccuracies,
                'blunder_rate': round(blunder_rate, 2),
                'mistake_rate': round(mistake_rate, 2),
                'inaccuracy_rate': round(inaccuracy_rate, 2)
            },
            'time_controls': [{'name': tc, 'count': count} for tc, count in time_controls],
            'time_control_stats': time_control_stats,
            'operation_status': operation_status
        })
    finally:
        db.close()

@app.route('/api/fetch-games', methods=['POST'])
def fetch_games():
    """Fetch next batch of games"""
    global operation_status
    if operation_status['fetching'] or operation_status['analyzing']:
        return jsonify({'error': 'Another operation is already running'}), 400
    data = request.get_json()
    batch_size = data.get('batch_size', 100)
    fetch_older = data.get('fetch_older', False)
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    # Start fetching in background
    thread = threading.Thread(target=run_fetch_games, args=(username, batch_size, fetch_older))
    thread.start()
    direction = "older" if fetch_older else "newer"
    return jsonify({'message': f'Started fetching {batch_size} {direction} games for {username}'})

@app.route('/api/analyze-games', methods=['POST'])
def analyze_games():
    """Analyze unanalyzed games"""
    global operation_status
    if operation_status['fetching'] or operation_status['analyzing']:
        return jsonify({'error': 'Another operation is already running'}), 400
    data = request.get_json()
    time_limit_per_game = data.get('time_limit_per_game', 20)
    total_time_limit = data.get('total_time_limit')  # Optional total session limit
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    # Start analysis in background
    thread = threading.Thread(target=run_analyze_games, args=(username, time_limit_per_game, total_time_limit))
    thread.start()
    message = f'Started analyzing games for {username} with {time_limit_per_game}s per game'
    if total_time_limit:
        message += f' (max {total_time_limit}s total)'
    return jsonify({'message': message})

def run_fetch_games(username, batch_size, fetch_older=False):
    """Background task to fetch games"""
    global operation_status
    direction = "older" if fetch_older else "newer"
    print(f"[DEBUG] Starting fetch for {username} with batch size {batch_size} ({direction} games)")
    operation_status['fetching'] = True
    operation_status['progress'] = {'stage': 'fetching', 'current': 0, 'total': batch_size}
    try:
        async def fetch():
            print("[DEBUG] Creating BlunderTracker instance")
            tracker = BlunderTracker()
            print(f"[DEBUG] About to call fetch_user_games (fetch_older={fetch_older})")
            result = await tracker.fetch_user_games(username, max_games=batch_size, fetch_older=fetch_older)
            print(f"[DEBUG] fetch_user_games returned: {result}")
            return result
        print("[DEBUG] Creating new asyncio event loop")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("[DEBUG] Running event loop for fetch")
        games_added = loop.run_until_complete(fetch())
        print(f"[DEBUG] Fetch complete, games added: {games_added}")
        loop.close()
        operation_status['last_operation'] = {
            'type': 'fetch',
            'completed_at': datetime.now(UTC).isoformat(),
            'result': f'Added {games_added} new {direction} games for {username}'
        }
    except Exception as e:
        print(f"[ERROR] Exception during fetch: {e}")
        import traceback; traceback.print_exc()
        operation_status['last_operation'] = {
            'type': 'fetch',
            'completed_at': datetime.now(UTC).isoformat(),
            'error': str(e)
        }
    finally:
        operation_status['fetching'] = False
        operation_status['progress'] = {}

def run_analyze_games(username, time_limit_per_game, total_time_limit=None):
    """Background task to analyze games"""
    global operation_status
    operation_status['analyzing'] = True
    
    # Get count of unanalyzed games for progress tracking
    db = db_manager.get_db(username)
    unanalyzed_count = db.query(Game).filter(
        Game.username == username,
        Game.fully_analyzed == False
    ).count()
    db.close()
    
    operation_status['progress'] = {
        'stage': 'analyzing', 
        'current': 0, 
        'total': unanalyzed_count,
        'start_time': datetime.now(UTC).isoformat(),
        'time_limit_per_game': time_limit_per_game,
        'total_time_limit': total_time_limit,
        'current_game': None,
        'games_analyzed': 0,
        'games_skipped': 0
    }
    
    def progress_callback(progress_data):
        """Update global progress state"""
        operation_status['progress'].update(progress_data)
    
    try:
        async def analyze():
            tracker = BlunderTracker(progress_callback=progress_callback)
            return await tracker.analyze_games(
                username, 
                time_limit_per_game_seconds=time_limit_per_game,
                total_time_limit_seconds=total_time_limit
            )
        # Run async function in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(analyze())
        loop.close()
        
        operation_status['last_operation'] = {
            'type': 'analyze',
            'completed_at': datetime.now(UTC).isoformat(),
            'result': f'Analysis completed for {username}: {result["games_analyzed"]} games analyzed, {result["games_skipped"]} skipped'
        }
    except Exception as e:
        operation_status['last_operation'] = {
            'type': 'analyze',
            'completed_at': datetime.now(UTC).isoformat(),
            'error': str(e)
        }
    finally:
        operation_status['analyzing'] = False
        operation_status['progress'] = {}

@app.route('/api/recent-games')
def get_recent_games():
    """Get recent games with analysis status"""
    username = request.args.get('username', 'default')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    db = db_manager.get_db(username)
    try:
        games = db.query(Game).order_by(Game.played_at.desc()).limit(20).all()
        game_list = []
        for game in games:
            moves_count = db.query(Move).filter(Move.game_lichess_id == game.lichess_id).count()
            blunders_count = db.query(Move).filter(
                Move.game_lichess_id == game.lichess_id,
                Move.is_blunder == True
            ).count()
            game_list.append({
                'lichess_id': game.lichess_id,
                'played_at': game.played_at.isoformat(),
                'time_control': game.time_control,
                'opening_name': game.opening_name,
                'user_color': game.user_color,
                'user_rating': game.user_rating,
                'opponent_rating': game.opponent_rating,
                'result': game.result,
                'fully_analyzed': game.fully_analyzed,
                'moves_count': moves_count,
                'blunders_count': blunders_count
            })
        result = jsonify(game_list)
    finally:
        db.close()
    return result

@app.route('/api/blunder-analysis')
def get_blunder_analysis():
    """Get detailed blunder analysis"""
    username = request.args.get('username', 'default')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    db = db_manager.get_db(username)
    try:
        # Recent blunders
        recent_blunders = db.query(Move).filter(Move.is_blunder == True).order_by(Move.played_at.desc()).limit(10).all()
        # Blunders by opening
        opening_blunders = db.query(
            Move.opening_name,
            func.count(Move.id).label('blunder_count'),
            func.count(func.distinct(Move.game_lichess_id)).label('games')
        ).filter(Move.is_blunder == True).group_by(Move.opening_name).order_by(func.count(Move.id).desc()).limit(10).all()
        # Blunders by time control
        time_control_blunders = db.query(
            Move.time_control,
            func.count(Move.id).label('blunder_count')
        ).filter(Move.is_blunder == True).group_by(Move.time_control).all()
        # Average centipawn loss by rating range
        from sqlalchemy import case
        rating_analysis = db.query(
            case(
                (Move.opponent_rating < 1200, 'Under 1200'),
                (Move.opponent_rating < 1400, '1200-1399'),
                (Move.opponent_rating < 1600, '1400-1599'),
                (Move.opponent_rating < 1800, '1600-1799'),
                (Move.opponent_rating >= 1800, '1800+'),
                else_='Unknown'
            ).label('rating_range'),
            func.avg(Move.centipawn_loss).label('avg_cp_loss'),
            func.count(Move.id).label('move_count')
        ).filter(Move.centipawn_loss > 0).group_by('rating_range').all()
        result = jsonify({
            'recent_blunders': [{
                'move_san': blunder.move_san,
                'centipawn_loss': blunder.centipawn_loss,
                'played_at': blunder.played_at.isoformat(),
                'opening_name': blunder.opening_name,
                'opponent_rating': blunder.opponent_rating,
                'game_id': blunder.game_lichess_id
            } for blunder in recent_blunders],
            'opening_blunders': [{
                'opening': opening,
                'blunder_count': count,
                'games': games
            } for opening, count, games in opening_blunders],
            'time_control_blunders': [{
                'time_control': tc,
                'blunder_count': count
            } for tc, count in time_control_blunders],
            'rating_analysis': [{
                'rating_range': rating_range,
                'avg_cp_loss': round(float(avg_cp_loss), 1),
                'move_count': move_count
            } for rating_range, avg_cp_loss, move_count in rating_analysis]
        })
    finally:
        db.close()
    return result

@app.route('/api/performance')
def get_performance_data():
    """Get performance data for charting with optional filters"""
    username = request.args.get('username', 'default')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    db = db_manager.get_db(username)
    try:
        # Get query parameters for filtering
        time_control = request.args.get('timeControl')
        rating_min = request.args.get('ratingRange[0]', type=int)
        rating_max = request.args.get('ratingRange[1]', type=int)
        date_start = request.args.get('dateRange[0]')
        date_end = request.args.get('dateRange[1]')
        
        # Base query for moves with game data
        query = db.query(Move).join(Game, Move.game_lichess_id == Game.lichess_id)
        
        # Apply filters
        if time_control and time_control != 'All':
            # Support 4-category time control classification
            if time_control == 'bullet':
                # Bullet: 120+1 and below (60+0, 60+1, 120+1, etc.)
                query = query.filter(Game.time_control.in_(['60+0', '60+1', '120+1', '180+0']))
            elif time_control == 'blitz':
                # Blitz: 3+2 to 5+3 typically (but exclude bullet range)
                query = query.filter(Game.time_control.in_(['180+2', '300+0', '300+3']))
            elif time_control == 'rapid':
                # Rapid: 10-30 minute games
                query = query.filter(Game.time_control.in_(['600+0', '600+5', '900+10', '1800+0']))
            elif time_control == 'classical':
                # Classical: 30+ minute games
                query = query.filter(Game.time_control.in_(['1800+0', '1800+30', '3600+0']))
            else:
                # Exact time control match (for backwards compatibility)
                query = query.filter(Game.time_control == time_control)
        
        if rating_min and rating_max:
            query = query.filter(Move.opponent_rating >= rating_min, Move.opponent_rating <= rating_max)
        
        if date_start:
            query = query.filter(Move.played_at >= date_start)
        
        if date_end:
            query = query.filter(Move.played_at <= date_end)
        
        # Get moves ordered by date
        moves = query.order_by(Move.played_at).all()
        
        # Group moves by game and calculate performance metrics
        performance_data = []
        game_moves = {}
        
        # Group moves by game
        for move in moves:
            game_id = move.game_lichess_id
            if game_id not in game_moves:
                # Get the corresponding game to access user_rating
                game = db.query(Game).filter(Game.lichess_id == game_id).first()
                user_rating = game.user_rating if game else None
                
                game_moves[game_id] = {
                    'moves': [],
                    'date': move.played_at,
                    'time_control': move.time_control,
                    'opponent_rating': move.opponent_rating,
                    'user_rating': user_rating
                }
            game_moves[game_id]['moves'].append(move)
        
        # Calculate performance for each game
        for game_id, game_data in game_moves.items():
            moves_list = game_data['moves']
            total_moves = len(moves_list)
            
            if total_moves == 0:
                continue
            
            blunders = sum(1 for m in moves_list if m.is_blunder)
            mistakes = sum(1 for m in moves_list if m.is_mistake)
            inaccuracies = sum(1 for m in moves_list if m.is_inaccuracy)
            
            blunder_rate = (blunders / total_moves) * 100
            mistake_rate = (mistakes / total_moves) * 100
            inaccuracy_rate = (inaccuracies / total_moves) * 100
            
            avg_cp_loss = sum(m.centipawn_loss for m in moves_list if m.centipawn_loss > 0) / len([m for m in moves_list if m.centipawn_loss > 0]) if any(m.centipawn_loss > 0 for m in moves_list) else 0
            
            performance_data.append({
                'date': game_data['date'].isoformat(),
                'blunder_rate': blunder_rate,
                'mistake_rate': mistake_rate,
                'inaccuracy_rate': inaccuracy_rate,
                'total_moves': total_moves,
                'avg_centipawn_loss': avg_cp_loss,
                'user_rating': game_data['user_rating'],
                'opponent_rating': game_data['opponent_rating']
            })
        
        # Sort by date
        performance_data.sort(key=lambda x: x['date'])
        result = jsonify(performance_data)
    finally:
        db.close()
    return result

# Configure for cloud deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    # Enable CORS for production
    app.run(host='0.0.0.0', port=port, debug=debug)
