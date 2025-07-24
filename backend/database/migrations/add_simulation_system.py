"""
Migration: Add Sequential Simulation System
Adds user progress tracking, conversation logs, and scene enhancements for sequential timeline simulation
"""

import sqlite3
import os
from pathlib import Path

def run_migration():
    """Add simulation system tables to the database"""
    
    # Get database path
    db_path = Path(__file__).parent.parent.parent / "ai_agent_platform.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Adding simulation system tables...")
        
        # 1. Enhance scenario_scenes table with simulation features
        print("Enhancing scenario_scenes table...")
        enhancement_queries = [
            "ALTER TABLE scenario_scenes ADD COLUMN goal_criteria TEXT;",
            "ALTER TABLE scenario_scenes ADD COLUMN max_attempts INTEGER DEFAULT 5;", 
            "ALTER TABLE scenario_scenes ADD COLUMN success_threshold REAL DEFAULT 0.7;",
            "ALTER TABLE scenario_scenes ADD COLUMN hint_triggers TEXT;",
            "ALTER TABLE scenario_scenes ADD COLUMN scene_context TEXT;",
            "ALTER TABLE scenario_scenes ADD COLUMN persona_instructions TEXT;",
            # New fields for timeline cards
            "ALTER TABLE scenario_scenes ADD COLUMN timeout_turns INTEGER;",
            "ALTER TABLE scenario_scenes ADD COLUMN success_metric TEXT;",
        ]
        
        for query in enhancement_queries:
            try:
                cursor.execute(query)
                print(f"✓ Executed: {query}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"⚠ Column already exists: {query}")
                else:
                    print(f"✗ Error with {query}: {e}")
        
        # 2. Create user_progress table
        print("\nCreating user_progress table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
                current_scene_id INTEGER REFERENCES scenario_scenes(id),
                simulation_status TEXT DEFAULT 'not_started',
                scenes_completed TEXT DEFAULT '[]',
                total_attempts INTEGER DEFAULT 0,
                hints_used INTEGER DEFAULT 0,
                forced_progressions INTEGER DEFAULT 0,
                completion_percentage REAL DEFAULT 0.0,
                average_attempts_per_scene REAL DEFAULT 0.0,
                total_time_spent INTEGER DEFAULT 0,
                session_count INTEGER DEFAULT 0,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                final_score REAL,
                completion_notes TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created user_progress table")
        
        # 3. Create scene_progress table
        print("Creating scene_progress table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scene_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_progress_id INTEGER NOT NULL REFERENCES user_progress(id),
                scene_id INTEGER NOT NULL REFERENCES scenario_scenes(id),
                status TEXT DEFAULT 'not_started',
                attempts INTEGER DEFAULT 0,
                hints_used INTEGER DEFAULT 0,
                goal_achieved BOOLEAN DEFAULT 0,
                forced_progression BOOLEAN DEFAULT 0,
                time_spent INTEGER DEFAULT 0,
                messages_sent INTEGER DEFAULT 0,
                ai_responses INTEGER DEFAULT 0,
                goal_achievement_score REAL,
                interaction_quality REAL,
                scene_feedback TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created scene_progress table")
        
        # 4. Create conversation_logs table
        print("Creating conversation_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_progress_id INTEGER NOT NULL REFERENCES user_progress(id),
                scene_id INTEGER NOT NULL REFERENCES scenario_scenes(id),
                message_type TEXT NOT NULL,
                sender_name TEXT,
                persona_id INTEGER REFERENCES scenario_personas(id),
                message_content TEXT NOT NULL,
                message_order INTEGER NOT NULL,
                attempt_number INTEGER DEFAULT 1,
                is_hint BOOLEAN DEFAULT 0,
                ai_context_used TEXT,
                ai_model_version TEXT,
                processing_time REAL,
                user_reaction TEXT,
                led_to_progress BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created conversation_logs table")
        
        # 5. Create indexes for performance
        print("\nCreating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_progress_user_scenario ON user_progress(user_id, scenario_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_progress_status ON user_progress(simulation_status);",
            "CREATE INDEX IF NOT EXISTS idx_scene_progress_user_scene ON scene_progress(user_progress_id, scene_id);",
            "CREATE INDEX IF NOT EXISTS idx_conversation_logs_user_scene ON conversation_logs(user_progress_id, scene_id);",
            "CREATE INDEX IF NOT EXISTS idx_conversation_logs_timestamp ON conversation_logs(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_conversation_logs_message_order ON conversation_logs(scene_id, message_order);",
        ]
        
        for index_query in indexes:
            cursor.execute(index_query)
            print(f"✓ Created index: {index_query.split()[-1].replace(';', '')}")
        
        # Commit all changes
        conn.commit()
        print(f"\n🎉 Successfully added simulation system tables to {db_path}")
        
        # Show table counts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%progress%' OR name LIKE '%conversation%';")
        new_tables = cursor.fetchall()
        print(f"\nNew simulation tables: {[table[0] for table in new_tables]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def rollback_migration():
    """Remove simulation system tables (for development/testing)"""
    
    db_path = Path(__file__).parent.parent.parent / "ai_agent_platform.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Rolling back simulation system migration...")
        
        # Drop tables in reverse order (due to foreign keys)
        rollback_queries = [
            "DROP TABLE IF EXISTS conversation_logs;",
            "DROP TABLE IF EXISTS scene_progress;", 
            "DROP TABLE IF EXISTS user_progress;",
        ]
        
        for query in rollback_queries:
            cursor.execute(query)
            print(f"✓ Executed: {query}")
        
        # Remove added columns from scenario_scenes (SQLite limitation - can't drop columns easily)
        print("⚠ Note: Added columns to scenario_scenes table cannot be easily removed in SQLite")
        print("  Consider recreating the database if full rollback is needed")
        
        conn.commit()
        print("🔄 Simulation system migration rolled back")
        return True
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def add_timeout_turns_column():
    """Add timeout_turns column to scenario_scenes if it does not exist"""
    db_path = Path(__file__).parent.parent.parent / "ai_agent_platform.db"
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Check if column exists
        cursor.execute("PRAGMA table_info(scenario_scenes);")
        columns = [row[1] for row in cursor.fetchall()]
        if "timeout_turns" in columns:
            print("timeout_turns column already exists in scenario_scenes.")
            return True
        # Add the column
        cursor.execute("ALTER TABLE scenario_scenes ADD COLUMN timeout_turns INTEGER;")
        conn.commit()
        print("✓ Added timeout_turns column to scenario_scenes.")
        return True
    except Exception as e:
        print(f"❌ Failed to add timeout_turns column: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    elif len(sys.argv) > 1 and sys.argv[1] == "add_timeout_turns":
        add_timeout_turns_column()
    else:
        run_migration() 