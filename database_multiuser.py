"""
Multi-user database management for Chess Blunder Tracker
Supports both SQLite (local) and PostgreSQL (cloud deployment)
"""

import os
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
import urllib.parse

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    lichess_id = Column(String(255), nullable=False)  # Added length for PostgreSQL
    username = Column(String(255), nullable=False)   # Added length for PostgreSQL
    played_at = Column(DateTime, nullable=False)
    time_control = Column(String(50))                # Added length for PostgreSQL
    variant = Column(String(50))                     # Added length for PostgreSQL
    opening_name = Column(String(255))               # Added length for PostgreSQL
    opening_eco = Column(String(10))                 # Added length for PostgreSQL
    user_color = Column(String(10))                  # 'white' or 'black'
    user_rating = Column(Integer)
    opponent_rating = Column(Integer)
    result = Column(String(20))                      # Added length for PostgreSQL
    pgn = Column(String)                             # Text field for PostgreSQL
    fully_analyzed = Column(Boolean, default=False)
    analysis_started_at = Column(DateTime)
    analysis_completed_at = Column(DateTime)
    
    # Create composite unique constraint for PostgreSQL multi-user support
    __table_args__ = (
        sa.UniqueConstraint('lichess_id', 'username', name='uq_game_lichess_user'),
        sa.Index('idx_games_username', 'username'),
        sa.Index('idx_games_played_at', 'played_at'),
    )

class Move(Base):
    __tablename__ = 'moves'
    
    id = Column(Integer, primary_key=True)
    game_lichess_id = Column(String(255), nullable=False)  # Reference to game
    move_number = Column(Integer, nullable=False)
    played_at = Column(DateTime, nullable=False)  # From game
    move_san = Column(String(20), nullable=False)           # Added length for PostgreSQL
    centipawn_loss = Column(Integer)  # For user moves only
    opponent_rating = Column(Integer)  # From game
    opening_name = Column(String(255))  # From game               # Added length for PostgreSQL
    time_control = Column(String(50))  # From game               # Added length for PostgreSQL
    user_color = Column(String(10))  # From game                 # Added length for PostgreSQL
    is_blunder = Column(Boolean, default=False)  # Centipawn loss >= 300
    is_mistake = Column(Boolean, default=False)  # Centipawn loss >= 100
    is_inaccuracy = Column(Boolean, default=False)  # Centipawn loss >= 50
    
    # Create indexes for PostgreSQL performance
    __table_args__ = (
        sa.Index('idx_moves_game_lichess_id', 'game_lichess_id'),
        sa.Index('idx_moves_played_at', 'played_at'),
        sa.Index('idx_moves_blunder', 'is_blunder'),
    )

class DatabaseManager:
    """Manages databases for multiple users"""
    
    def __init__(self, data_dir: Optional[str] = None):
        # Determine if we're using PostgreSQL (cloud) or SQLite (local)
        self.use_postgres = bool(os.getenv('DATABASE_URL'))
        
        if self.use_postgres:
            # Cloud deployment with PostgreSQL
            self.database_url = os.getenv('DATABASE_URL')
            print(f"[INFO] Using PostgreSQL database")
        else:
            # Local development with SQLite
            if data_dir is None:
                data_dir = "data"
            self.data_dir = data_dir
            os.makedirs(data_dir, exist_ok=True)
            print(f"[INFO] Using SQLite databases in {data_dir}")
        
        self.engines = {}
        self.sessions = {}
    
    def get_connection_string(self, username: str) -> str:
        """Get the database connection string for a specific user"""
        if self.use_postgres:
            # PostgreSQL: Use single database with user-scoped tables
            return self.database_url or ""
        else:
            # SQLite: One file per user
            safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_')).lower()
            db_path = os.path.join(self.data_dir, f"chess_blunders_{safe_username}.db")
            return f'sqlite:///{db_path}'
    
    def get_db_path(self, username: str) -> str:
        """Get the database file path for a specific user (SQLite only)"""
        if self.use_postgres:
            return "PostgreSQL Database"
        
        # Sanitize username for filename
        safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_')).lower()
        return os.path.join(self.data_dir, f"chess_blunders_{safe_username}.db")
    
    def get_engine(self, username: str):
        """Get or create database engine for a user"""
        if username not in self.engines:
            connection_string = self.get_connection_string(username)
            self.engines[username] = create_engine(connection_string)
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engines[username])
        
        return self.engines[username]
    
    def get_session(self, username: str):
        """Get a database session for a specific user"""
        if username not in self.sessions:
            engine = self.get_engine(username)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.sessions[username] = SessionLocal
        
        return self.sessions[username]()
    
    def get_db(self, username: str):
        """Get a database session for a specific user (compatibility method)"""
        return self.get_session(username)
    
    def list_users(self) -> list[str]:
        """List all users with databases"""
        users = []
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.startswith("chess_blunders_") and filename.endswith(".db"):
                    # Extract username from filename
                    username = filename[15:-3]  # Remove "chess_blunders_" and ".db"
                    users.append(username)
        return sorted(users)
    
    def get_user_stats(self, username: str) -> dict:
        """Get basic stats for a user to check if they have data"""
        try:
            db = self.get_db(username)
            total_games = db.query(Game).count()
            total_moves = db.query(Move).count()
            db.close()
            return {
                'username': username,
                'games': total_games,
                'moves': total_moves,
                'has_data': total_games > 0
            }
        except Exception:
            return {
                'username': username,
                'games': 0,
                'moves': 0,
                'has_data': False
            }

# Global database manager instance
db_manager = DatabaseManager()

# Legacy compatibility functions
def get_db(username: Optional[str] = None):
    """Get a database session - requires username for new multi-user system"""
    if username is None:
        # Fallback to default database for backwards compatibility
        # This should be removed once all calls are updated
        username = "default"
    return db_manager.get_db(username)
