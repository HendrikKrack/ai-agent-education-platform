#!/usr/bin/env python3
"""
Script to recreate database tables with updated schema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from database import engine
from database.models import Base

def recreate_tables():
    """Drop all tables and recreate them"""
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables with new schema...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables recreated successfully!")

if __name__ == "__main__":
    try:
        recreate_tables()
    except Exception as e:
        print(f"❌ Error recreating tables: {e}") 