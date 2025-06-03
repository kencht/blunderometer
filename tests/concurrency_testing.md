# Testing Blunderometer Concurrency

This guide explains how to test the multi-user concurrency features of Blunderometer.

## Using the Concurrency Test Script

The `test_concurrency.py` script simulates multiple users accessing the application simultaneously.

### Prerequisites

1. Make sure Blunderometer server is running:
   ```
   python app.py
   ```

2. Create test users by first running these commands (one-time setup):
   ```
   python3 -c "from database_multiuser import db_manager; db_manager.get_db('test_user1'); db_manager.get_db('test_user2'); db_manager.get_db('test_user3')"
   ```

### Running the Test

```bash
python test_concurrency.py
```

For non-default server URL:
```bash
python test_concurrency.py http://localhost:8000/api
```

### What the Test Does

1. Creates 6 concurrent threads that simulate users
2. Each thread randomly performs operations (stats, analysis)
3. Tracks successful and failed operations
4. Monitors the number of concurrent analyses

### Expected Results

- You should see the concurrency limit (max 2 simultaneous analyses) working
- Some analysis requests should be rejected with 429 status when the limit is reached
- All stats requests should succeed regardless of ongoing operations

## Manual Testing

You can also test concurrency manually using multiple browser windows:

1. Open 3+ browser windows (or incognito tabs)
2. Navigate to the Blunderometer app in each
3. Enter different usernames in each window
4. Try to start analysis in all windows simultaneously
5. Observe that only 2 analyses run at once, with others receiving an error message
6. Verify that stats viewing works in all windows simultaneously

## What to Check

- [ ] Max 2 users can analyze games concurrently 
- [ ] More analysis requests are rejected with a clear message
- [ ] Each user can only start one operation at a time for themselves
- [ ] Any number of users can view stats simultaneously
- [ ] Progress is tracked separately for each user
