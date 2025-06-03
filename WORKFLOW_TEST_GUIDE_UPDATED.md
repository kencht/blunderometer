# 🧪 Workflow Testing Guide

## Updated for Username Submit Button System

This guide helps you test the complete workflow of the Blunderometer application, including the new username submission system that prevents database creation on every keystroke.

## 🎯 Prerequisites

1. **Backend running** on `http://localhost:5001`
2. **Frontend running** on `http://localhost:3000` (or 3001, 3002, etc.)
3. **Valid Lichess username** for testing

## 🚀 Complete Workflow Test

### Step 1: Username Submission
1. Open the frontend in your browser
2. **Type a username** in the input field (notice: no database files created yet)
3. **Click "Submit" button** or press Enter
4. **Verify**: "Active: username" appears
5. **Check**: Only now should a database file be created in `data/` directory

### Step 2: Game Fetching
1. In the "Getting Started" panel, click **"Fetch 50 Newer Games"**
2. **Watch progress**: "Fetching newer games from Lichess..." 
3. **Verify success**: "Games fetched successfully! Ready to analyze."
4. **Check stats**: Numbers should update in the Performance Overview

### Step 3: Game Analysis
1. Configure analysis settings:
   - **Per Game**: 20 seconds (recommended)
   - **Total Session**: 600 seconds (10 minutes)
2. Click **"Start Analysis"**
3. **Watch live progress**:
   ```
   🧠 Analyzing game 5 / 23
   ⏱️ Per game limit: 0:15 remaining  
   📊 Estimated remaining: 6:30
   🎯 Current: ABC123XYZ
   ✅ Completed: 5 | Skipped: 0
   ```

### Step 4: Results Verification
1. **Performance Overview**: Check updated statistics
2. **Performance Chart**: Verify data points appear
3. **Time Control Analysis**: Confirm breakdown by game type
4. **Filters**: Test different time controls and date ranges

## 🔄 Multi-User Testing

### Test Concurrent Users
1. **Open multiple browser tabs/windows**
2. **Use different usernames** in each tab:
   - Tab 1: Submit "user1" 
   - Tab 2: Submit "user2"
   - Tab 3: Submit "user3"
3. **Start operations simultaneously**
4. **Verify**: Each user operates independently

### Expected Behavior
- ✅ **Data isolation**: Each user sees only their own data
- ✅ **Concurrent fetching**: Multiple users can fetch games simultaneously
- ✅ **Analysis queueing**: Max 2 concurrent analyses (others get "Too many concurrent analyses" message)
- ✅ **Session management**: Each user maintains their own session

## 🕐 Timeout Testing

### Test Session Timeout
1. **Submit username** and start analysis
2. **Close browser tab** (simulates user leaving)
3. **Wait 60+ seconds**
4. **Check backend logs**: Should show session cleanup
5. **Reopen tab**: Session should be reset

### Test Keep-Alive
1. **Submit username** and start analysis  
2. **Keep browser tab open** and active
3. **Monitor network tab**: Should see ping requests every 30 seconds
4. **Verify**: Analysis continues without interruption

## 🧪 API Testing (Manual)

### Test Username Submit Protection
```bash
# This should work (proper username submission)
curl -X GET "http://localhost:5001/api/stats?username=testuser"

# Check that database files are only created when username is "submitted"
ls data/  # Should only show files for submitted usernames
```

### Test Concurrent Analysis Limit
```bash
# Start first analysis
curl -X POST "http://localhost:5001/api/analyze-games" \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "time_limit_per_game": 30}'

# Start second analysis (should work)  
curl -X POST "http://localhost:5001/api/analyze-games" \
  -H "Content-Type: application/json" \
  -d '{"username": "user2", "time_limit_per_game": 30}'

# Start third analysis (should get 429 error)
curl -X POST "http://localhost:5001/api/analyze-games" \
  -H "Content-Type: application/json" \
  -d '{"username": "user3", "time_limit_per_game": 30}'
```

## 🎯 Expected Results

### Successful Workflow
- **Username submission**: Clean input → submit → activation
- **Game fetching**: Progress updates → success message → updated stats
- **Analysis**: Real-time countdown → completion → updated charts
- **Multi-user**: Independent operations per username
- **Timeout**: Proper cleanup when users leave

### Performance Indicators
- **Frontend**: Responsive UI with real-time updates
- **Backend**: Sub-second API responses for stats/data
- **Analysis**: 15-25 seconds per game (depending on time limit)
- **Memory**: Stable usage even with multiple concurrent users

## 🐛 Troubleshooting

### Common Issues
1. **"No games to analyze"**: User needs to fetch games first
2. **"Too many concurrent analyses"**: Wait for other analyses to complete
3. **"Username is required"**: Submit a username before operations
4. **Slow analysis**: Reduce per-game time limit or check CPU usage

### Debug Commands
```bash
# Check active sessions
curl "http://localhost:5001/api/stats?username=testuser"

# Check user database
ls -la data/
sqlite3 data/chess_blunders_testuser.db ".tables"

# Monitor backend logs
tail -f app.log  # If logging is enabled
```

## ✅ Validation Checklist

- [ ] Username input doesn't create database files
- [ ] Submit button properly activates username
- [ ] Game fetching works with progress updates
- [ ] Analysis runs with real-time countdown
- [ ] Multiple users can operate independently
- [ ] Concurrent analysis limit enforced (max 2)
- [ ] Session timeout works when tabs closed
- [ ] Keep-alive maintains active sessions
- [ ] Charts and stats update correctly
- [ ] All time controls can be filtered

This comprehensive testing ensures your Blunderometer is production-ready! 🏆
