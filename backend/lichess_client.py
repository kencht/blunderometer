import httpx
import asyncio
import chess.pgn
import io
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

# Configuration constants
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
        
        # Enhanced retry logic and timeout configuration for cloud deployment
        max_retries = 3
        games = []  # Initialize games list before retry loop
        
        for attempt in range(max_retries):
            # Increase timeout on retry attempts - more generous for cloud environments
            timeout_seconds = 45.0 + (attempt * 15.0)  # 45s, 60s, 75s
            connect_timeout = 15.0 + (attempt * 5.0)   # 15s, 20s, 25s
            read_timeout = 30.0 + (attempt * 10.0)     # 30s, 40s, 50s
            
            timeout = httpx.Timeout(timeout_seconds, connect=connect_timeout, read=read_timeout)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                try:
                    print(f"Fetching games for {username} (attempt {attempt + 1}/{max_retries})")
                    response = await client.get(url, params=params, headers=headers)
                    response.raise_for_status()
                    
                    # Success - parse the response
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
                    
                    break  # Success, exit retry loop
                    
                except httpx.TimeoutException as e:
                    print(f"Timeout error fetching games for {username} (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:  # Last attempt
                        raise Exception(f"Timeout connecting to Lichess API after {max_retries} attempts. This may be due to network issues on the cloud server. Please try again later.")
                    # Wait before retry
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    continue
                    
                except httpx.HTTPStatusError as e:
                    print(f"HTTP error fetching games for {username}: {e.response.status_code}")
                    if e.response.status_code == 429:
                        if attempt == max_retries - 1:
                            raise Exception("Rate limited by Lichess API. Please try again in a few minutes.")
                        # Wait longer for rate limiting
                        await asyncio.sleep(5 * (attempt + 1))  # 5s, 10s, 15s
                        continue
                    elif e.response.status_code == 404:
                        raise Exception(f"User '{username}' not found on Lichess.")
                    elif e.response.status_code >= 500:
                        # Server error - retry
                        if attempt == max_retries - 1:
                            raise Exception(f"Lichess server error: {e.response.status_code}. Please try again later.")
                        await asyncio.sleep(3 * (attempt + 1))  # 3s, 6s, 9s
                        continue
                    else:
                        raise Exception(f"Error fetching games: {e.response.status_code}")
                        
                except httpx.RequestError as e:
                    print(f"Request error fetching games for {username} (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:  # Last attempt
                        raise Exception("Network error connecting to Lichess API. This may be due to connectivity issues on the cloud server. Please try again later.")
                    # Wait before retry
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
        await asyncio.sleep(LICHESS_RATE_LIMIT)
        return games
    
    async def get_user_info(self, username: str) -> Dict:
        """Get user information from Lichess"""
        # User info is public and doesn't require authentication
        url = f"{self.base_url}/user/{username}"
        
        # Enhanced retry logic for user info with shorter timeouts
        max_retries = 2  # Fewer retries for user info since it's lighter
        
        for attempt in range(max_retries):
            timeout_seconds = 20.0 + (attempt * 10.0)  # 20s, 30s
            connect_timeout = 8.0 + (attempt * 2.0)    # 8s, 10s
            read_timeout = 12.0 + (attempt * 3.0)      # 12s, 15s
            
            timeout = httpx.Timeout(timeout_seconds, connect=connect_timeout, read=read_timeout)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                try:
                    print(f"Getting user info for {username} (attempt {attempt + 1}/{max_retries})")
                    response = await client.get(url)
                    response.raise_for_status()
                    
                    await asyncio.sleep(LICHESS_RATE_LIMIT)
                    return response.json()
                    
                except httpx.TimeoutException as e:
                    print(f"Timeout error getting user info for {username} (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        raise Exception(f"Timeout connecting to Lichess API for user info after {max_retries} attempts.")
                    await asyncio.sleep(1)  # Brief wait before retry
                    continue
                    
                except httpx.HTTPStatusError as e:
                    print(f"HTTP error getting user info for {username}: {e.response.status_code}")
                    if e.response.status_code == 404:
                        raise Exception(f"User '{username}' not found on Lichess.")
                    elif e.response.status_code >= 500 and attempt < max_retries - 1:
                        # Retry server errors
                        await asyncio.sleep(2)
                        continue
                    else:
                        raise Exception(f"Error getting user info: {e.response.status_code}")
                        
                except httpx.RequestError as e:
                    print(f"Request error getting user info for {username} (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        raise Exception("Network error connecting to Lichess API for user info.")
                    await asyncio.sleep(1)
                    continue
        
        # Should never reach here due to exceptions, but add fallback
        raise Exception("Failed to get user info after all retries")
    
    async def get_game_pgn(self, game_id: str) -> str:
        """Fetch the PGN for a single game from Lichess"""
        if not self.session:
            raise RuntimeError("LichessClient session is not initialized")
        # Note: Game export endpoint doesn't use /api prefix unlike other endpoints
        url = f"https://lichess.org/game/export/{game_id}"
        headers = {"Accept": "application/x-chess-pgn"}
        
        # Enhanced retry logic for PGN fetching
        max_retries = 2
        
        for attempt in range(max_retries):
            timeout_seconds = 25.0 + (attempt * 10.0)  # 25s, 35s
            timeout = httpx.Timeout(timeout_seconds, connect=8.0, read=17.0)
            
            # First try without authentication for public games
            try:
                async with httpx.AsyncClient(timeout=timeout) as public_client:
                    print(f"Fetching PGN for game {game_id} (attempt {attempt + 1}/{max_retries})")
                    response = await public_client.get(url, headers=headers)
                    response.raise_for_status()
                    await asyncio.sleep(LICHESS_RATE_LIMIT)
                    return response.text
                    
            except httpx.TimeoutException as e:
                print(f"Timeout fetching PGN for game {game_id} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Timeout fetching PGN for game {game_id}")
                await asyncio.sleep(1)
                continue
                
            except httpx.HTTPStatusError as e:
                # If we get 401/403 and have an API token, try with authentication
                if e.response.status_code in [401, 403] and self.api_token:
                    try:
                        headers["Authorization"] = f"Bearer {self.api_token}"
                        async with httpx.AsyncClient(timeout=timeout) as auth_client:
                            response = await auth_client.get(url, headers=headers)
                            response.raise_for_status()
                            await asyncio.sleep(LICHESS_RATE_LIMIT)
                            return response.text
                    except Exception as auth_e:
                        print(f"Authentication attempt failed for game {game_id}: {auth_e}")
                        if attempt == max_retries - 1:
                            raise
                        continue
                        
                # Handle other HTTP errors
                if e.response.status_code >= 500 and attempt < max_retries - 1:
                    print(f"Server error fetching PGN for game {game_id}, retrying...")
                    await asyncio.sleep(2)
                    continue
                else:
                    # Re-raise the original error if we can't handle it
                    raise
                    
            except httpx.RequestError as e:
                print(f"Request error fetching PGN for game {game_id} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Network error fetching PGN for game {game_id}")
                await asyncio.sleep(1)
                continue
        
        # Should never reach here
        raise Exception(f"Failed to fetch PGN for game {game_id} after all retries")
    
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
