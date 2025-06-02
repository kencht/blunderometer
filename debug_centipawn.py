#!/usr/bin/env python3

import asyncio
import chess
import chess.pgn
import chess.engine
import io
from database import get_db, Game

async def debug_centipawn_calculation():
    """Debug a single move to see what's happening with centipawn calculation"""
    
    # Get a game to test
    db = get_db()
    game = db.query(Game).first()
    
    print(f"Debugging game: {game.lichess_id}")
    print(f"User color: {game.user_color}")
    
    # Parse PGN
    pgn_io = io.StringIO(game.pgn)
    parsed_game = chess.pgn.read_game(pgn_io)
    
    if not parsed_game:
        print("Failed to parse game")
        return
    
    # Start engine
    transport, engine = await chess.engine.popen_uci("/opt/homebrew/bin/stockfish")
    
    try:
        board = parsed_game.board()
        move_number = 1
        
        for move in parsed_game.mainline_moves():
            # Only analyze first user move for debugging
            is_user_move = (board.turn == chess.WHITE and game.user_color == 'white') or \
                          (board.turn == chess.BLACK and game.user_color == 'black')
            
            if is_user_move:
                print(f"\n=== ANALYZING MOVE {move_number} ===")
                
                # Get move in SAN notation BEFORE making the move
                move_san = board.san(move)
                print(f"Move: {move_san}")
                print(f"Board before move: {board.fen()}")
                
                # Get position before move
                print("Analyzing position before move...")
                eval_before = await engine.analyse(board, chess.engine.Limit(depth=15))
                print(f"Evaluation before: {eval_before}")
                
                # Make the move
                board.push(move)
                print(f"Board after move: {board.fen()}")
                
                # Get position after move
                print("Analyzing position after move...")
                eval_after = await engine.analyse(board, chess.engine.Limit(depth=15))
                print(f"Evaluation after: {eval_after}")
                
                # Calculate centipawn loss manually
                print("\n=== CENTIPAWN CALCULATION ===")
                score_before = eval_before.get('score')
                score_after = eval_after.get('score')
                print(f"Score before: {score_before}")
                print(f"Score after: {score_after}")
                
                if score_before and score_after:
                    # Convert to centipawns - handle PovScore objects
                    # Get scores from white's perspective
                    white_score_before = score_before.pov(chess.WHITE)
                    white_score_after = score_after.pov(chess.WHITE)
                    
                    if white_score_before.is_mate():
                        cp_before = 10000 if white_score_before.mate() > 0 else -10000
                    else:
                        cp_before = white_score_before.score()
                        
                    if white_score_after.is_mate():
                        cp_after = 10000 if white_score_after.mate() > 0 else -10000
                    else:
                        cp_after = white_score_after.score()
                    
                    print(f"White perspective - Before: {cp_before}, After: {cp_after}")
                    
                    # Convert to user perspective
                    if game.user_color == 'white':
                        user_cp_before = cp_before
                        user_cp_after = cp_after
                    else:
                        user_cp_before = -cp_before
                        user_cp_after = -cp_after
                    
                    print(f"User perspective - Before: {user_cp_before}, After: {user_cp_after}")
                    
                    # Calculate loss
                    centipawn_loss = max(0, user_cp_before - user_cp_after)
                    print(f"Centipawn loss: {centipawn_loss}")
                
                break  # Only analyze first user move
            else:
                board.push(move)
            
            move_number += 1
    
    finally:
        await engine.quit()
    
    db.close()

if __name__ == "__main__":
    asyncio.run(debug_centipawn_calculation())
