# Debug Scripts

This directory contains debugging and diagnostic scripts used during development.

## Debug Files

### Analysis Debugging
- **`debug_analysis.py`** - Chess analysis debugging
- **`debug_move_analysis.py`** - Move-specific analysis debugging
- **`debug_centipawn.py`** - Centipawn calculation debugging

## Purpose

These scripts were used to:
- Troubleshoot chess engine integration
- Verify move analysis calculations
- Debug centipawn loss computations
- Test Stockfish integration

## Usage

These are development tools and not part of the main application flow. They can be useful for:
- Understanding how the analysis works
- Debugging issues with chess engine
- Testing specific scenarios

```bash
# Run debug scripts (ensure Stockfish is installed)
python debug/debug_analysis.py
python debug/debug_centipawn.py
python debug/debug_move_analysis.py
```

**Note**: These scripts may require manual configuration of test data or specific chess positions.
