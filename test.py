import asyncio
from database import get_db, Game, Move
from lichess_client import LichessClient

async def test_fetch_games():
    """Test fetching games from Lichess"""
    print("Testing Lichess API...")
    
    async with LichessClient() as client:
        games = await client.get_user_games("timkench", max_games=3)
        print(f"Fetched {len(games)} games")
        
        if games:
            game = games[0]
            parsed = client.parse_game_data(game, "timkench")
            print(f"Sample game: {parsed['lichess_id']} - {parsed['played_at']}")
            print(f"Opening: {parsed['opening_name']}")
            print(f"User color: {parsed['user_color']}")
            print(f"Ratings: {parsed['user_rating']} vs {parsed['opponent_rating']}")

def test_database():
    """Test database connection"""
    print("Testing database...")
    
    db = next(get_db())
    
    # Count existing games and moves
    game_count = db.query(Game).count()
    move_count = db.query(Move).count()
    
    print(f"Games in database: {game_count}")
    print(f"Moves in database: {move_count}")
    
    db.close()

async def main():
    test_database()
    await test_fetch_games()

if __name__ == "__main__":
    asyncio.run(main())
