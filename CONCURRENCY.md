# Blunderometer Concurrency Model

## Multi-User Concurrency

Blunderometer supports concurrent usage by multiple users with the following characteristics:

### User Isolation

- **Database Isolation**: Each user gets their own SQLite database file (`chess_blunders_{username}.db`)
- **Operation Tracking**: User operations (fetching, analyzing) are tracked separately
- **Progress Status**: Each user has their own progress tracking

### Resource Management

- **Concurrent Analysis Limit**: Maximum of 2 simultaneous game analyses (configurable via `MAX_CONCURRENT_ANALYSES`)
- **Stockfish Engine**: Each analysis process uses its own Stockfish engine instance
- **CPU Protection**: The concurrent analysis limit prevents server overload

## How It Works

1. **User Status Tracking**: The application maintains a `user_operations` dictionary that stores operation status for each user
2. **Resource Counting**: Before starting a new analysis, the system counts active analyses across all users
3. **Queue Management**: If maximum concurrent analyses is reached, new requests receive a 429 status code with a friendly message

## Example Scenarios

### Scenario 1: Two Users Analyzing Games
- User A starts analyzing games (1/2 slots used)
- User B starts analyzing games (2/2 slots used)
- User C tries to start analysis → Gets "Maximum concurrent analyses reached" message
- Once User A or B completes, User C can start their analysis

### Scenario 2: Multiple Users Browsing
- Any number of users can browse their statistics simultaneously
- Each user gets data only from their own database
- Viewing stats does not block other operations

### Scenario 3: Fetching and Analyzing
- User A can fetch new games while User B is analyzing games
- Each user can only run one operation at a time for themselves
- Example: User A cannot simultaneously fetch and analyze, but can fetch while User B analyzes

### Scenario 4: User Tab Close/Disconnect
- If a user closes their browser tab, their session times out after 60 seconds of inactivity
- Active operations (analysis, fetching) continue to completion even if the user disconnects
- Resources are freed automatically when operations complete for disconnected users

## Technical Implementation

- Flask backend uses thread-based concurrency for long-running operations
- SQLite connections are not shared between users
- Thread-safe dictionaries track user state
- Resource limits prevent server overload
- Automatic timeout for inactive sessions releases resources

## Configuration

- The concurrent analysis limit can be adjusted by modifying the `MAX_CONCURRENT_ANALYSES` value in `app.py`
- User session timeout can be configured via the `USER_TIMEOUT_SECONDS` value in `app.py`