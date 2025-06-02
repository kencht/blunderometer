import asyncio
from datetime import datetime, UTC
from database_multiuser import DatabaseManager, Game, Move
from backend.lichess_client import LichessClient
from game_analyzer import GameAnalyzer

class BlunderTracker:
    def __init__(self, progress_callback=None):
        self.analyzer = GameAnalyzer()
        self.db_manager = DatabaseManager()
        self.progress_callback = progress_callback
    
    async def fetch_user_games(self, username, max_games=100, game_types=None, fetch_older=False):
        """Step 1: Fetch user's games and store in database"""
        if game_types is None:
            game_types = ["blitz", "rapid", "classical"]
            
        print(f"Fetching games for {username} (types: {', '.join(game_types)})...")
        
        db = self.db_manager.get_db(username)
        
        since = None
        until = None
        
        if fetch_older:
            # Fetch games older than our oldest game
            oldest_game = db.query(Game).filter(Game.username == username).order_by(Game.played_at.asc()).first()
            until = oldest_game.played_at if oldest_game else None
            print(f"Fetching games older than {until}")
        else:
            # Fetch games newer than our newest game
            latest_game = db.query(Game).filter(Game.username == username).order_by(Game.played_at.desc()).first()
            since = latest_game.played_at if latest_game else None
            print(f"Fetching games newer than {since}")
        
        async with LichessClient() as client:
            games_json = await client.get_user_games(username, max_games, since, until, game_types)
            
            games_added = 0
            for game_json in games_json:
                # Check if game already exists
                existing = db.query(Game).filter(Game.lichess_id == game_json['id']).first()
                if existing:
                    continue
                
                # Parse and store game
                game_data = client.parse_game_data(game_json, username)
                game = Game(**game_data)
                db.add(game)
                games_added += 1
            
            db.commit()
            db.close()
            
        print(f"Added {games_added} new games")
        return games_added
    
    async def analyze_games(self, username, time_limit_per_game_seconds=300, total_time_limit_seconds=None):
        """Step 2: Analyze games with time limit per game, mark fully analyzed ones"""
        print(f"Starting game analysis with {time_limit_per_game_seconds}s per game...")
        if total_time_limit_seconds:
            print(f"Total session time limit: {total_time_limit_seconds}s")
        
        session_start_time = datetime.now(UTC)
        db = self.db_manager.get_db(username)
        
        # Get unanalyzed games, ordered by date
        unanalyzed_games = db.query(Game).filter(
            Game.username == username,
            Game.fully_analyzed == False
        ).order_by(Game.played_at.desc()).all()
        
        print(f"Found {len(unanalyzed_games)} unanalyzed games")
        
        games_analyzed = 0
        games_skipped = 0
        
        for i, game in enumerate(unanalyzed_games):
            # Check total session time limit if specified
            if total_time_limit_seconds:
                elapsed_seconds = (datetime.now(UTC) - session_start_time).total_seconds()
                if elapsed_seconds >= total_time_limit_seconds:
                    print(f"Total session time limit ({total_time_limit_seconds}s) reached. Stopping analysis.")
                    break
                    
                remaining_time = total_time_limit_seconds - elapsed_seconds
                print(f"Session time remaining: {remaining_time:.1f}s")
            
            # Update progress if callback provided
            if self.progress_callback:
                self.progress_callback({
                    'current': i,
                    'total': len(unanalyzed_games),
                    'current_game': game.lichess_id,
                    'games_analyzed': games_analyzed,
                    'games_skipped': games_skipped
                })
            
            print(f"Analyzing game {i+1}/{len(unanalyzed_games)}: {game.lichess_id} ({game.played_at})...")
            
            game.analysis_started_at = datetime.now(UTC)
            db.commit()
            
            # Analyze the game with per-game time limit
            success, move_evaluations = await self.analyzer.analyze_game_with_time_limit(
                game.pgn, game.user_color, time_limit_per_game_seconds
            )
            
            if success:
                # Store the move analysis data immediately
                for move_eval in move_evaluations:
                    centipawn_loss = move_eval.get('centipawn_loss', 0) or 0
                    
                    move_record = Move(
                        game_lichess_id=game.lichess_id,
                        move_number=move_eval['move_number'],
                        played_at=game.played_at,
                        move_san=move_eval['move_san'],
                        centipawn_loss=centipawn_loss,
                        opponent_rating=game.opponent_rating,
                        opening_name=game.opening_name,
                        time_control=game.time_control,
                        user_color=game.user_color,
                        is_blunder=(centipawn_loss >= 300),
                        is_mistake=(centipawn_loss >= 100),
                        is_inaccuracy=(centipawn_loss >= 50)
                    )
                    db.add(move_record)
                
                game.fully_analyzed = True
                game.analysis_completed_at = datetime.now(UTC)
                games_analyzed += 1
                print(f"✓ Game {game.lichess_id} fully analyzed ({len(move_evaluations)} moves)")
            else:
                games_skipped += 1
                print(f"✗ Game {game.lichess_id} analysis incomplete (time limit reached)")
            
            db.commit()
        
        print(f"Analysis session complete: {games_analyzed} games analyzed, {games_skipped} games skipped")
        db.close()
        return {"games_analyzed": games_analyzed, "games_skipped": games_skipped}
    
    def process_analyzed_games(self, username):
        """Step 3: Report on fully analyzed games and moves"""
        print("Checking processed moves from analyzed games...")
        
        db = self.db_manager.get_db(username)
        
        # Get fully analyzed games
        analyzed_games = db.query(Game).filter(
            Game.username == username,
            Game.fully_analyzed == True
        ).order_by(Game.played_at.desc()).all()
        
        total_moves = db.query(Move).count()
        blunders = db.query(Move).filter(Move.is_blunder == True).count()
        mistakes = db.query(Move).filter(Move.is_mistake == True).count()
        inaccuracies = db.query(Move).filter(Move.is_inaccuracy == True).count()
        
        print(f"✓ {len(analyzed_games)} games fully analyzed")
        print(f"✓ {total_moves} moves processed")
        print(f"✓ {blunders} blunders (≥300 centipawns)")
        print(f"✓ {mistakes} mistakes (≥100 centipawns)")
        print(f"✓ {inaccuracies} inaccuracies (≥50 centipawns)")
        
        db.close()
        return total_moves

async def main():
    tracker = BlunderTracker()
    username = "kencht"  # Correct Lichess username
    
    # Step 1: Fetch games
    await tracker.fetch_user_games(username, max_games=20)
    
    # Step 2: Analyze games (with time limit per game)
    await tracker.analyze_games(username, time_limit_per_game_seconds=20)
    
    # Step 3: Process into moves database
    tracker.process_analyzed_games(username)
    
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
