#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('backend')
from backend.database import get_db
from backend.models import Game, Move
from backend.chess_analyzer import ChessAnalyzer
from backend.lichess_client import LichessClient

async def test_analysis_for_failed_game():
    """Test analyzing one of the games that previously failed"""
    
    # Get database session
    db = next(get_db())
    
    # Get one of the failed games
    failed_game = db.query(Game).filter(Game.analyzed == False).first()
    if not failed_game:
        print("No unanalyzed games found")
        return
    
    print(f"Testing analysis for game {failed_game.lichess_id}")
    
    # Get the PGN for this game
    async with LichessClient() as lichess:
        try:
            pgn = await lichess.get_game_pgn(failed_game.lichess_id)
            print(f"Successfully fetched PGN for game {failed_game.lichess_id}")
            print(f"PGN length: {len(pgn)}")
            
            # Parse moves from PGN
            pgn_moves = lichess.parse_pgn_moves(pgn)
            print(f"Parsed {len(pgn_moves)} moves from PGN")
            
            if pgn_moves:
                print("First few moves:", pgn_moves[:5])
                
                # Analyze moves
                analyzer = ChessAnalyzer()
                analyzed_moves = await analyzer.analyze_game(pgn_moves)
                print(f"Analyzed {len(analyzed_moves)} moves")
                
                if analyzed_moves:
                    print("Analysis successful! First analyzed move:")
                    print(analyzed_moves[0])
                    
                    # Test saving one move
                    move_data = analyzed_moves[0]
                    move = Move(
                        game_id=failed_game.id,
                        move_number=move_data['move_number'],
                        color=move_data['color'],
                        move_san=move_data['move_san'],
                        move_uci=move_data['move_uci'],
                        evaluation_before=move_data['evaluation_before'],
                        evaluation_after=move_data['evaluation_after'],
                        evaluation_diff=move_data['evaluation_diff'],
                        best_move_san=move_data['best_move_san'],
                        best_move_uci=move_data['best_move_uci'],
                        is_user_move=(move_data['color'] == failed_game.user_color),
                        is_mistake=move_data['is_mistake'],
                        is_blunder=move_data['is_blunder'],
                        is_inaccuracy=move_data['is_inaccuracy']
                    )
                    db.add(move)
                    db.commit()
                    print("Successfully saved test move!")
                    
                    # Clean up the test move
                    db.delete(move)
                    db.commit()
                    print("Cleaned up test move")
                    
                else:
                    print("Analysis returned no moves - analyzer issue")
            else:
                print("PGN parsing returned no moves - parsing issue")
                
        except Exception as e:
            print(f"Error during analysis test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analysis_for_failed_game())
