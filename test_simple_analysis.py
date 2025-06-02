#!/usr/bin/env python3

import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append('backend')

from database import get_db
from models import User, Game, Move
from lichess_client import LichessClient
from chess_analyzer import ChessAnalyzer

async def test_single_game_analysis():
    """Test the analysis of a single game that's already in the database"""
    
    db = next(get_db())
    
    try:
        # Get the unanalyzed game
        game = db.query(Game).filter(Game.lichess_id == 'Yn8YVgkT').first()
        if not game:
            print("Game not found!")
            return
            
        print(f"Found game: {game.lichess_id}")
        print(f"Game analyzed: {game.analyzed}")
        
        # Get game data from Lichess
        async with LichessClient() as lichess:
            games_data = await lichess.get_user_games("kencht", 5, None, ["blitz", "rapid", "classical"])
            
            # Find our specific game
            game_data = None
            for gd in games_data:
                if gd['id'] == 'Yn8YVgkT':
                    game_data = gd
                    break
                    
            if not game_data:
                print("Game data not found from Lichess!")
                return
                
            print(f"Got game data from Lichess")
            
            # Parse moves from PGN
            pgn_moves = lichess.parse_pgn_moves(game_data.get('pgn', ''))
            print(f"Parsed {len(pgn_moves)} moves from PGN")
            
            if len(pgn_moves) == 0:
                print("No moves found in PGN!")
                return
            
            print(f"First few moves: {pgn_moves[:3]}")
            
            # Analyze moves
            print("Starting analysis...")
            analyzer = ChessAnalyzer()
            analyzed_moves = await analyzer.analyze_game(pgn_moves)
            print(f"Analysis completed! Analyzed {len(analyzed_moves)} moves")
            
            if analyzed_moves:
                print(f"First analyzed move: {analyzed_moves[0]}")
                
                # Check for mistakes and blunders
                mistakes = [m for m in analyzed_moves if m['is_mistake']]
                blunders = [m for m in analyzed_moves if m['is_blunder']]
                print(f"Found {len(mistakes)} mistakes and {len(blunders)} blunders")
                
                # Show a few examples
                if blunders:
                    print(f"Example blunder: {blunders[0]}")
                if mistakes:
                    print(f"Example mistake: {mistakes[0]}")
                
                print("✓ Analysis successful!")
            else:
                print("❌ No moves were analyzed")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_single_game_analysis())
