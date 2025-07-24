#!/usr/bin/env python3
"""
Database inspection script to see stored scenarios, personas, and scenes
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.models import Scenario, ScenarioPersona, ScenarioScene, ScenarioFile, ScenarioReview

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_agent_platform.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inspect_database():
    """Inspect the database contents"""
    
    db = SessionLocal()
    
    try:
        print("🔍 DATABASE INSPECTION")
        print("=" * 50)
        
        # Check scenarios
        scenarios = db.query(Scenario).all()
        print(f"\n📋 SCENARIOS ({len(scenarios)} total):")
        
        if not scenarios:
            print("  ❌ No scenarios found in database")
        else:
            for scenario in scenarios:
                print(f"\n  📝 Scenario ID: {scenario.id}")
                print(f"     Title: {scenario.title}")
                print(f"     Student Role: {scenario.student_role}")
                print(f"     Category: {scenario.category}")
                print(f"     Difficulty: {scenario.difficulty_level}")
                print(f"     Is Public: {scenario.is_public}")
                print(f"     Created: {scenario.created_at}")
                
                # Check personas for this scenario
                personas = db.query(ScenarioPersona).filter(
                    ScenarioPersona.scenario_id == scenario.id
                ).all()
                print(f"     👥 Personas: {len(personas)}")
                for persona in personas:
                    print(f"        - {persona.name} ({persona.role})")
                
                # Check scenes for this scenario
                scenes = db.query(ScenarioScene).filter(
                    ScenarioScene.scenario_id == scenario.id
                ).order_by(ScenarioScene.scene_order).all()
                print(f"     🎬 Scenes: {len(scenes)}")
                for scene in scenes:
                    print(f"        {scene.scene_order}. {scene.title}")
                    if scene.image_url:
                        print(f"           🖼️ Has image: {scene.image_url[:50]}...")
                
                # Check files for this scenario
                files = db.query(ScenarioFile).filter(
                    ScenarioFile.scenario_id == scenario.id
                ).all()
                print(f"     📁 Files: {len(files)}")
                for file in files:
                    print(f"        - {file.filename} ({file.processing_status})")
        
        # Check recent activity
        print(f"\n📊 DATABASE STATISTICS:")
        print(f"     Total Scenarios: {db.query(Scenario).count()}")
        print(f"     Total Personas: {db.query(ScenarioPersona).count()}")
        print(f"     Total Scenes: {db.query(ScenarioScene).count()}")
        print(f"     Total Files: {db.query(ScenarioFile).count()}")
        print(f"     Total Reviews: {db.query(ScenarioReview).count()}")
        
        # Check for published scenarios
        published = db.query(Scenario).filter(Scenario.is_public == True).count()
        drafts = db.query(Scenario).filter(Scenario.is_public == False).count()
        print(f"     Published: {published}")
        print(f"     Drafts: {drafts}")
        
        # Show table structure
        print(f"\n🗃️ TABLE STRUCTURE:")
        with engine.connect() as conn:
            # Check if our new tables exist
            tables = [
                "scenarios", "scenario_personas", "scenario_scenes", 
                "scenario_files", "scenario_reviews", "scene_personas"
            ]
            
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"     ✅ {table}: {result} rows")
                except Exception as e:
                    print(f"     ❌ {table}: {str(e)}")
        
    except Exception as e:
        print(f"❌ Database inspection failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

def show_recent_scenarios(limit=5):
    """Show most recent scenarios with details"""
    
    db = SessionLocal()
    
    try:
        print(f"\n🕐 RECENT SCENARIOS (last {limit}):")
        print("=" * 50)
        
        recent = db.query(Scenario).order_by(
            Scenario.created_at.desc()
        ).limit(limit).all()
        
        if not recent:
            print("  ❌ No recent scenarios found")
            return
        
        for i, scenario in enumerate(recent, 1):
            print(f"\n{i}. 📝 {scenario.title}")
            print(f"   ID: {scenario.id}")
            print(f"   Created: {scenario.created_at}")
            print(f"   Source: {scenario.source_type}")
            print(f"   Public: {'✅' if scenario.is_public else '❌'}")
            
            # Show some content
            if scenario.description:
                desc = scenario.description[:100] + "..." if len(scenario.description) > 100 else scenario.description
                print(f"   Description: {desc}")
            
            # Count related data
            persona_count = db.query(ScenarioPersona).filter(
                ScenarioPersona.scenario_id == scenario.id
            ).count()
            scene_count = db.query(ScenarioScene).filter(
                ScenarioScene.scenario_id == scenario.id
            ).count()
            
            print(f"   Content: {persona_count} personas, {scene_count} scenes")
    
    except Exception as e:
        print(f"❌ Failed to show recent scenarios: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting database inspection...")
    inspect_database()
    show_recent_scenarios()
    print("\n✅ Database inspection complete!") 