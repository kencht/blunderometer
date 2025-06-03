# Render Deployment Configuration

## Backend (Python Flask)
- **Runtime:** python-3.12.0
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app.py`
- **Environment Variables:**
  - `FLASK_ENV=production`
  - `PORT=10000` (Render default)

## Frontend (React)
- **Build Command:** `cd frontend && npm install && npm run build`
- **Publish Directory:** `frontend/build`
- **Node Version:** 18.x

## Deployment Steps

### Option 1: Single Service (Backend serves Frontend) - RECOMMENDED
1. Go to [render.com](https://render.com)
2. Connect your GitHub repository `blunderometer`
3. Create new "Web Service"
4. **Build Command Options (try in order if one fails):**
   - **Option A (Simple):** `pip install -r requirements.txt && cd frontend && npm install && npm run build`
   - **Option B (Script):** `bash build.sh`
   - **Option C (Explicit):** `pip install -r requirements.txt; cd frontend; npm install; npm run build`
5. Set start command: `python app.py`
6. Deploy!

### Option 2: Separate Services
1. **Backend Service:**
   - Type: Web Service
   - Build: `pip install -r requirements.txt`
   - Start: `python app.py`

2. **Frontend Service:**
   - Type: Static Site
   - Build: `cd frontend && npm install && npm run build`
   - Publish: `frontend/build`

## Network Reliability Improvements ✅

The application now includes enhanced network error handling for cloud deployment:

### Backend Improvements
- **Retry Logic**: Automatic retry with exponential backoff for network failures
- **Generous Timeouts**: 45-75 second timeouts optimized for cloud environments
- **Smart Error Handling**: Different retry strategies for different error types
- **Rate Limit Handling**: Automatic backoff for API rate limiting

### Frontend Improvements  
- **Extended Timeouts**: 90-second request timeout for cloud operations
- **Better Error Messages**: User-friendly messages for network issues
- **Timeout Detection**: Specific handling for timeout vs other errors

### Features
- **3 Retry Attempts**: For games fetching with exponential backoff
- **2 Retry Attempts**: For user info and PGN fetching
- **Progressive Timeouts**: Longer timeouts on each retry attempt
- **Cloud-Optimized**: Designed for render.com network characteristics

## Environment Setup
The app will automatically install Stockfish via the `stockfish` Python package.

## Database
SQLite files are stored in `/data` and persist between deployments on Render.

## Testing the Deployment

After deployment, test the network improvements:

1. **Fetch Games**: Try fetching 50 games - should handle timeouts gracefully
2. **Monitor Logs**: Check render.com logs for retry attempts and network status
3. **Error Messages**: Verify user-friendly error messages appear for network issues
4. **Performance**: Expect longer initial response times as the cloud server "warms up"

The enhanced error handling should resolve most network connectivity issues experienced on render.com!
