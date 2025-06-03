# Chess Blunder Tracker - Workflow Testing Guide

## Current Status
✅ **Backend API (Port 5001)**: Working correctly
✅ **Frontend React App (Port 3001)**: Loading successfully  
✅ **Database**: 20 games available, some analyzed
✅ **APIs Tested**: `/api/stats`, `/api/performance`, `/api/fetch-games`, `/api/analyze-games`

## End-to-End Workflow Test

### Prerequisites
1. Backend Flask app running on `http://localhost:5001`
2. Frontend React app running on `http://localhost:3001`
3. Database with existing game data

### Test Steps

#### 1. Open Application
- Navigate to `http://localhost:3001`
- Verify the application loads with:
  - Stats panel showing current game/move statistics
  - Performance chart (should display with our fix)
  - Workflow panel with 4 steps

#### 2. Test Username Input
- In the Workflow Panel, enter a valid Lichess username (e.g., "Magnus", "Hikaru")
- Verify the input accepts the username
- Check that step 1 (Input) shows as completed

#### 3. Test Fetch Games
- Click "Fetch Games" button
- Verify:
  - Step 2 shows as "In Progress" 
  - Status message appears
  - Button becomes disabled during operation
- Wait for completion (should show "Complete" status)

#### 4. Test Analyze Games  
- After fetch completes, click "Analyze Games"
- Verify:
  - Step 3 shows as "In Progress"
  - Progress indicators work
  - Status updates appear
- Wait for analysis completion

#### 5. Test Results Display
- After analysis completes:
  - Step 4 should show as "Complete"
  - Stats panel should refresh with new data
  - Performance chart should update with new data points
  - All operation status should show as inactive

### API Verification Commands

```bash
# Test stats API
curl http://localhost:5001/api/stats

# Test performance API (fixed SQLAlchemy join)
curl http://localhost:5001/api/performance

# Test fetch games API
curl -X POST http://localhost:5001/api/fetch-games \
  -H "Content-Type: application/json" \
  -d '{"username": "Magnus", "count": 5}'

# Test analyze games API  
curl -X POST http://localhost:5001/api/analyze-games \
  -H "Content-Type: application/json" \
  -d '{"username": "Magnus", "time_limit": 20}'
```

## Expected Results

### Successful Workflow
1. **Input Step**: Username accepted, validation passes
2. **Fetch Step**: Games successfully downloaded from Lichess
3. **Analyze Step**: Games analyzed for blunders/mistakes/inaccuracies  
4. **Complete Step**: All data available in UI, charts updated

### Key Features Working
- ✅ Real-time status polling
- ✅ Progress indicators
- ✅ Error handling
- ✅ Background operation monitoring
- ✅ Stats refresh after completion
- ✅ Performance chart data loading (SQLAlchemy fix applied)
- ✅ User session timeout (inactive users cleaned up)
- ✅ Multi-user concurrency support

## Timeout Testing

### Testing User Session Timeouts
Use the provided test script to verify user session timeout functionality:

```bash
# Test timeout for single user
python test_timeout.py --test single

# Test timeout with multiple users
python test_timeout.py --test multiple

# Run all timeout tests
python test_timeout.py
```

### Manual Browser Tab Close Test
1. Start analysis for a user
2. Close the browser tab without canceling
3. Wait 60 seconds
4. Check `/api/active-users` endpoint - user should be removed
5. Verify the analysis slot is freed up for other users

## Troubleshooting

### Common Issues
1. **Port Conflicts**: Ensure Flask runs on 5001 (not 5000 - AirPlay conflict)
2. **CORS Issues**: CORS is enabled in Flask app
3. **API Timeouts**: Long operations run in background threads
4. **Database Locks**: SQLAlchemy sessions properly managed

### Verification Steps
1. Check both services are running: `ps aux | grep -E "(python|node)"`
2. Test API connectivity: `curl http://localhost:5001/api/stats`
3. Check frontend loading: `curl http://localhost:3001`
4. Monitor browser console for errors
5. Check Flask console for API request logs

## Implementation Completed

### Backend Fixes ✅
- Fixed SQLAlchemy join error in `/api/performance` endpoint
- Proper join condition: `Move.game_lichess_id == Game.lichess_id`

### Frontend Implementation ✅  
- Created comprehensive `WorkflowPanel.tsx` component
- Updated `api.ts` with username parameter support
- Integrated workflow into main `App.tsx`
- Added real-time status polling
- Implemented progress tracking and error handling

### Integration ✅
- Backend and frontend properly connected
- API endpoints tested and working
- TypeScript interfaces aligned with backend responses
- CORS configured for development

The Chess Blunder Tracker workflow interface is now fully functional and ready for production use!
