# 🎯 Blunderometer

A comprehensive chess analysis tool that fetches your Lichess games and analyzes them to identify blunders, mistakes, and inaccuracies using Stockfish engine analysis.

![Blunderometer Screenshot](https://via.placeholder.com/800x400/2563eb/ffffff?text=Blunderometer+Dashboard)

## 🚀 Features

### Game Analysis
- **Per-Game Time Limits**: Set individual time limits for each game analysis (10-60 seconds)
- **Session Time Limits**: Optional total session time limits to control overall analysis duration
- **Real-time Progress Tracking**: Live countdown timers and progress bars during analysis
- **Comprehensive Move Evaluation**: Identifies blunders (≥300cp), mistakes (≥100cp), and inaccuracies (≥50cp)

### Data Management
- **Lichess Integration**: Automatically fetch games from Lichess API
- **Multi-User Support**: Separate databases for different users
- **Incremental Updates**: Fetch only new games or fill in historical gaps
- **Persistent Storage**: SQLite database with full game and move history

### Visualization & Analytics
- **Performance Charts**: Track your improvement over time
- **Time Control Analysis**: Compare performance across different time controls
- **Detailed Statistics**: Comprehensive stats on games, moves, and errors
- **Interactive Dashboard**: Modern React-based UI with real-time updates## 🛠️ Technical Stack

### Backend
- **Python 3.12+** - Core application logic
- **Flask** - Web API and serving
- **SQLAlchemy** - Database ORM
- **Stockfish** - Chess engine for analysis
- **python-chess** - Chess game manipulation
- **asyncio** - Asynchronous game processing

### Frontend
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Chart.js** - Data visualization
- **Lucide React** - Icon library

### Database
- **SQLite** - Lightweight, file-based database
- **Multi-tenant** - Separate databases per user

## 📦 Installation

### Prerequisites
- Python 3.12 or higher
- Node.js 18 or higher
- Stockfish chess engine

### Install Stockfish

**macOS (with Homebrew):**
```bash
brew install stockfish
```

**Ubuntu/Debian:**
```bash
sudo apt-get install stockfish
```

**Windows:**
Download from [Stockfish official site](https://stockfishchess.org/download/)

### Backend Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/blunderometer.git
cd blunderometer
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure Stockfish path (if needed):**
Edit `game_analyzer.py` and update the `engine_path` if Stockfish is not in `/opt/homebrew/bin/stockfish`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install Node.js dependencies:**
```bash
npm install
```

## 🚀 Usage

### Start the Application

1. **Start the backend (in root directory):**
```bash
python app.py
```
The API will be available at `http://localhost:5001`

2. **Start the frontend (in frontend directory):**
```bash
cd frontend
npm start
```
The web interface will be available at `http://localhost:3000`

### Using the Application

1. **Enter your Lichess username** in the input field
2. **Configure analysis settings:**
   - **Games**: Number of games to fetch (25-200)
   - **Per Game (s)**: Time limit for analyzing each game (10-60 seconds)
   - **Total (s)**: Optional total session time limit (300-1800 seconds)

3. **Fetch games** from Lichess (newer or older games)
4. **Start analysis** and watch the real-time progress
5. **View results** in the comprehensive dashboard

### Analysis Features

- **Real-time Progress**: Watch games being analyzed with countdown timers
- **Time Management**: Set per-game limits to balance speed vs accuracy
- **Session Control**: Use total time limits for quick analysis sessions
- **Detailed Tracking**: See current game being analyzed and completion stats

## 📊 Understanding the Results

### Move Classifications
- **Blunder**: Moves losing ≥300 centipawns (major mistakes)
- **Mistake**: Moves losing ≥100 centipawns (significant errors)
- **Inaccuracy**: Moves losing ≥50 centipawns (minor imprecisions)

### Performance Metrics
- **Games Analyzed**: Total games with complete analysis
- **Average Centipawn Loss**: Overall accuracy metric
- **Error Distribution**: Breakdown by time control and rating
- **Improvement Trends**: Track progress over time

## 🔧 Configuration

### Time Limits
The application supports two types of time limits:

1. **Per-Game Limit**: Maximum time to spend analyzing each individual game
2. **Total Session Limit**: Maximum time for the entire analysis session

This allows you to balance between analysis depth and total processing time.

### Engine Settings
Stockfish analysis uses depth 15 by default. You can modify this in `game_analyzer.py`:
```python
eval_before = await engine.analyse(board, chess.engine.Limit(depth=15))
```

## 🗃️ Database Schema

The application uses separate SQLite databases for each user with two main tables:

### Games Table
- Game metadata (ID, date, rating, time control, etc.)
- Analysis status and timestamps
- Result and opening information

### Moves Table
- Individual move analysis results
- Centipawn loss calculations
- Move classifications (blunder/mistake/inaccuracy)

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Test basic analysis
python test_simple_analysis.py

# Test time limit functionality
python test_time_limit_fix.py

# Test the complete workflow
python test_workflow.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Lichess](https://lichess.org) for providing the excellent API
- [Stockfish](https://stockfishchess.org) for the powerful chess engine
- [python-chess](https://github.com/niklasf/python-chess) for chess game manipulation
- The chess community for inspiration and feedback

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/blunderometer/issues) page
2. Create a new issue with detailed information
3. Include your operating system, Python version, and error messages

---

**Happy analyzing! 🎯♟️**
