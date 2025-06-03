#!/bin/bash
# Run test script for multiple users
# Usage: ./run_test_users.sh

# Create test user databases if they don't exist
echo "Creating test user databases..."
python3 -c "from database_multiuser import db_manager; db_manager.get_db('test_user1'); db_manager.get_db('test_user2'); db_manager.get_db('test_user3')"

# Run the concurrency test with default settings
echo "Starting concurrency test..."
python3 test_concurrency.py

echo ""
echo "Test complete!"
echo "Check CONCURRENCY.md for more information about multi-user support."
