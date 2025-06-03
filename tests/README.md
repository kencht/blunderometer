# Tests

This directory contains test scripts to verify the functionality of the Blunderometer application.

## Test Files

### Core Functionality Tests
- **`test_simple_analysis.py`** - Basic analysis functionality test
- **`test_improved_analysis.py`** - Enhanced analysis features test
- **`test_analysis.py`** - General analysis system test
- **`test_imports.py`** - Module import verification

### Feature-Specific Tests
- **`test_time_limit_fix.py`** - Time limit functionality verification
- **`test_workflow.py`** - Complete workflow testing

### Legacy Tests
- **`test.py`** - General test script

## Running Tests

Make sure the Flask backend is running before executing tests:

```bash
# Start the backend
python app.py

# Run individual tests
python tests/test_time_limit_fix.py
python tests/test_workflow.py
python tests/test_simple_analysis.py

# Or run all tests
for test in tests/test_*.py; do python "$test"; done
```

## Test Documentation

See `WORKFLOW_TEST_GUIDE.md` for detailed testing procedures and expected outcomes.
