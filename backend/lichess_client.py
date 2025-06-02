import httpx
import asyncio
import chess.pgn
import io
from datetime import datetime
from typing import List, Dict, Optional
import os
import sys
from pathlib import Path

# Add backend directory to path for proper imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from config import LICHESS_API_BASE, LICHESS_RATE_LIMIT
except ImportError:
    # Fallback values if config import fails
    LICHESS_API_BASE = "https://lichess.org/api"
    LICHESS_RATE_LIMIT = 1

LICHESS_API_TOKEN = os.getenv("LICHESS_API_TOKEN")

class LichessClient:
    def __init__(self):
        self.base_url = LICHESS_API_BASE
        self.session = None
        self.api_token = LICHESS_API_TOKEN
    
    async def __aenter__(self):
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        self.session = httpx.AsyncClient(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def get_user_games(
        self, 
        username: str, 
        max_games: int = 50,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        game_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """Fetch user games from Lichess API"""
        if game_types is None:
            game_types = ["blitz", "rapid", "classical"]
        
        params = {
            "max": max_games,
            "rated": "true",
            "perfType": ",".join(game_types),
            "clocks": "true",
            "evals": "false",  # We'll do our own analysis
            "opening": "true"
        }
        
        if since:
            params["since"] = int(since.timestamp() * 1000)
        
        if until:
            params["until"] = int(until.timestamp() * 1000)
        
        url = f"{self.base_url}/games/user/{username}"
        
        # Set proper headers for NDJSON response
        headers = {
            "Accept": "application/x-ndjson"
        }
        
        # Use a public client for user games (public data)
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
        
            games = []
            content = response.text
            
            # Parse NDJSON (newline-delimited JSON)
            for line in content.strip().split('\n'):
                if line.strip():
                    import json
                    try:
                        game_data = json.loads(line)
                        # If PGN is missing, fetch it
                        if not game_data.get('pgn'):
                            try:
                                game_data['pgn'] = await self.get_game_pgn(game_data['id'])
                            except Exception as e:
                                print(f"Could not fetch PGN for game {game_data['id']}: {e}")
                        games.append(game_data)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing game data: {e}")
                        continue
        
        await asyncio.sleep(LICHESS_RATE_LIMIT)
        return games
    
    async def get_user_info(self, username: str) -> Dict:
        """Get user information from Lichess"""
        # User info is public and doesn't require authentication
        url = f"{self.base_url}/user/{username}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
        
        await asyncio.sleep(LICHESS_RATE_LIMIT)
        return response.json()
    
    async def get_game_pgn(self, game_id: str) -> str:
        """Fetch the PGN for a single game from Lichess"""
        if not self.session:
            raise RuntimeError("LichessClient session is not initialized")
        # Note: Game export endpoint doesn't use /api prefix unlike other endpoints
        url = f"https://lichess.org/game/export/{game_id}"
        headers = {"Accept": "application/x-chess-pgn"}
        
        # First try without authentication for public games
        try:
            async with httpx.AsyncClient() as public_client:
                response = await public_client.get(url, headers=headers)
                response.raise_for_status()
                await asyncio.sleep(LICHESS_RATE_LIMIT)
                return response.text
        except httpx.HTTPStatusError as e:
            # If we get 401/403 and have an API token, try with authentication
            if e.response.status_code in [401, 403] and self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
                async with httpx.AsyncClient() as auth_client:
                    response = await auth_client.get(url, headers=headers)
                    response.raise_for_status()
                    await asyncio.sleep(LICHESS_RATE_LIMIT)
                    return response.text
            else:
                # Re-raise the original error if we can't handle it
                raise
    
    def parse_pgn_moves(self, pgn_string: str) -> List[str]:
        """Parse PGN and extract moves"""
        pgn_io = io.StringIO(pgn_string)
        game = chess.pgn.read_game(pgn_io)
        
        if not game:
            return []
        
        moves = []
        board = game.board()
        
        for move in game.mainline_moves():
            san_move = board.san(move)
            moves.append({
                'san': san_move,
                'uci': move.uci(),
                'fen_before': board.fen(),
            })
            board.push(move)
        
        return moves

    def parse_game_data(self, game_json, username):
        """Parse Lichess game JSON into our format for compatibility with main.py"""
        # Determine user color
        white_player = game_json['players']['white']['user']['name']
        user_color = 'white' if white_player.lower() == username.lower() else 'black'
        
        # Get ratings
        white_rating = game_json['players']['white'].get('rating')
        black_rating = game_json['players']['black'].get('rating')
        user_rating = white_rating if user_color == 'white' else black_rating
        opponent_rating = black_rating if user_color == 'white' else white_rating
        
        # Get time control
        clock = game_json.get('clock', {})
        time_control = f"{clock.get('initial', 0)}+{clock.get('increment', 0)}" if clock else 'correspondence'
        
        return {
            'lichess_id': game_json['id'],
            'username': username,
            'played_at': datetime.fromtimestamp(game_json['createdAt'] / 1000),
            'time_control': time_control,
            'variant': game_json.get('variant', 'standard'),
            'opening_name': game_json.get('opening', {}).get('name'),
            'opening_eco': game_json.get('opening', {}).get('eco'),
            'user_color': user_color,
            'user_rating': user_rating,
            'opponent_rating': opponent_rating,
            'result': game_json.get('status'),
            'pgn': game_json.get('pgn', '')
        }
