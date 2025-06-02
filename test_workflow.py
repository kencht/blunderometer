#!/usr/bin/env python3
"""
End-to-end workflow test script
Tests the complete user workflow: fetch games -> analyze games -> view results
"""

import requests
import time
import json

BASE_URL = 'http://localhost:5001'

def test_workflow():
    print("=== Testing Chess Blunder Tracker Workflow ===\n")
    username = 'timkench'
    # Step 1: Check initial stats
    print("1. Checking initial stats...")
    response = requests.get(f'{BASE_URL}/api/stats', params={'username': username})
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✓ Initial games: {stats['games']['total']}")
        print(f"   ✓ Analyzed games: {stats['games']['analyzed']}")
        print(f"   ✓ Operation status: {stats['operation_status']}")
    else:
        print(f"   ✗ Failed to get stats: {response.status_code}")
        return False
    # Step 2: Test fetch games
    print("\n2. Testing fetch games...")
    fetch_data = {'username': username, 'batch_size': 5}
    response = requests.post(f'{BASE_URL}/api/fetch-games', 
                           headers={'Content-Type': 'application/json'}, 
                           data=json.dumps(fetch_data))
    if response.status_code == 200:
        print(f"   ✓ Fetch request successful: {response.json()['message']}")
        # Wait and monitor progress
        print("   Monitoring fetch progress...")
        for i in range(10):  # Wait up to 10 seconds
            time.sleep(1)
            stats_response = requests.get(f'{BASE_URL}/api/stats', params={'username': username})
            if stats_response.status_code == 200:
                status = stats_response.json()['operation_status']
                if not status['fetching']:
                    print(f"   ✓ Fetch completed: {status.get('last_operation', {}).get('result', 'Unknown')}")
                    break
                else:
                    print(f"   ⏳ Still fetching... ({i+1}s)")
        else:
            print("   ⚠ Fetch took longer than expected")
    else:
        print(f"   ✗ Fetch request failed: {response.status_code} - {response.text}")
        return False
    # Step 3: Test analyze games
    print("\n3. Testing analyze games...")
    analyze_data = {'username': username, 'time_limit': 10}
    response = requests.post(f'{BASE_URL}/api/analyze-games', 
                           headers={'Content-Type': 'application/json'}, 
                           data=json.dumps(analyze_data))
    if response.status_code == 200:
        print(f"   ✓ Analysis request successful: {response.json()['message']}")
        # Wait and monitor progress
        print("   Monitoring analysis progress...")
        for i in range(15):  # Wait up to 15 seconds
            time.sleep(1)
            stats_response = requests.get(f'{BASE_URL}/api/stats', params={'username': username})
            if stats_response.status_code == 200:
                status = stats_response.json()['operation_status']
                if not status['analyzing']:
                    print(f"   ✓ Analysis completed: {status.get('last_operation', {}).get('result', 'Unknown')}")
                    break
                else:
                    print(f"   ⏳ Still analyzing... ({i+1}s)")
        else:
            print("   ⚠ Analysis took longer than expected")
    else:
        print(f"   ✗ Analysis request failed: {response.status_code} - {response.text}")
        return False
    # Step 4: Test performance data
    print("\n4. Testing performance data...")
    response = requests.get(f'{BASE_URL}/api/performance', params={'username': username})
    if response.status_code == 200:
        performance = response.json()
        print(f"   ✓ Performance data available: {len(performance)} data points")
        if performance:
            latest = performance[-1]
            print(f"   ✓ Latest: {latest['date']} - Avg CP Loss: {latest['avg_centipawn_loss']}")
    else:
        print(f"   ✗ Failed to get performance data: {response.status_code}")
        return False
    # Step 5: Final stats check
    print("\n5. Final stats check...")
    response = requests.get(f'{BASE_URL}/api/stats', params={'username': username})
    if response.status_code == 200:
        final_stats = response.json()
        print(f"   ✓ Final games: {final_stats['games']['total']}")
        print(f"   ✓ Final analyzed: {final_stats['games']['analyzed']}")
        print(f"   ✓ Blunder rate: {final_stats['moves']['blunder_rate']}%")
        print(f"   ✓ Operation complete: {not final_stats['operation_status']['fetching'] and not final_stats['operation_status']['analyzing']}")
    else:
        print(f"   ✗ Failed to get final stats: {response.status_code}")
        return False
    print("\n=== Workflow Test Completed Successfully! ===")
    return True

if __name__ == '__main__':
    try:
        test_workflow()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
