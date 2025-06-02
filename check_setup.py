#!/usr/bin/env python3
"""
System setup checker for Blunderometer
Run this script to verify your environment is ready
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check Python version is 3.12+"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 12:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.12+ required")
        return False

def check_node_version():
    """Check Node.js version"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"📦 Node.js version: {version}")
            # Extract major version number
            major_version = int(version[1:].split('.')[0])
            if major_version >= 18:
                print("✅ Node.js version is compatible")
                return True
            else:
                print("❌ Node.js 18+ required")
                return False
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False

def check_stockfish():
    """Check if Stockfish is available"""
    stockfish_paths = [
        "/opt/homebrew/bin/stockfish",  # macOS Homebrew
        "/usr/bin/stockfish",           # Linux
        "/usr/local/bin/stockfish",     # Alternative Linux
        "stockfish",                    # In PATH
    ]
    
    for path in stockfish_paths:
        try:
            result = subprocess.run([path, 'quit'], 
                                  input='quit\n', 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                print(f"✅ Stockfish found at: {path}")
                return True, path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    print("❌ Stockfish not found")
    print("   Install with: brew install stockfish (macOS) or sudo apt install stockfish (Linux)")
    return False, None

def check_dependencies():
    """Check if Python dependencies can be imported"""
    required_packages = [
        'flask',
        'flask_cors', 
        'chess',
        'aiohttp',
        'sqlalchemy',
        'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} missing")
            missing.append(package)
    
    if missing:
        print(f"\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    return True

def check_frontend_dependencies():
    """Check if frontend dependencies are installed"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    node_modules = frontend_dir / "node_modules"
    package_json = frontend_dir / "package.json"
    
    if not package_json.exists():
        print("❌ package.json not found in frontend/")
        return False
    
    if not node_modules.exists():
        print("❌ node_modules not found - run 'npm install' in frontend/")
        return False
    
    print("✅ Frontend dependencies appear to be installed")
    return True

def main():
    print("🎯 Blunderometer Setup Checker")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Node.js Version", check_node_version),
        ("Stockfish Engine", lambda: check_stockfish()[0]),
        ("Python Dependencies", check_dependencies),
        ("Frontend Dependencies", check_frontend_dependencies),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        results.append(check_func())
    
    print("\n" + "=" * 40)
    print("📊 SETUP SUMMARY")
    print("=" * 40)
    
    all_passed = all(results)
    if all_passed:
        print("🎉 All checks passed! You're ready to run Blunderometer!")
        print("\nNext steps:")
        print("1. Start backend: python app.py")
        print("2. Start frontend: cd frontend && npm start")
        print("3. Open browser: http://localhost:3000")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nNeed help? Check the README.md troubleshooting section.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
