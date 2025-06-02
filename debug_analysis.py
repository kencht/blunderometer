#!/usr/bin/env python3

import asyncio
from database import get_db, Game
from game_analyzer import GameAnalyzer

async def debug_analysis():
    """Debug the analysis to see what's happening with centipawn calculations"""
    
    db = get_db()
    game = db.query(Game).first()
    
    print(f"Debugging analysis for game {game.lichess_id}")
    print(f"User color: {game.user_color}")
    
    analyzer = GameAnalyzer()
    
    try:
        success, move_evaluations = await analyzer.analyze_game_with_time_limit(
            game.pgn, game.user_color, time_limit_seconds=60
        )
        
        print(f"Analysis success: {success}")
        print(f"Number of move evaluations: {len(move_evaluations)}")
        
        if move_evaluations:
            print("\nFirst 5 move evaluations:")
            for i, move_eval in enumerate(move_evaluations[:5]):
                print(f"{i+1}. {move_eval}")
                
            # Check if any have None values
            none_count = sum(1 for m in move_evaluations if m.get('centipawn_loss') is None)
            print(f"\nMoves with None centipawn_loss: {none_count}")
            
            # Check for specific values
            values = [m.get('centipawn_loss') for m in move_evaluations]
            unique_values = set(values)
            print(f"Unique centipawn loss values: {unique_values}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    db.close()

if __name__ == "__main__":
    asyncio.run(debug_analysis())
