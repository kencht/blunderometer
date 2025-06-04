#!/usr/bin/env python3
"""
Copy database files from repository to cloud storage location on startup
This ensures pre-existing databases are available in cloud deployment
"""

import os
import shutil
import sys

def copy_databases():
    """Copy database files from repository data/ to cloud storage location"""
    
    # Source and destination directories
    source_dir = "data"
    
    # Use the same logic as database_multiuser.py to determine target directory
    if os.getenv('RENDER') or os.getenv('PORT'):  # Cloud environment
        dest_dir = "/tmp/chess_data"
    else:  # Local development
        dest_dir = "data"  # No need to copy in local development
        return
    
    print(f"[STARTUP] Copying databases from {source_dir} to {dest_dir}")
    
    # Create destination directory
    os.makedirs(dest_dir, exist_ok=True)
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"[STARTUP] No source database directory found at {source_dir}")
        return
    
    # Copy all database files
    copied_count = 0
    for filename in os.listdir(source_dir):
        if filename.endswith('.db'):
            source_path = os.path.join(source_dir, filename)
            dest_path = os.path.join(dest_dir, filename)
            
            # Only copy if destination doesn't exist or is older
            if not os.path.exists(dest_path) or os.path.getmtime(source_path) > os.path.getmtime(dest_path):
                print(f"[STARTUP] Copying {filename}")
                shutil.copy2(source_path, dest_path)
                copied_count += 1
            else:
                print(f"[STARTUP] Skipping {filename} (destination is newer)")
    
    print(f"[STARTUP] Database copy complete. {copied_count} files copied.")

if __name__ == "__main__":
    copy_databases()
