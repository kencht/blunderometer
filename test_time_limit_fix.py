#!/usr/bin/env python3
"""
Test script to verify the time limit fixes
"""
import asyncio
import requests
import time

BASE_URL = 'http://localhost:5001'

async def test_time_limit_functionality():
    """Test the updated time limit functionality"""
    
    print("🧪 Testing Time Limit Functionality")
    print("=" * 50)
    
    username = "kencht"
    
    # Test 1: Check if we can start analysis with per-game time limit
    print("\n1. Testing analysis with per-game time limit...")
    
    response = requests.post(f'{BASE_URL}/api/analyze-games', json={
        'username': username,
        'time_limit_per_game': 10,  # 10 seconds per game
    })
    
    if response.status_code == 200:
        print("✅ Successfully started analysis with per-game time limit")
        print(f"Response: {response.json()['message']}")
        
        # Monitor progress for a short time
        print("\n2. Monitoring analysis progress...")
        for i in range(10):  # Monitor for 20 seconds
            time.sleep(2)
            stats_response = requests.get(f'{BASE_URL}/api/stats?username={username}')
            if stats_response.status_code == 200:
                stats = stats_response.json()
                operation_status = stats.get('operation_status', {})
                
                if operation_status.get('analyzing'):
                    progress = operation_status.get('progress', {})
                    current = progress.get('current', 0)
                    total = progress.get('total', 0)
                    current_game = progress.get('current_game', 'Unknown')
                    games_analyzed = progress.get('games_analyzed', 0)
                    games_skipped = progress.get('games_skipped', 0)
                    
                    print(f"  Progress: {current}/{total} games")
                    print(f"  Current game: {current_game}")
                    print(f"  Analyzed: {games_analyzed}, Skipped: {games_skipped}")
                    print(f"  Time limit per game: {progress.get('time_limit_per_game', 'N/A')}s")
                    print("  " + "-" * 40)
                else:
                    print("✅ Analysis completed!")
                    if operation_status.get('last_operation'):
                        print(f"Result: {operation_status['last_operation'].get('result', 'N/A')}")
                    break
            else:
                print(f"❌ Failed to get stats: {stats_response.status_code}")
        
    else:
        print(f"❌ Failed to start analysis: {response.status_code}")
        print(f"Error: {response.text}")
    
    print("\n3. Testing analysis with total time limit...")
    
    # Wait a moment before next test
    time.sleep(3)
    
    response = requests.post(f'{BASE_URL}/api/analyze-games', json={
        'username': username,
        'time_limit_per_game': 15,  # 15 seconds per game
        'total_time_limit': 45      # 45 seconds total
    })
    
    if response.status_code == 200:
        print("✅ Successfully started analysis with total time limit")
        print(f"Response: {response.json()['message']}")
        
        # Monitor for total time limit
        print("\n4. Monitoring total time limit enforcement...")
        start_time = time.time()
        for i in range(30):  # Monitor for up to 60 seconds
            time.sleep(2)
            elapsed = time.time() - start_time
            
            stats_response = requests.get(f'{BASE_URL}/api/stats?username={username}')
            if stats_response.status_code == 200:
                stats = stats_response.json()
                operation_status = stats.get('operation_status', {})
                
                if operation_status.get('analyzing'):
                    progress = operation_status.get('progress', {})
                    print(f"  Elapsed: {elapsed:.1f}s, Total limit: {progress.get('total_time_limit', 'N/A')}s")
                    print(f"  Progress: {progress.get('current', 0)}/{progress.get('total', 0)} games")
                else:
                    print(f"✅ Analysis stopped after {elapsed:.1f}s")
                    if operation_status.get('last_operation'):
                        print(f"Result: {operation_status['last_operation'].get('result', 'N/A')}")
                    break
        
    else:
        print(f"❌ Failed to start analysis with total limit: {response.status_code}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_time_limit_functionality())
