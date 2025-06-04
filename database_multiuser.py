"""
Multi-user database management for Chess Blunder Tracker
SQLite only - for local use
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
    lichess_id = Column(String, nullable=False, unique=True)
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
    """Manages SQLite databases for multiple users locally"""
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = "data"
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        print(f"[INFO] Using SQLite databases in {data_dir}")
        
        self.engines = {}
        self.sessions = {}
    
    def get_connection_string(self, username: str) -> str:
        """Get the SQLite database connection string for a specific user"""
        safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_')).lower()
        db_path = os.path.join(self.data_dir, f"chess_blunders_{safe_username}.db")
        return f'sqlite:///{db_path}'
    
    def get_db_path(self, username: str) -> str:
        """Get the physical database file path for a user"""
        safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_')).lower()
        return os.path.join(self.data_dir, f"chess_blunders_{safe_username}.db")
    
    def get_engine(self, username: str):
        """Get or create database engine for a user"""
        if username not in self.engines:
            connection_string = self.get_connection_string(username)
            self.engines[username] = create_engine(connection_string, echo=False)
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engines[username])
            
        return self.engines[username]
    
    def get_session(self, username: str):
        """Get or create database session for a user"""
        if username not in self.sessions:
            engine = self.get_engine(username)
            Session = sessionmaker(bind=engine)
            self.sessions[username] = Session()
            
        return self.sessions[username]
    
    def get_db(self, username: str):
        """Get database session for a user (alias for get_session for Flask app compatibility)"""
        return self.get_session(username)
    
    def close_session(self, username: str):
        """Close database session for a user"""
        if username in self.sessions:
            self.sessions[username].close()
            del self.sessions[username]
    
    def close_all_sessions(self):
        """Close all database sessions"""
        for username in list(self.sessions.keys()):
            self.close_session(username)
    
    def get_game_count(self, username: str) -> int:
        """Get total number of games for a user"""
        session = self.get_session(username)
        return session.query(Game).count()
    
    def get_move_count(self, username: str) -> int:
        """Get total number of moves for a user"""
        session = self.get_session(username)
        return session.query(Move).count()
    
    def get_blunder_count(self, username: str) -> int:
        """Get total number of blunders for a user"""
        session = self.get_session(username)
        return session.query(Move).filter(Move.is_blunder == True).count()
    
    def game_exists(self, username: str, lichess_id: str) -> bool:
        """Check if a game already exists for a user"""
        session = self.get_session(username)
        return session.query(Game).filter(Game.lichess_id == lichess_id).first() is not None
    
    def add_game(self, username: str, game_data: dict) -> Game:
        """Add a new game for a user"""
        session = self.get_session(username)
        
        game = Game(
            lichess_id=game_data['lichess_id'],
            username=username,
            played_at=game_data['played_at'],
            time_control=game_data.get('time_control'),
            variant=game_data.get('variant'),
            opening_name=game_data.get('opening_name'),
            opening_eco=game_data.get('opening_eco'),
            user_color=game_data.get('user_color'),
            user_rating=game_data.get('user_rating'),
            opponent_rating=game_data.get('opponent_rating'),
            result=game_data.get('result'),
            pgn=game_data.get('pgn')
        )
        
        session.add(game)
        session.commit()
        return game
    
    def update_game_analysis(self, username: str, lichess_id: str, analysis_data: dict):
        """Update game analysis status"""
        session = self.get_session(username)
        game = session.query(Game).filter(Game.lichess_id == lichess_id).first()
        
        if game:
            for key, value in analysis_data.items():
                setattr(game, key, value)
            session.commit()
    
    def add_moves(self, username: str, moves_data: list):
        """Add multiple moves for a user"""
        session = self.get_session(username)
        
        moves = []
        for move_data in moves_data:
            move = Move(**move_data)
            moves.append(move)
        
        session.add_all(moves)
        session.commit()
    
    def get_user_stats(self, username: str) -> dict:
        """Get comprehensive stats for a user"""
        session = self.get_session(username)
        
        total_games = session.query(Game).count()
        total_moves = session.query(Move).count()
        total_blunders = session.query(Move).filter(Move.is_blunder == True).count()
        total_mistakes = session.query(Move).filter(Move.is_mistake == True).count()
        total_inaccuracies = session.query(Move).filter(Move.is_inaccuracy == True).count()
        
        return {
            'total_games': total_games,
            'total_moves': total_moves,
            'total_blunders': total_blunders,
            'total_mistakes': total_mistakes,
            'total_inaccuracies': total_inaccuracies,
            'blunder_rate': (total_blunders / total_moves * 100) if total_moves > 0 else 0
        }
