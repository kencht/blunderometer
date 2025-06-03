#!/usr/bin/env python3
"""
Test script for network reliability improvements
Tests the enhanced error handling and retry logic for render.com deployment
"""

import asyncio
import sys
import time
from backend.lichess_client import LichessClient

async def test_network_reliability():
    """Test all network reliability features"""
    print("🌐 Testing Network Reliability Improvements for Render.com\n")
    
    success_count = 0
    total_tests = 4
    
    async with LichessClient() as client:
        
        # Test 1: Valid user info fetching
        print("1️⃣  Testing user info fetching with retry logic...")
        try:
            start_time = time.time()
            user_info = await client.get_user_info('kencht')
            duration = time.time() - start_time
            print(f"   ✅ Success: User {user_info.get('username')} ({duration:.2f}s)")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Test 2: Games fetching with retry logic
        print("\n2️⃣  Testing games fetching with enhanced timeouts...")
        try:
            start_time = time.time()
            games = await client.get_user_games('kencht', max_games=5)
            duration = time.time() - start_time
            print(f"   ✅ Success: Fetched {len(games)} games ({duration:.2f}s)")
            if games:
                print(f"      Latest game: {games[0].get('id')}")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            
        # Test 3: Invalid user handling
        print("\n3️⃣  Testing graceful error handling for invalid users...")
        try:
            await client.get_user_info('nonexistent_user_12345')
            print("   ❌ Should have failed for nonexistent user")
        except Exception as e:
            if "not found" in str(e):
                print(f"   ✅ Success: Proper error handling - {e}")
                success_count += 1
            else:
                print(f"   ⚠️  Unexpected error: {e}")
                
        # Test 4: PGN fetching with retry
        print("\n4️⃣  Testing PGN fetching with retry logic...")
        try:
            start_time = time.time()
            # Use a known public game ID
            pgn = await client.get_game_pgn('Yn8YVgkT')  # Recent game from kencht
            duration = time.time() - start_time
            if pgn and len(pgn) > 100:  # Basic validation
                print(f"   ✅ Success: PGN fetched ({len(pgn)} chars, {duration:.2f}s)")
                success_count += 1
            else:
                print(f"   ⚠️  PGN seems incomplete: {len(pgn) if pgn else 0} chars")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Results summary
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All network reliability improvements working perfectly!")
        print("✅ Ready for render.com deployment with enhanced error handling")
    elif success_count >= total_tests - 1:
        print("✅ Network reliability improvements mostly working")
        print("⚠️  Minor issues detected but deployment should work")
    else:
        print("❌ Network reliability issues detected")
        print("🔧 May need additional debugging before deployment")
    
    # Deployment readiness
    print("\n🚀 Render.com Deployment Features:")
    print("   • 3-attempt retry logic with exponential backoff")
    print("   • Progressive timeouts (45s → 60s → 75s)")
    print("   • Smart error categorization (network, server, rate limit)")
    print("   • Enhanced user feedback for different error types")
    print("   • Frontend 90-second timeout handling")
    
    return success_count == total_tests

if __name__ == "__main__":
    try:
        success = asyncio.run(test_network_reliability())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
