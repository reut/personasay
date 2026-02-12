#!/usr/bin/env python3
"""
Initialize database from starter template
Run this script to set up a fresh database from the starter template
"""

import os
import shutil
from pathlib import Path

# Paths
BACKEND_DIR = Path(__file__).parent
DATA_DIR = BACKEND_DIR / "data"
STARTER_DB = DATA_DIR / "personasay_starter.db"
TARGET_DB = DATA_DIR / "personasay.db"

def init_database():
    """Initialize database from starter template"""
    
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # Check if target database already exists
    if TARGET_DB.exists():
        response = input(f"Database already exists at {TARGET_DB}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted. Keeping existing database.")
            return
        print("Removing existing database...")
        TARGET_DB.unlink()
    
    # Copy starter database
    if STARTER_DB.exists():
        print(f"Copying starter database from {STARTER_DB}...")
        shutil.copy2(STARTER_DB, TARGET_DB)
        print(f"✓ Database initialized at {TARGET_DB}")
    else:
        print(f"⚠ Warning: Starter database not found at {STARTER_DB}")
        print("The application will create a new empty database on first run.")

if __name__ == "__main__":
    print("PersonaSay Database Initialization")
    print("=" * 50)
    init_database()
