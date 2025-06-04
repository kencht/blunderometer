# Chess Blunder Tracker

A local web application to analyze your Lichess games and track blunders, mistakes, and inaccuracies using Stockfish engine analysis.

## Features

- 🎯 **Multi-user Support**: Each user gets their own SQLite database
- 📊 **Comprehensive Analysis**: Track blunders (300+ centipawn loss), mistakes (100+), and inaccuracies (50+)
- ⏱️ **Real-time Progress**: Live countdown timers and progress tracking
- 🔍 **Detailed Statistics**: View performance by time control, opening, rating range
- 📈 **Performance Charts**: Visual representation of your improvement over time
- 🎨 **Modern UI**: Clean, responsive React frontend

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Stockfish chess engine

### Simple Setup

1. **Clone and start**
   ```bash
   git clone https://github.com/kencht/blunderometer.git
   cd blunderometer
   ./start.sh
   ```

   The script will automatically:
   - Install dependencies
   - Build the frontend
   - Check for Stockfish
   - Start the server at http://localhost:5000

### Manual Setup

If you prefer manual installation:

1. **Clone the repository**
   ```bash
   git clone https://github.com/kencht/blunderometer.git
   cd blunderometer
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Stockfish**
   - **macOS**: `brew install stockfish`
   - **Ubuntu/Debian**: `sudo apt install stockfish`
   - **Windows**: Download from [stockfish.org](https://stockfishchess.org/download/)

4. **Build the frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## Usage

1. **Enter your Lichess username** in the web interface
2. **Select date range** for games to analyze
3. **Click "Fetch Games"** to download your games
4. **Click "Analyze Games"** to run Stockfish analysis
5. **View your results** in the statistics and charts

## Configuration

The application will automatically detect your Stockfish installation. If needed, you can set a custom path:

```bash
export STOCKFISH_PATH=/path/to/your/stockfish
python app.py
```

## Data Storage

- Each user's data is stored in a separate SQLite database in the `data/` folder
- Example: User "alice" → `data/chess_blunders_alice.db`
- Data persists between sessions

## Performance Notes

- Analysis runs concurrently with a limit of 2 Stockfish engines to prevent CPU overload
- Each game typically takes 30-60 seconds to analyze depending on length
- User sessions timeout after 60 seconds of inactivity to free resources

## Development

To run in development mode with hot reloading:

```bash
# Terminal 1 - Backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm start
```

The frontend will be available at `http://localhost:3000` and proxy API calls to the backend.

## Troubleshooting

### Stockfish not found
If you get "Stockfish not found" errors:
1. Install Stockfish using your package manager
2. Or set the `STOCKFISH_PATH` environment variable

### Port already in use
If port 5000 is busy:
```bash
export FLASK_RUN_PORT=8080
python app.py
```

### Games not loading
- Check that your Lichess username is correct
- Verify your internet connection
- Some users have API rate limits - try smaller date ranges

## License

MIT License - see LICENSE file for details.
