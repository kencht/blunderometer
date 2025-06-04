#!/usr/bin/env python3
"""
Migration script to move data from SQLite to PostgreSQL
Run this when upgrading from SQLite (local) to PostgreSQL (cloud)
"""

import os
import sys
from sqlalchemy import create_engine, text
from database_multiuser import DatabaseManager, Game, Move, Base
import sqlite3
from datetime import datetime

def migrate_user_data(username: str, sqlite_db_path: str, postgres_url: str):
    """Migrate a single user's data from SQLite to PostgreSQL"""
    
    # Connect to SQLite source
    sqlite_engine = create_engine(f'sqlite:///{sqlite_db_path}')
    
    # Connect to PostgreSQL destination
    postgres_engine = create_engine(postgres_url)
    
    # Create tables in PostgreSQL if they don't exist
    Base.metadata.create_all(postgres_engine)
    
    print(f"[INFO] Migrating user '{username}' from {sqlite_db_path}")
    
    # Get data from SQLite
    with sqlite_engine.connect() as sqlite_conn:
        # Count records
        games_result = sqlite_conn.execute(text("SELECT COUNT(*) FROM games"))
        moves_result = sqlite_conn.execute(text("SELECT COUNT(*) FROM moves"))
        games_count = games_result.scalar()
        moves_count = moves_result.scalar()
        
        print(f"[INFO] Found {games_count} games and {moves_count} moves to migrate")
        
        # Get all games
        games_result = sqlite_conn.execute(text("SELECT * FROM games"))
        games_data = games_result.fetchall()
        
        # Get all moves
        moves_result = sqlite_conn.execute(text("SELECT * FROM moves"))
        moves_data = moves_result.fetchall()
    
    # Insert data into PostgreSQL
    with postgres_engine.connect() as postgres_conn:
        # Check if user data already exists
        existing_games_result = postgres_conn.execute(
            text("SELECT COUNT(*) FROM games WHERE username = :username"),
            {"username": username}
        )
        existing_games = existing_games_result.scalar() or 0
        
        if existing_games > 0:
            print(f"[WARNING] User '{username}' already has {existing_games} games in PostgreSQL")
            response = input("Continue and potentially create duplicates? (y/N): ")
            if response.lower() != 'y':
                print("[INFO] Skipping migration for this user")
                return
        
        # Insert games
        migrated_games = 0
        for game_row in games_data:
            try:
                # Convert SQLite row to dict
                game_dict = dict(game_row._mapping)
                
                # Ensure username is set
                game_dict['username'] = username
                
                # Insert game
                postgres_conn.execute(
                    text("""
                        INSERT INTO games (
                            lichess_id, username, played_at, time_control, variant,
                            opening_name, opening_eco, user_color, user_rating,
                            opponent_rating, result, pgn, fully_analyzed,
                            analysis_started_at, analysis_completed_at
                        ) VALUES (
                            :lichess_id, :username, :played_at, :time_control, :variant,
                            :opening_name, :opening_eco, :user_color, :user_rating,
                            :opponent_rating, :result, :pgn, :fully_analyzed,
                            :analysis_started_at, :analysis_completed_at
                        ) ON CONFLICT (lichess_id, username) DO NOTHING
                    """),
                    game_dict
                )
                migrated_games += 1
            except Exception as e:
                try:
                    lichess_id = dict(game_row._mapping).get('lichess_id', 'unknown')
                except:
                    lichess_id = 'unknown'
                print(f"[ERROR] Failed to migrate game {lichess_id}: {e}")
        
        # Insert moves
        migrated_moves = 0
        for move_row in moves_data:
            try:
                # Convert SQLite row to dict
                move_dict = dict(move_row._mapping)
                
                # Insert move
                postgres_conn.execute(
                    text("""
                        INSERT INTO moves (
                            game_lichess_id, move_number, played_at, move_san,
                            centipawn_loss, opponent_rating, opening_name,
                            time_control, user_color, is_blunder, is_mistake, is_inaccuracy
                        ) VALUES (
                            :game_lichess_id, :move_number, :played_at, :move_san,
                            :centipawn_loss, :opponent_rating, :opening_name,
                            :time_control, :user_color, :is_blunder, :is_mistake, :is_inaccuracy
                        )
                    """),
                    move_dict
                )
                migrated_moves += 1
            except Exception as e:
                print(f"[ERROR] Failed to migrate move: {e}")
        
        # Commit the transaction
        postgres_conn.commit()
        
        print(f"[SUCCESS] Migrated {migrated_games} games and {migrated_moves} moves for user '{username}'")

def main():
    """Main migration function"""
    print("=== SQLite to PostgreSQL Migration Tool ===")
    
    # Check if we have PostgreSQL URL
    postgres_url = os.getenv('DATABASE_URL')
    if not postgres_url:
        print("[ERROR] DATABASE_URL environment variable not set")
        print("Please set DATABASE_URL to your PostgreSQL connection string")
        return 1
    
    # Find SQLite databases in data directory
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"[ERROR] Data directory '{data_dir}' not found")
        return 1
    
    sqlite_files = [f for f in os.listdir(data_dir) if f.endswith('.db')]
    
    if not sqlite_files:
        print(f"[INFO] No SQLite database files found in '{data_dir}'")
        return 0
    
    print(f"[INFO] Found {len(sqlite_files)} SQLite database files:")
    for db_file in sqlite_files:
        print(f"  - {db_file}")
    
    # Extract usernames from database filenames
    users_to_migrate = []
    for db_file in sqlite_files:
        if db_file.startswith('chess_blunders_') and db_file.endswith('.db'):
            username = db_file[15:-3]  # Remove 'chess_blunders_' prefix and '.db' suffix
            users_to_migrate.append((username, os.path.join(data_dir, db_file)))
    
    if not users_to_migrate:
        print("[ERROR] No valid chess blunder database files found")
        return 1
    
    print(f"\n[INFO] Users to migrate:")
    for username, db_path in users_to_migrate:
        print(f"  - {username} ({db_path})")
    
    # Confirm migration
    response = input(f"\nProceed with migration of {len(users_to_migrate)} users? (y/N): ")
    if response.lower() != 'y':
        print("[INFO] Migration cancelled")
        return 0
    
    # Perform migration
    success_count = 0
    for username, db_path in users_to_migrate:
        try:
            migrate_user_data(username, db_path, postgres_url)
            success_count += 1
        except Exception as e:
            print(f"[ERROR] Migration failed for user '{username}': {e}")
    
    print(f"\n=== Migration Complete ===")
    print(f"Successfully migrated {success_count} out of {len(users_to_migrate)} users")
    
    if success_count == len(users_to_migrate):
        print("\n[INFO] All users migrated successfully!")
        print("[INFO] You can now:")
        print("  1. Set DATABASE_URL environment variable on Render.com")
        print("  2. Deploy your application")
        print("  3. Your data will persist across container restarts!")
        return 0
    else:
        print(f"\n[WARNING] {len(users_to_migrate) - success_count} users failed to migrate")
        return 1

if __name__ == "__main__":
    sys.exit(main())
