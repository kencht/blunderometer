#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('backend')
from lichess_client import LichessClient

# This is a known public Lichess game (using a valid game ID from TV channels)
PUBLIC_GAME_ID = "SgX5PvxJ"

async def print_public_game_pgn():
    print(f"Attempting to fetch PGN for public game {PUBLIC_GAME_ID}...")
    async with LichessClient() as lichess:
        try:
            pgn = await lichess.get_game_pgn(PUBLIC_GAME_ID)
            print(f"PGN for public game {PUBLIC_GAME_ID}:")
            print(pgn)
        except Exception as e:
            print(f"Failed to fetch PGN for public game: {e}")
    print("Done.")

if __name__ == "__main__":
    asyncio.run(print_public_game_pgn())
