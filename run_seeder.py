#!/usr/bin/env python3
"""
Manual database seeder script.
Run this script to seed the database with test data.

Usage:
    python run_seeder.py
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.auth.seeder import seed_database

async def main():
    """Run the database seeder."""
    print("🌱 Starting manual database seeding...")
    try:
        await seed_database()
        print("✅ Seeding completed successfully!")
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
