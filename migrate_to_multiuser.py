#!/usr/bin/env python3
"""
Migration script to move data from single database to multi-user database structure
"""

import sqlite3
import os
from database_multiuser import DatabaseManager, Game, Move

def migrate_user_data(username: str):
    """Migrate a specific user's data from the old database to the new multi-user structure"""
    
    print(f"Migrating data for user: {username}")
    
    # Connect to old database
    old_db = sqlite3.connect('chess_blunders.db')
    old_db.row_factory = sqlite3.Row  # Enable column access by name
    old_cursor = old_db.cursor()
    
    # Initialize new database manager
    db_manager = DatabaseManager()
    new_db = db_manager.get_db(username)
    
    try:
        # Migrate games
        print("Migrating games...")
        old_cursor.execute("SELECT * FROM games WHERE username = ?", (username,))
        games_data = old_cursor.fetchall()
        
        games_migrated = 0
        for game_row in games_data:
            # Check if game already exists in new database
            existing = new_db.query(Game).filter(Game.lichess_id == game_row['lichess_id']).first()
            if existing:
                continue
                
            # Create new game record
            game = Game(
                lichess_id=game_row['lichess_id'],
                username=game_row['username'],
                played_at=game_row['played_at'],
                time_control=game_row['time_control'],
                variant=game_row['variant'],
                opening_name=game_row['opening_name'],
                opening_eco=game_row['opening_eco'],
                user_color=game_row['user_color'],
                user_rating=game_row['user_rating'],
                opponent_rating=game_row['opponent_rating'],
                result=game_row['result'],
                pgn=game_row['pgn'],
                fully_analyzed=bool(game_row['fully_analyzed']),
                analysis_started_at=game_row['analysis_started_at'],
                analysis_completed_at=game_row['analysis_completed_at']
            )
            new_db.add(game)
            games_migrated += 1
        
        new_db.commit()
        print(f"✓ Migrated {games_migrated} games")
        
        # Migrate moves
        print("Migrating moves...")
        old_cursor.execute("""
            SELECT m.* FROM moves m 
            JOIN games g ON m.game_lichess_id = g.lichess_id 
            WHERE g.username = ?
        """, (username,))
        moves_data = old_cursor.fetchall()
        
        moves_migrated = 0
        for move_row in moves_data:
            # Check if move already exists in new database
            existing = new_db.query(Move).filter(
                Move.game_lichess_id == move_row['game_lichess_id'],
                Move.move_number == move_row['move_number']
            ).first()
            if existing:
                continue
                
            # Create new move record
            move = Move(
                game_lichess_id=move_row['game_lichess_id'],
                move_number=move_row['move_number'],
                played_at=move_row['played_at'],
                move_san=move_row['move_san'],
                centipawn_loss=move_row['centipawn_loss'],
                opponent_rating=move_row['opponent_rating'],
                opening_name=move_row['opening_name'],
                time_control=move_row['time_control'],
                user_color=move_row['user_color'],
                is_blunder=bool(move_row['is_blunder']),
                is_mistake=bool(move_row['is_mistake']),
                is_inaccuracy=bool(move_row['is_inaccuracy'])
            )
            new_db.add(move)
            moves_migrated += 1
        
        new_db.commit()
        print(f"✓ Migrated {moves_migrated} moves")
        
        # Verify migration
        total_games = new_db.query(Game).count()
        analyzed_games = new_db.query(Game).filter(Game.fully_analyzed == True).count()
        total_moves = new_db.query(Move).count()
        blunders = new_db.query(Move).filter(Move.is_blunder == True).count()
        
        print(f"\nMigration Results for {username}:")
        print(f"Total games: {total_games}")
        print(f"Analyzed games: {analyzed_games}")
        print(f"Total moves: {total_moves}")
        print(f"Blunders: {blunders}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        new_db.rollback()
        return False
    finally:
        new_db.close()
        old_db.close()
    
    return True

if __name__ == "__main__":
    # Migrate kencht user data
    if migrate_user_data("kencht"):
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
