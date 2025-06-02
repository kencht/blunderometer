import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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

# Database setup
engine = create_engine('sqlite:///chess_blunders.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get a database session"""
    return SessionLocal()
