#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('backend')
from lichess_client import LichessClient
from chess_analyzer import ChessAnalyzer
from database import get_db
from models import User, Game, Move

async def debug_failed_game():
    """Debug why some games have no moves after analysis"""
    print("Starting debug...")
    
    # Get one of the failed games
    db = next(get_db())
    user = db.query(User).first()
    print(f"Found user: {user.lichess_username if user else 'None'}")
    
    # Get a game with 0 moves
    failed_game = db.query(Game).filter(
        Game.user_id == user.id,
        Game.analyzed == True
    ).all()
    
    for game in failed_game:
        move_count = db.query(Move).filter(Move.game_id == game.id).count()
        if move_count == 0:
            print(f"Debugging game {game.lichess_id} with 0 moves...")
            
            # Try to get the game data again
            async with LichessClient() as lichess:
                try:
                    games_data = await lichess.get_user_games(user.lichess_username, 10, None, ["blitz", "rapid", "classical"])
                    
                    # Find this specific game
                    game_data = None
                    for gd in games_data:
                        if gd['id'] == game.lichess_id:
                            game_data = gd
                            break
                    
                    if not game_data:
                        print(f"❌ Game {game.lichess_id} not found in recent games")
                        continue
                        
                    print(f"✓ Found game data")
                    
                    # Parse PGN
                    pgn_moves = lichess.parse_pgn_moves(game_data.get('pgn', ''))
                    print(f"✓ Parsed {len(pgn_moves)} moves from PGN")
                    
                    if len(pgn_moves) == 0:
                        print(f"❌ No moves in PGN!")
                        print(f"PGN content: {game_data.get('pgn', 'NO PGN')[:200]}...")
                        continue
                    
                    print(f"First few moves: {pgn_moves[:5]}")
                    
                    # Try analysis
                    print("Starting analysis...")
                    analyzer = ChessAnalyzer()
                    try:
                        analyzed_moves = await analyzer.analyze_game(pgn_moves)
                        print(f"✓ Analysis returned {len(analyzed_moves)} moves")
                        
                        if len(analyzed_moves) == 0:
                            print("❌ Analysis returned 0 moves - this is the problem!")
                        else:
                            print(f"First analyzed move: {analyzed_moves[0]}")
                            
                    except Exception as e:
                        print(f"❌ Analysis failed with error: {e}")
                        import traceback
                        traceback.print_exc()
                    
                except Exception as e:
                    print(f"❌ Error fetching game data: {e}")
                    import traceback
                    traceback.print_exc()
            
            break  # Only test one failed game
    
    db.close()

if __name__ == "__main__":
    asyncio.run(debug_failed_game())
