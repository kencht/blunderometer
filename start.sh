#!/bin/bash

echo "🏁 Starting Chess Blunder Tracker..."
echo "======================================"

# Check if frontend is built
if [ ! -d "frontend/build" ]; then
    echo "📦 Building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    echo "✅ Frontend built successfully"
fi

# Check if Stockfish is available
if ! command -v stockfish &> /dev/null; then
    echo "❌ Stockfish not found. Please install it:"
    echo "   macOS: brew install stockfish"
    echo "   Ubuntu: sudo apt install stockfish"
    exit 1
fi

echo "✅ Stockfish found: $(which stockfish)"

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
python3 -c "import flask, chess, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

echo "✅ All dependencies ready"
echo ""
echo "🚀 Starting server at http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

# Start the Flask application
python3 app.py
