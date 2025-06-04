#!/bin/bash
set -e

echo "Installing system dependencies..."
# Install Stockfish engine (required for chess analysis)
if command -v apt-get >/dev/null 2>&1; then
    echo "Installing Stockfish via apt-get..."
    apt-get update && apt-get install -y stockfish
elif command -v brew >/dev/null 2>&1; then
    echo "Installing Stockfish via Homebrew..."
    brew install stockfish
else
    echo "Warning: Could not install Stockfish automatically. Please ensure it's available in PATH."
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Building frontend..."
npm run build

echo "Build completed successfully!"
