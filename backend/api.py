from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Game, Move
from lichess_client import LichessClient
from chess_analyzer import ChessAnalyzer
from analytics import AnalyticsService
from datetime import datetime
from typing import List, Dict, Optional
import asyncio

router = APIRouter()

@router.post("/users/{username}/analyze")
async def analyze_user_games(
    username: str,
    background_tasks: BackgroundTasks,
    max_games: int = 50,
    game_types: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Start analysis of user's games"""
    
    # Parse game_types from comma-separated string
    parsed_game_types = None
    if game_types:
        parsed_game_types = [gt.strip() for gt in game_types.split(',') if gt.strip()]
    
    # Create or get user
    user = db.query(User).filter(User.lichess_username == username).first()
    if not user:
        user = User(lichess_username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Start background analysis
    background_tasks.add_task(analyze_games_background, user.id, username, max_games, parsed_game_types, db)
    
    return {"message": f"Started analysis for {username}", "user_id": user.id}

async def analyze_games_background(user_id: int, username: str, max_games: int, game_types: Optional[List[str]], db: Session):
    """Background task to analyze games"""
    
    try:
        async with LichessClient() as lichess:
            # Get user's last analyzed date
            user = db.query(User).filter(User.id == user_id).first()
            since = user.last_analyzed if user.last_analyzed else None
            
            # Fetch games from Lichess
            games_data = await lichess.get_user_games(username, max_games, since, game_types)
            
            analyzer = ChessAnalyzer()
            
            for game_data in games_data:
                # Check if game already exists
                existing_game = db.query(Game).filter(
                    Game.lichess_id == game_data['id']
                ).first()
                
                if existing_game and existing_game.analyzed:
                    continue
                
                # Use existing game or create new one
                if existing_game:
                    game = existing_game
                else:
                    # Create game record
                    game = Game(
                        lichess_id=game_data['id'],
                        user_id=user_id,
                        played_at=datetime.fromtimestamp(game_data['createdAt'] / 1000),
                        time_control=f"{game_data['clock']['initial']}+{game_data['clock']['increment']}",
                        variant=game_data.get('variant', 'standard'),
                        opening_name=game_data.get('opening', {}).get('name'),
                        opening_eco=game_data.get('opening', {}).get('eco'),
                        white_username=game_data['players']['white']['user']['name'],
                        black_username=game_data['players']['black']['user']['name'],
                        white_rating=game_data['players']['white'].get('rating'),
                        black_rating=game_data['players']['black'].get('rating'),
                        user_color='white' if game_data['players']['white']['user']['name'].lower() == username.lower() else 'black',
                        result=game_data.get('status'),
                        termination=game_data.get('status')
                    )
                    
                    # Set user rating and opponent rating
                    if game.user_color == 'white':
                        game.user_rating = game.white_rating
                        game.opponent_rating = game.black_rating
                    else:
                        game.user_rating = game.black_rating
                        game.opponent_rating = game.white_rating
                    
                    db.add(game)
                    db.commit()
                    db.refresh(game)
                
                # Parse moves from PGN
                pgn_moves = lichess.parse_pgn_moves(game_data.get('pgn', ''))
                
                # Analyze moves
                analyzed_moves = await analyzer.analyze_game(pgn_moves)
                
                # Save move analysis
                moves_saved = 0
                for move_data in analyzed_moves:
                    move = Move(
                        game_id=game.id,
                        move_number=move_data['move_number'],
                        color=move_data['color'],
                        move_san=move_data['move_san'],
                        move_uci=move_data['move_uci'],
                        evaluation_before=move_data['evaluation_before'],
                        evaluation_after=move_data['evaluation_after'],
                        evaluation_diff=move_data['evaluation_diff'],
                        best_move_san=move_data['best_move_san'],
                        best_move_uci=move_data['best_move_uci'],
                        is_user_move=(move_data['color'] == game.user_color),
                        is_mistake=move_data['is_mistake'],
                        is_blunder=move_data['is_blunder'],
                        is_inaccuracy=move_data['is_inaccuracy']
                    )
                    db.add(move)
                    moves_saved += 1
                
                # Only mark game as analyzed if moves were successfully saved
                if moves_saved > 0:
                    game.analyzed = True
                    game.analysis_completed_at = datetime.utcnow()
                    print(f"Game {game.lichess_id}: Successfully analyzed {moves_saved} moves")
                else:
                    print(f"Game {game.lichess_id}: No moves analyzed - not marking as complete")
                
                db.commit()
            
            # Update user's last analyzed timestamp
            user.last_analyzed = datetime.utcnow()
            db.commit()
            
    except Exception as e:
        print(f"Error in background analysis: {e}")

@router.get("/users/{username}/analytics/mistake-rates")
async def get_mistake_rates(
    username: str,
    rolling_window: int = 20,
    db: Session = Depends(get_db)
):
    """Get mistake rates as percentages over rolling window of games"""
    
    user = db.query(User).filter(User.lichess_username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    analytics = AnalyticsService(db)
    results = analytics.get_mistake_rates(user.id, rolling_window)
    
    return {
        "username": username,
        "rolling_window": rolling_window,
        "data": results
    }

@router.get("/users/{username}/analytics/blunder-rates")
async def get_blunder_rates(
    username: str,
    rolling_window: int = 20,
    db: Session = Depends(get_db)
):
    """Get blunder rates as percentages over rolling window of games"""
    
    user = db.query(User).filter(User.lichess_username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    analytics = AnalyticsService(db)
    results = analytics.get_blunder_rates(user.id, rolling_window)
    
    return {
        "username": username,
        "rolling_window": rolling_window,
        "data": results
    }

@router.get("/users/{username}/analytics/blunder-moves")
async def get_blunder_move_distribution(
    username: str,
    db: Session = Depends(get_db)
):
    """Get distribution of moves where blunders occur"""
    
    user = db.query(User).filter(User.lichess_username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    analytics = AnalyticsService(db)
    results = analytics.get_blunder_move_distribution(user.id)
    
    return {
        "username": username,
        "data": results
    }

@router.get("/users/{username}/analytics/openings")
async def get_opening_analysis(
    username: str,
    db: Session = Depends(get_db)
):
    """Get mistakes/blunders analysis by opening"""
    
    user = db.query(User).filter(User.lichess_username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    analytics = AnalyticsService(db)
    results = analytics.get_opening_analysis(user.id)
    
    return {
        "username": username,
        "data": results
    }

@router.get("/users/{username}/analytics/performance-trends")
async def get_performance_trends(
    username: str,
    rolling_window: int = 20,
    db: Session = Depends(get_db)
):
    """Get overall performance trends with rating correlation"""
    
    user = db.query(User).filter(User.lichess_username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    analytics = AnalyticsService(db)
    results = analytics.get_performance_trends(user.id, rolling_window)
    
    return {
        "username": username,
        "rolling_window": rolling_window,
        "data": results
    }

@router.get("/users/{username}/status")
async def get_analysis_status(
    username: str,
    db: Session = Depends(get_db)
):
    """Get analysis status for a user"""
    
    user = db.query(User).filter(User.lichess_username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    total_games = db.query(Game).filter(Game.user_id == user.id).count()
    analyzed_games = db.query(Game).filter(Game.user_id == user.id, Game.analyzed == True).count()
    
    return {
        "username": username,
        "total_games": total_games,
        "analyzed_games": analyzed_games,
        "last_analyzed": user.last_analyzed,
        "analysis_complete": total_games == analyzed_games if total_games > 0 else False
    }

@router.get("/users/{username}/analytics/user-stats")
async def get_user_stats(
    username: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive user statistics"""
    
    user = db.query(User).filter(User.lichess_username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get total games
    total_games = db.query(Game).filter(Game.user_id == user.id).count()
    analyzed_games = db.query(Game).filter(Game.user_id == user.id, Game.analyzed == True).count()
    
    # Get total moves, mistakes, and blunders for user
    user_moves = db.query(Move).join(Game).filter(
        Game.user_id == user.id,
        Move.is_user_move == True,
        Game.analyzed == True
    ).all()
    
    total_moves = len(user_moves)
    total_mistakes = sum(1 for move in user_moves if move.is_mistake)
    total_blunders = sum(1 for move in user_moves if move.is_blunder)
    
    return {
        "username": username,
        "total_games": total_games,
        "analyzed_games": analyzed_games,
        "total_moves": total_moves,
        "total_mistakes": total_mistakes,
        "total_blunders": total_blunders,
        "mistake_rate": total_mistakes / max(total_moves, 1),
        "blunder_rate": total_blunders / max(total_moves, 1),
        "last_analyzed": user.last_analyzed,
        "analysis_complete": total_games == analyzed_games if total_games > 0 else False
    }
