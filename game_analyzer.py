import chess
import chess.pgn
import chess.engine
import asyncio
from datetime import datetime, timedelta
import io
import time
import os
import shutil

class GameAnalyzer:
    def __init__(self, engine_path=None):
        """Initialize GameAnalyzer with automatic Stockfish detection"""
        if engine_path:
            self.engine_path = engine_path
        else:
            self.engine_path = self._find_stockfish_engine()
    
    def _find_stockfish_engine(self):
        """Automatically find Stockfish engine path across different environments"""
        # Check environment variable first
        env_path = os.getenv('STOCKFISH_PATH')
        if env_path and os.path.isfile(env_path):
            print(f"[INFO] Using Stockfish from STOCKFISH_PATH: {env_path}")
            return env_path
        
        # Common Stockfish locations to check
        possible_paths = [
            # Cloud/Linux environments (most common)
            "/usr/bin/stockfish",
            "/usr/local/bin/stockfish", 
            "stockfish",  # If in PATH
            # macOS Homebrew
            "/opt/homebrew/bin/stockfish",
            "/usr/local/bin/stockfish",
            # Windows
            "stockfish.exe",
            # Alternative names
            "/usr/games/stockfish",
            "/app/stockfish"  # Some cloud platforms
        ]
        
        # First, try to find it in PATH
        stockfish_in_path = shutil.which("stockfish")
        if stockfish_in_path:
            print(f"[INFO] Found Stockfish in PATH: {stockfish_in_path}")
            return stockfish_in_path
        
        # Then check each possible path
        for path in possible_paths:
            if os.path.isfile(path):
                print(f"[INFO] Found Stockfish at: {path}")
                return path
        
        # If not found, raise an informative error
        raise FileNotFoundError(
            "Stockfish engine not found. Please install Stockfish:\n"
            "- Ubuntu/Debian: sudo apt-get install stockfish\n"
            "- macOS: brew install stockfish\n"
            "- Windows: Download from https://stockfishchess.org/download/\n"
            "- Or set STOCKFISH_PATH environment variable to the engine location\n"
            "- Cloud platforms: Ensure stockfish package is installed in build script"
        )
        
    async def analyze_game_with_time_limit(self, pgn_text, user_color, time_limit_seconds=300):
        """Analyze a game with a time limit. Returns (success, move_evaluations)"""
        start_time = time.time()
        
        try:
            # Parse PGN
            pgn_io = io.StringIO(pgn_text)
            game = chess.pgn.read_game(pgn_io)
            
            if not game:
                return False, []
            
            # Start engine
            transport, engine = await chess.engine.popen_uci(self.engine_path)
            
            move_evaluations = []
            board = game.board()
            move_number = 1
            
            try:
                for move in game.mainline_moves():
                    # Check time limit
                    if time.time() - start_time > time_limit_seconds:
                        print(f"Time limit reached at move {move_number}")
                        return False, move_evaluations
                    
                    # Only analyze user moves
                    is_user_move = (board.turn == chess.WHITE and user_color == 'white') or \
                                  (board.turn == chess.BLACK and user_color == 'black')
                    
                    if is_user_move:
                        # Get move in SAN notation BEFORE making the move
                        move_san = board.san(move)
                        
                        # Get position before move
                        eval_before = await engine.analyse(board, chess.engine.Limit(depth=15))
                        
                        # Make the move
                        board.push(move)
                        
                        # Get position after move
                        eval_after = await engine.analyse(board, chess.engine.Limit(depth=15))
                        
                        # Calculate centipawn loss
                        centipawn_loss = self.calculate_centipawn_loss(
                            eval_before.get('score'), eval_after.get('score'), user_color
                        )
                        
                        move_evaluations.append({
                            'move_number': move_number,
                            'move_san': move_san,
                            'centipawn_loss': centipawn_loss
                        })
                    else:
                        # Just make the move without analysis
                        board.push(move)
                    
                    move_number += 1
                
                return True, move_evaluations
                
            finally:
                await engine.quit()
                
        except Exception as e:
            print(f"Error analyzing game: {e}")
            return False, []
    
    def calculate_centipawn_loss(self, score_before, score_after, user_color):
        """Calculate centipawn loss for a move"""
        try:
            # Convert scores to centipawns from user's perspective
            cp_before = self.score_to_centipawns(score_before, user_color)
            cp_after = self.score_to_centipawns(score_after, user_color)
            
            # Centipawn loss is the difference (positive means loss)
            return max(0, cp_before - cp_after)
            
        except:
            return None
    
    def score_to_centipawns(self, score, user_color):
        """Convert chess.engine.Score to centipawns from user's perspective"""
        if not score:
            return 0
            
        # Handle PovScore objects (Stockfish returns these)
        if hasattr(score, 'pov'):
            # Get the actual score from white's perspective
            white_score = score.pov(chess.WHITE)
        else:
            white_score = score
            
        # Get score from white's perspective
        if white_score.is_mate():
            # Mate scores: positive = white winning, negative = black winning
            white_cp = 10000 if white_score.mate() > 0 else -10000
        else:
            # PovScore uses .score() but regular Score might use different method
            if hasattr(white_score, 'score'):
                white_cp = white_score.score()
            elif hasattr(white_score, 'cp'):
                white_cp = white_score.cp
            else:
                return 0
            
        # Convert to user's perspective
        if user_color == 'white':
            return white_cp
        else:
            return -white_cp
