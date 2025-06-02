#!/usr/bin/env python3

import sys
import os

# Add backend to path
sys.path.append('backend')

print("Testing imports...")

try:
    from database import get_db
    print("✓ Database import successful")
except Exception as e:
    print(f"❌ Database import failed: {e}")

try:
    from models import User, Game, Move
    print("✓ Models import successful")
except Exception as e:
    print(f"❌ Models import failed: {e}")

try:
    from lichess_client import LichessClient
    print("✓ Lichess client import successful")
except Exception as e:
    print(f"❌ Lichess client import failed: {e}")

try:
    from chess_analyzer import ChessAnalyzer
    print("✓ Chess analyzer import successful")
except Exception as e:
    print(f"❌ Chess analyzer import failed: {e}")
    import traceback
    traceback.print_exc()

print("Import test completed.")
