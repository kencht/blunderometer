import chess
import chess.engine
from typing import List, Dict, Optional, Tuple, Any
from config import STOCKFISH_PATH, STOCKFISH_DEPTH, STOCKFISH_TIME_LIMIT, MISTAKE_THRESHOLD, BLUNDER_THRESHOLD
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChessAnalyzer:
    def __init__(self):
        self.engine_path = STOCKFISH_PATH
        self.depth = STOCKFISH_DEPTH
        self.time_limit = STOCKFISH_TIME_LIMIT
        # Overall timeout for entire game analysis
        self.analysis_timeout = 20.0  # 20 seconds max per game
        # Individual operation timeout
        self.operation_timeout = 2.0  # 2 seconds max per engine operation
    
    async def analyze_game(self, moves: List[Dict], starting_fen: Optional[str] = None) -> List[Dict]:
        """Analyze a complete game and return move evaluations"""
        try:
            # Wrap entire analysis in timeout
            return await asyncio.wait_for(
                self._analyze_game_internal(moves, starting_fen),
                timeout=self.analysis_timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Game analysis timed out after {self.analysis_timeout} seconds")
            return []
        except Exception as e:
            logger.error(f"Error in game analysis: {e}")
            return []
    
    async def _analyze_game_internal(self, moves: List[Dict], starting_fen: Optional[str] = None) -> List[Dict]:
        """Internal game analysis with proper engine management"""
        board = chess.Board() if not starting_fen else chess.Board(starting_fen)
        analyzed_moves = []
        
        # Initialize engine
        transport = None
        engine = None
        try:
            logger.info(f"Starting analysis of {len(moves)} moves")
            transport, engine = await chess.engine.popen_uci(self.engine_path)
            
            # Get initial position evaluation
            prev_eval = await self._safe_get_position_evaluation(engine, board)
            
            for i, move_data in enumerate(moves):
                move_uci = move_data['uci']
                move_san = move_data['san']
                
                try:
                    move = chess.Move.from_uci(move_uci)
                    
                    # Get best move for current position (with timeout)
                    best_move_info = await self._safe_get_best_move(engine, board)
                    
                    # Make the move
                    board.push(move)
                    
                    # Get evaluation after the move (with timeout)
                    current_eval = await self._safe_get_position_evaluation(engine, board)
                    
                    # Calculate evaluation difference
                    eval_diff = self._calculate_eval_diff(prev_eval, current_eval, i % 2 == 1)
                    
                    # Classify the move
                    classification = self._classify_move(eval_diff)
                    
                    analyzed_move = {
                        'move_number': (i // 2) + 1,
                        'color': 'white' if i % 2 == 0 else 'black',
                        'move_san': move_san,
                        'move_uci': move_uci,
                        'evaluation_before': prev_eval,
                        'evaluation_after': current_eval,
                        'evaluation_diff': eval_diff,
                        'best_move_san': best_move_info['san'] if best_move_info else None,
                        'best_move_uci': best_move_info['uci'] if best_move_info else None,
                        'is_mistake': classification['mistake'],
                        'is_blunder': classification['blunder'],
                        'is_inaccuracy': classification['inaccuracy']
                    }
                    
                    analyzed_moves.append(analyzed_move)
                    prev_eval = current_eval
                    
                    # Log progress every 10 moves
                    if (i + 1) % 10 == 0:
                        logger.info(f"Analyzed {i + 1}/{len(moves)} moves")
                    
                except Exception as e:
                    logger.warning(f"Error analyzing move {move_san}: {e}")
                    continue
                    
        except FileNotFoundError:
            logger.error(f"Stockfish not found at {self.engine_path}. Please install Stockfish or update the path in config.py")
            return []
        except Exception as e:
            logger.error(f"Error initializing Stockfish engine: {e}")
            return []
        finally:
            # Clean up engine properly
            if engine:
                try:
                    await asyncio.wait_for(engine.quit(), timeout=5.0)
                except (asyncio.TimeoutError, Exception) as e:
                    logger.warning(f"Error closing engine: {e}")
                    try:
                        if transport:
                            transport.close()
                    except:
                        pass
        
        logger.info(f"Successfully analyzed {len(analyzed_moves)} moves")
        return analyzed_moves
    
    async def _safe_get_position_evaluation(self, engine, board: chess.Board) -> float:
        """Get position evaluation with timeout protection"""
        try:
            info = await asyncio.wait_for(
                engine.analyse(board, chess.engine.Limit(depth=self.depth, time=self.time_limit)),
                timeout=self.operation_timeout
            )
            
            score = info["score"].relative
            if score.is_mate():
                # Convert mate scores to large centipawn values
                mate_in = score.mate()
                return 10000 if mate_in > 0 else -10000
            else:
                return score.score() or 0
                
        except asyncio.TimeoutError:
            logger.warning("Position evaluation timed out")
            return 0
        except Exception as e:
            logger.warning(f"Error getting evaluation: {e}")
            return 0
    
    async def _safe_get_best_move(self, engine, board: chess.Board) -> Optional[Dict]:
        """Get the best move with timeout protection"""
        try:
            result = await asyncio.wait_for(
                engine.play(board, chess.engine.Limit(depth=self.depth, time=self.time_limit)),
                timeout=self.operation_timeout
            )
            
            if result.move:
                temp_board = board.copy()
                san_move = temp_board.san(result.move)
                
                return {
                    'uci': result.move.uci(),
                    'san': san_move
                }
        except asyncio.TimeoutError:
            logger.warning("Best move calculation timed out")
        except Exception as e:
            logger.warning(f"Error getting best move: {e}")
        
        return None
        """Get the best move for current position"""
        try:
            result = await engine.play(
                board, 
                chess.engine.Limit(depth=self.depth, time=self.time_limit)
            )
            
            if result.move:
                temp_board = board.copy()
                san_move = temp_board.san(result.move)
                
                return {
                    'uci': result.move.uci(),
                    'san': san_move
                }
        except Exception as e:
            print(f"Error getting best move: {e}")
        
        return None
    
    def _calculate_eval_diff(self, prev_eval: float, current_eval: float, is_white_to_move: bool) -> float:
        """Calculate evaluation difference (always positive for worse positions)"""
        if is_white_to_move:
            # After black's move, white to move
            return prev_eval - current_eval
        else:
            # After white's move, black to move
            return current_eval - prev_eval
    
    def _classify_move(self, eval_diff: float) -> Dict[str, bool]:
        """Classify move based on evaluation difference"""
        return {
            'blunder': eval_diff >= BLUNDER_THRESHOLD,
            'mistake': MISTAKE_THRESHOLD <= eval_diff < BLUNDER_THRESHOLD,
            'inaccuracy': 50 <= eval_diff < MISTAKE_THRESHOLD
        }
    
    def analyze_opening(self, moves: List[str]) -> Dict[str, Any]:
        """Analyze opening from move list"""
        board = chess.Board()
        opening_moves = []
        
        # Usually openings are considered the first 10-15 moves
        for i, move_san in enumerate(moves[:15]):
            try:
                move = board.parse_san(move_san)
                board.push(move)
                opening_moves.append(move_san)
            except:
                break
        
        # This is a simplified opening detection
        # In a real app, you'd use an opening database
        opening_name = " ".join(opening_moves[:6])  # First 3 moves for each side
        
        return {
            'name': opening_name,
            'eco': 'Unknown',  # Would need opening database for ECO codes
            'moves': opening_moves
        }
