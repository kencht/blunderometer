import os
from pathlib import Path

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chess_analysis.db")

# Lichess API
LICHESS_API_BASE = "https://lichess.org/api"
LICHESS_RATE_LIMIT = 1  # seconds between requests
LICHESS_API_TOKEN = os.getenv("LICHESS_API_TOKEN")

# Stockfish Configuration
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/opt/homebrew/bin/stockfish")  # Default macOS Homebrew path
STOCKFISH_DEPTH = int(os.getenv("STOCKFISH_DEPTH", "8"))  # Reduced further for faster analysis
STOCKFISH_TIME_LIMIT = float(os.getenv("STOCKFISH_TIME_LIMIT", "0.2"))  # Much faster per-move analysis

# Analysis thresholds (in centipawns)
MISTAKE_THRESHOLD = 100  # 1 pawn
BLUNDER_THRESHOLD = 300  # 3 pawns

# Rolling average settings
DEFAULT_ROLLING_WINDOW = 20  # games
DEFAULT_MOVES_WINDOW = 10   # moves for mistakes per X moves calculation

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
