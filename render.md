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

### Option 1: Single Service (Backend serves Frontend)
1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Create new "Web Service"
4. Set build command: `pip install -r requirements.txt && cd frontend && npm install && npm run build:ci`
5. Set start command: `python app.py`
6. Deploy!

### Option 2: Separate Services
1. **Backend Service:**
   - Type: Web Service
   - Build: `pip install -r requirements.txt`
   - Start: `python app.py`

2. **Frontend Service:**
   - Type: Static Site
   - Build: `cd frontend && npm install && npm run build:ci`
   - Publish: `frontend/build`

## Environment Setup
The app will automatically install Stockfish via the `stockfish` Python package.

## Database
SQLite files are stored in `/data` and persist between deployments on Render.
