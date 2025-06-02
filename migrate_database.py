#!/usr/bin/env python3

"""
Database migration script to add blunder classification columns to the moves table
"""

import sqlite3
from database import get_db, Move

def migrate_database():
    """Add blunder classification columns to the moves table"""
    
    # Connect directly to SQLite
    conn = sqlite3.connect('chess_blunders.db')
    cursor = conn.cursor()
    
    print("Adding blunder classification columns...")
    
    try:
        # Add the new columns
        cursor.execute("ALTER TABLE moves ADD COLUMN is_blunder BOOLEAN DEFAULT 0")
        cursor.execute("ALTER TABLE moves ADD COLUMN is_mistake BOOLEAN DEFAULT 0") 
        cursor.execute("ALTER TABLE moves ADD COLUMN is_inaccuracy BOOLEAN DEFAULT 0")
        
        conn.commit()
        print("✓ Successfully added columns")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ Columns already exist")
        else:
            print(f"✗ Error adding columns: {e}")
            return False
    
    conn.close()
    
    # Now update existing data using SQLAlchemy
    print("Updating existing move classifications...")
    
    db = get_db()
    moves = db.query(Move).all()
    
    updated_count = 0
    for move in moves:
        if move.centipawn_loss is not None:
            # Update classification flags based on centipawn loss
            move.is_blunder = (move.centipawn_loss >= 300)
            move.is_mistake = (move.centipawn_loss >= 100)
            move.is_inaccuracy = (move.centipawn_loss >= 50)
            updated_count += 1
    
    db.commit()
    db.close()
    
    print(f"✓ Updated {updated_count} moves with blunder classifications")
    return True

def check_migration_status():
    """Check the current status of moves and blunders"""
    
    db = get_db()
    
    total_moves = db.query(Move).count()
    blunders = db.query(Move).filter(Move.is_blunder == True).count()
    mistakes = db.query(Move).filter(Move.is_mistake == True).count()
    inaccuracies = db.query(Move).filter(Move.is_inaccuracy == True).count()
    
    print(f"\nMigration Results:")
    print(f"Total moves: {total_moves}")
    print(f"Blunders (≥300 cp): {blunders}")
    print(f"Mistakes (≥100 cp): {mistakes}")
    print(f"Inaccuracies (≥50 cp): {inaccuracies}")
    
    # Show some examples
    print(f"\nSample blunders:")
    sample_blunders = db.query(Move).filter(Move.is_blunder == True).limit(5).all()
    for move in sample_blunders:
        print(f"  {move.move_san}: {move.centipawn_loss} cp loss")
    
    db.close()

if __name__ == "__main__":
    if migrate_database():
        check_migration_status()
