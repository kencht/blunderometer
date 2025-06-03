# Render.com Deployment Quick Fix Guide

## Build Command Syntax Error Solution

If you're getting a bash syntax error with the build command, try these options in order:

### Option 1: Use the build script
```
bash build.sh
```

### Option 2: Use semicolons instead of &&
```
pip install -r requirements.txt; cd frontend; npm install; npm run build
```

### Option 3: Use explicit shell command
```
/bin/bash -c "pip install -r requirements.txt && cd frontend && npm install && npm run build"
```

### Option 4: Multi-line approach
In Render's build command field, you can also try:
```
pip install -r requirements.txt
cd frontend
npm install
npm run build
```

## Current Settings That Should Work:
- **Runtime:** Python 3.12
- **Build Command:** `bash build.sh` (recommended)
- **Start Command:** `python app.py`
- **Environment Variables:**
  - `FLASK_ENV=production`
  - `PORT=10000`

## Verification Steps:
1. Check that `build.sh` is executable (it should be after our changes)
2. Ensure all files are committed to GitHub
3. Try the deployment with the build script approach first

## If Build Still Fails:
1. Check Render's build logs for specific error details
2. Try the semicolon-separated command approach
3. Consider using Render's "Native Environment" instead of "Docker"

The application is ready for deployment once the build command works!
