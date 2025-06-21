#!/usr/bin/env python3
"""
Database initialization script for CastLang backend.
This script creates the database tables and can be used for initial setup.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database import create_tables, engine
from src.models import Base

def init_database():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    try:
        create_tables()
        print("✅ Database tables created successfully!")
        
        # Test the connection
        with engine.connect() as conn:
            result = conn.execute("SELECT version();")
            version = result.fetchone()[0]
            print(f"✅ Database connection successful! PostgreSQL version: {version}")
            
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. Database 'castlang' exists")
        print("3. User 'castlang' has proper permissions")
        print("4. DATABASE_URL environment variable is set correctly")
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1) 