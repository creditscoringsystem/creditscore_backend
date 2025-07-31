#!/usr/bin/env python3
"""
Database migration script for Profile Service
Adds new columns: date_of_birth, address
"""

from sqlalchemy import text
from database import engine

def migrate_database():
    """Migrate database to add new columns"""
    
    # SQL commands to add new columns
    migration_commands = [
        """
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS date_of_birth DATE;
        """,
        """
        ALTER TABLE profiles 
        ADD COLUMN IF NOT EXISTS address VARCHAR(500);
        """
    ]
    
    try:
        with engine.connect() as conn:
            for command in migration_commands:
                print(f"Executing: {command.strip()}")
                conn.execute(text(command))
                conn.commit()
                print("✓ Success")
        
        print("\n🎉 Database migration completed successfully!")
        print("New columns added:")
        print("- date_of_birth (DATE)")
        print("- address (VARCHAR(500))")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    migrate_database() 