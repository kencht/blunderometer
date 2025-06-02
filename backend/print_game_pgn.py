#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('backend')
from lichess_client import LichessClient

async def print_game_pgn():
    async with LichessClient() as lichess:
        games = await lichess.get_user_games("kencht", 5, None, ["blitz", "rapid", "classical"])
        print(f"Fetched {len(games)} games. IDs:", [g.get('id') for g in games])
        for game in games:
            if game['id'] == 'Yn8YVgkT':
                print("PGN for game Yn8YVgkT:")
                print(game.get('pgn', 'NO_PGN'))
                break
        else:
            print("Game Yn8YVgkT not found in API response.")

if __name__ == "__main__":
    asyncio.run(print_game_pgn())
