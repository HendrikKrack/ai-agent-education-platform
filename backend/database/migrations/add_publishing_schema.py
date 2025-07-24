"""
Database migration: Add PDF-to-Scenario Publishing Schema
Adds new tables for personas, scenes, files, and reviews
Extends scenarios table with publishing fields
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_agent_platform.db")

def run_migration():
    """Run the publishing schema migration"""
    
    engine = create_engine(DATABASE_URL)
    
    # SQL statements for the migration
    migration_sql = [
        # Extend scenarios table with publishing fields
        """
        ALTER TABLE scenarios ADD COLUMN student_role VARCHAR;
        """,
        """
        ALTER TABLE scenarios ADD COLUMN category VARCHAR;
        """,
        """
        ALTER TABLE scenarios ADD COLUMN difficulty_level VARCHAR;
        """,
        """
        ALTER TABLE scenarios ADD COLUMN estimated_duration INTEGER;
        """,
        """
        ALTER TABLE scenarios ADD COLUMN tags JSON;
        """,
        """
        ALTER TABLE scenarios ADD COLUMN pdf_title VARCHAR;
        """,
        """
        ALTER TABLE scenarios ADD COLUMN pdf_source VARCHAR;
        """,
        """
        ALTER TABLE scenarios ADD COLUMN processing_version VARCHAR DEFAULT '1.0';
        """,
        """
        ALTER TABLE scenarios ADD COLUMN rating_avg FLOAT DEFAULT 0.0;
        """,
        """
        ALTER TABLE scenarios ADD COLUMN rating_count INTEGER DEFAULT 0;
        """,
        
        # Create scenario_personas table
        """
        CREATE TABLE scenario_personas (
            id INTEGER PRIMARY KEY,
            scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
            name VARCHAR NOT NULL,
            role VARCHAR NOT NULL,
            background TEXT,
            correlation TEXT,
            primary_goals JSON,
            personality_traits JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE INDEX idx_scenario_personas_scenario_id ON scenario_personas(scenario_id);
        """,
        """
        CREATE INDEX idx_scenario_personas_name ON scenario_personas(name);
        """,
        
        # Create scenario_scenes table
        """
        CREATE TABLE scenario_scenes (
            id INTEGER PRIMARY KEY,
            scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
            title VARCHAR NOT NULL,
            description TEXT NOT NULL,
            user_goal TEXT,
            scene_order INTEGER DEFAULT 0,
            estimated_duration INTEGER,
            image_url VARCHAR,
            image_prompt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE INDEX idx_scenario_scenes_scenario_id ON scenario_scenes(scenario_id);
        """,
        """
        CREATE INDEX idx_scenario_scenes_title ON scenario_scenes(title);
        """,
        """
        CREATE INDEX idx_scenario_scenes_order ON scenario_scenes(scenario_id, scene_order);
        """,
        
        # Create scene_personas junction table
        """
        CREATE TABLE scene_personas (
            scene_id INTEGER NOT NULL REFERENCES scenario_scenes(id) ON DELETE CASCADE,
            persona_id INTEGER NOT NULL REFERENCES scenario_personas(id) ON DELETE CASCADE,
            involvement_level VARCHAR DEFAULT 'participant',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (scene_id, persona_id)
        );
        """,
        
        # Create scenario_files table
        """
        CREATE TABLE scenario_files (
            id INTEGER PRIMARY KEY,
            scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
            filename VARCHAR NOT NULL,
            file_path VARCHAR,
            file_size INTEGER,
            file_type VARCHAR DEFAULT 'pdf',
            original_content TEXT,
            processed_content TEXT,
            processing_status VARCHAR DEFAULT 'pending',
            processing_log JSON,
            llamaparse_job_id VARCHAR,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        );
        """,
        """
        CREATE INDEX idx_scenario_files_scenario_id ON scenario_files(scenario_id);
        """,
        """
        CREATE INDEX idx_scenario_files_status ON scenario_files(processing_status);
        """,
        
        # Create scenario_reviews table
        """
        CREATE TABLE scenario_reviews (
            id INTEGER PRIMARY KEY,
            scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
            reviewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            review_text TEXT,
            pros JSON,
            cons JSON,
            use_case VARCHAR,
            helpful_votes INTEGER DEFAULT 0,
            total_votes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE INDEX idx_scenario_reviews_scenario_id ON scenario_reviews(scenario_id);
        """,
        """
        CREATE INDEX idx_scenario_reviews_reviewer_id ON scenario_reviews(reviewer_id);
        """,
        """
        CREATE INDEX idx_scenario_reviews_rating ON scenario_reviews(rating);
        """,
        """
        CREATE UNIQUE INDEX idx_scenario_reviews_unique ON scenario_reviews(scenario_id, reviewer_id);
        """
    ]
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("🚀 Starting publishing schema migration...")
                
                # Execute each SQL statement
                for i, sql in enumerate(migration_sql, 1):
                    print(f"  Step {i}/{len(migration_sql)}: {sql.split()[0]} {sql.split()[1] if len(sql.split()) > 1 else ''}...")
                    conn.execute(text(sql))
                
                # Commit transaction
                trans.commit()
                print("✅ Publishing schema migration completed successfully!")
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                raise e
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise e

def rollback_migration():
    """Rollback the publishing schema migration"""
    
    engine = create_engine(DATABASE_URL)
    
    # SQL statements for rollback (in reverse order)
    rollback_sql = [
        "DROP TABLE IF EXISTS scenario_reviews;",
        "DROP TABLE IF EXISTS scenario_files;", 
        "DROP TABLE IF EXISTS scene_personas;",
        "DROP TABLE IF EXISTS scenario_scenes;",
        "DROP TABLE IF EXISTS scenario_personas;",
        
        # Remove added columns from scenarios table
        "ALTER TABLE scenarios DROP COLUMN IF EXISTS student_role;",
        "ALTER TABLE scenarios DROP COLUMN IF EXISTS category;",
        "ALTER TABLE scenarios DROP COLUMN IF EXISTS difficulty_level;",
        "ALTER TABLE scenarios DROP COLUMN IF EXISTS estimated_duration;",
        "ALTER TABLE scenarios DROP COLUMN IF EXISTS tags;",
        "ALTER TABLE scenarios DROP COLUMN IF EXISTS pdf_title;",
        "ALTER TABLE scenarios DROP COLUMN IF EXISTS pdf_source;",
        "ALTER TABLE scenarios DROP COLUMN IF EXISTS processing_version;",
        "ALTER TABLE scenarios DROP COLUMN IF EXISTS rating_avg;",
        "ALTER TABLE scenarios DROP COLUMN IF EXISTS rating_count;",
    ]
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                print("🔄 Rolling back publishing schema migration...")
                
                for i, sql in enumerate(rollback_sql, 1):
                    print(f"  Rollback step {i}/{len(rollback_sql)}: {sql}")
                    try:
                        conn.execute(text(sql))
                    except Exception as e:
                        print(f"    Warning: {e} (continuing...)")
                
                trans.commit()
                print("✅ Publishing schema rollback completed!")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Rollback failed: {e}")
                raise e
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise e

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        run_migration() 