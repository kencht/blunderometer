"""
Multi-user database management for Chess Blunder Tracker
Each user gets their own SQLite database file
"""

import os
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    lichess_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    played_at = Column(DateTime, nullable=False)
    time_control = Column(String)
    variant = Column(String)
    opening_name = Column(String)
    opening_eco = Column(String)
    user_color = Column(String)  # 'white' or 'black'
    user_rating = Column(Integer)
    opponent_rating = Column(Integer)
    result = Column(String)
    pgn = Column(String)
    fully_analyzed = Column(Boolean, default=False)
    analysis_started_at = Column(DateTime)
    analysis_completed_at = Column(DateTime)

class Move(Base):
    __tablename__ = 'moves'
    
    id = Column(Integer, primary_key=True)
    game_lichess_id = Column(String, nullable=False)  # Reference to game
    move_number = Column(Integer, nullable=False)
    played_at = Column(DateTime, nullable=False)  # From game
    move_san = Column(String, nullable=False)
    centipawn_loss = Column(Integer)  # For user moves only
    opponent_rating = Column(Integer)  # From game
    opening_name = Column(String)  # From game
    time_control = Column(String)  # From game
    user_color = Column(String)  # From game
    is_blunder = Column(Boolean, default=False)  # Centipawn loss >= 300
    is_mistake = Column(Boolean, default=False)  # Centipawn loss >= 100
    is_inaccuracy = Column(Boolean, default=False)  # Centipawn loss >= 50

class DatabaseManager:
    """Manages databases for multiple users"""
    
    def __init__(self, data_dir: Optional[str] = None):
        # Use cloud-appropriate data directory
        if data_dir is None:
            # For cloud deployment, use /tmp for ephemeral storage
            # For local development, use 'data' folder
            if os.getenv('RENDER') or os.getenv('PORT'):  # Cloud environment
                data_dir = "/tmp/chess_data"
            else:  # Local development
                data_dir = "data"
        
        self.data_dir = data_dir
        self.engines = {}
        self.sessions = {}
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
    
    def get_db_path(self, username: str) -> str:
        """Get the database file path for a specific user"""
        # Sanitize username for filename
        safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_')).lower()
        return os.path.join(self.data_dir, f"chess_blunders_{safe_username}.db")
    
    def get_engine(self, username: str):
        """Get or create database engine for a user"""
        if username not in self.engines:
            db_path = self.get_db_path(username)
            self.engines[username] = create_engine(f'sqlite:///{db_path}')
            
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
