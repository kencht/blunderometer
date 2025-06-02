#!/usr/bin/env python3

import asyncio
from database import get_db, Game
from game_analyzer import GameAnalyzer

async def test_single_game_analysis():
    """Test analyzing a single game to debug the issue"""
    
    db = get_db()
    game = db.query(Game).first()
    
    print(f"Testing game analysis for {game.lichess_id}")
    print(f"User color: {game.user_color}")
    print(f"PGN length: {len(game.pgn)}")
    
    analyzer = GameAnalyzer()
    
    try:
        success, move_evaluations = await analyzer.analyze_game_with_time_limit(
            game.pgn, game.user_color, time_limit_seconds=60  # Short time limit for testing
        )
        
        print(f"Analysis result: success={success}")
        print(f"Move evaluations: {len(move_evaluations)}")
        
        if move_evaluations:
            print("First move evaluation:", move_evaluations[0])
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    db.close()

if __name__ == "__main__":
    asyncio.run(test_single_game_analysis())
