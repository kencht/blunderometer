import aiohttp
import asyncio
from datetime import datetime
import re

class LichessClient:
    def __init__(self):
        self.base_url = "https://lichess.org/api"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_user_games(self, username, max_games=100, since=None, until=None, game_types=None):
        """Fetch user's games from Lichess"""
        url = f"{self.base_url}/games/user/{username}"
        
        # Use PGN format and parse it
        params = {
            'max': max_games,
            'moves': 'true',
            'tags': 'true',
            'clocks': 'true',
            'evals': 'false',
            'opening': 'true'
        }
        
        # Add optional parameters
        if since:
            # Convert datetime to milliseconds timestamp
            params['since'] = int(since.timestamp() * 1000)
        if until:
            # Convert datetime to milliseconds timestamp  
            params['until'] = int(until.timestamp() * 1000)
        if game_types:
            # Convert list to comma-separated string
            params['perfType'] = ','.join(game_types)
        
        games = []
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                # Response is in PGN format, need to parse it
                text = await response.text()
                games = self.parse_pgn_response(text)
        
        return games
    
    def parse_pgn_response(self, pgn_text):
        """Parse PGN response into game objects"""
        import re
        import chess.pgn
        import io
        from datetime import datetime
        
        games = []
        
        # Split PGN text into individual games
        game_texts = re.split(r'\n\n(?=\[Event)', pgn_text.strip())
        
        for game_text in game_texts:
            if not game_text.strip():
                continue
                
            try:
                # Parse the game using python-chess
                pgn_io = io.StringIO(game_text)
                game = chess.pgn.read_game(pgn_io)
                
                if game and game.headers:
                    # Extract game data from headers
                    headers = game.headers
                    
                    # Parse date and time
                    date_str = headers.get('UTCDate', '2025.01.01')
                    time_str = headers.get('UTCTime', '00:00:00')
                    datetime_str = f"{date_str} {time_str}"
                    created_at = datetime.strptime(datetime_str, '%Y.%m.%d %H:%M:%S')
                    
                    # Parse time control
                    time_control = headers.get('TimeControl', '300+3')
                    
                    game_data = {
                        'id': headers.get('GameId', ''),
                        'createdAt': int(created_at.timestamp() * 1000),
                        'variant': 'standard',  # Default
                        'status': headers.get('Termination', headers.get('Result', '')),
                        'players': {
                            'white': {
                                'user': {'name': headers.get('White', '')},
                                'rating': int(headers.get('WhiteElo', 0)) if headers.get('WhiteElo') else None
                            },
                            'black': {
                                'user': {'name': headers.get('Black', '')},
                                'rating': int(headers.get('BlackElo', 0)) if headers.get('BlackElo') else None
                            }
                        },
                        'opening': {
                            'name': headers.get('Opening', ''),
                            'eco': headers.get('ECO', '')
                        },
                        'clock': self.parse_time_control(time_control),
                        'pgn': game_text
                    }
                    
                    games.append(game_data)
                    
            except Exception as e:
                print(f"Error parsing game: {e}")
                continue
        
        return games
    
    def parse_time_control(self, time_control_str):
        """Parse time control string like '300+3' into clock dict"""
        try:
            if '+' in time_control_str:
                initial, increment = time_control_str.split('+')
                return {
                    'initial': int(initial),
                    'increment': int(increment)
                }
        except:
            pass
        
        return {'initial': 300, 'increment': 3}  # Default
    
    def parse_game_data(self, game_json, username):
        """Parse Lichess game JSON into our format"""
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
