# User Session Timeout Implementation

## Overview

The Blunderometer application now includes a session timeout feature that automatically cleans up inactive user resources when they close their browser tab or disconnect from the application. This prevents orphaned analysis processes from consuming server resources.

## How it Works

### Backend Implementation

1. **User Activity Tracking**:
   - Each user has a `last_active` timestamp that gets updated with every API call
   - The system tracks when users were last active via the `/api/ping` endpoint

2. **Automatic Resource Cleanup**:
   - Inactive users are cleaned up after 60 seconds of inactivity (configurable via `USER_TIMEOUT_SECONDS`)
   - Only inactive users who aren't currently analyzing or fetching games are removed

3. **Cleanup Process**:
   - The cleanup runs as a side-effect of the ping endpoint
   - Users with active operations (analyzing/fetching) are never timed out

### Frontend Implementation

1. **Keep-alive Mechanism**:
   - The frontend sends periodic "ping" requests every 30 seconds to indicate active status
   - Pings are sent automatically in the background while the app is open

2. **Event Handling**:
   - When a user switches usernames, the previous ping session is terminated and a new one starts
   - When the WorkflowPanel component unmounts, pings are automatically stopped

3. **Session Management**:
   - The API service provides methods for starting and stopping ping intervals
   - Each user gets their own independent ping session

## Configuration

The timeout behavior can be adjusted by modifying:

- **Backend**: `USER_TIMEOUT_SECONDS` in `app.py` (default: 60 seconds)
- **Frontend**: Ping interval in `WorkflowPanel.tsx` (default: 30000ms)

## Testing the Timeout Feature

1. **Normal Test**:
   - Start an analysis for User A
   - Close the browser tab
   - Wait 60+ seconds
   - Re-open the application
   - Verify the analysis was terminated

2. **Concurrent Users Test**:
   - Start analysis for Users A and B
   - Close User A's browser tab
   - Verify User B's analysis continues uninterrupted
   - Verify User A's resources are cleaned up after timeout

3. **API Testing**:
   - Use the `/api/active-users` endpoint to monitor cleanup behavior

## Benefits

1. **Resource Management**: Prevents resource leaks from abandoned browser sessions
2. **Improved Concurrency**: Orphaned analysis slots are freed up for other users
3. **Better UX**: Users can resume operations if they accidentally close their browser

The timeout implementation ensures that server resources are only used by active users, improving overall system stability and responsiveness.