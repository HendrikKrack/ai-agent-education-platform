# AI Simulation Marketplace Platform - Main FastAPI Application
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta
from pathlib import Path

from database.connection import get_db, engine
from database.models import Base, User, Scenario, ScenarioPersona, ScenarioScene
from database.schemas import (
    ScenarioCreate, UserRegister, UserLogin, UserLoginResponse, 
    UserResponse, UserUpdate, PasswordChange
)
from utilities.auth import (
    get_password_hash, authenticate_user, create_access_token, 
    get_current_user, get_current_user_optional, require_admin
)

# Import API routers
from api.parse_pdf import router as pdf_router
from api.simulation import router as simulation_router
from api.publishing import router as publishing_router

# Create FastAPI app
app = FastAPI(
    title="AI Simulation Marketplace Platform",
    description="Platform for creating and sharing AI-powered business simulations",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(pdf_router, tags=["PDF Processing"])
app.include_router(simulation_router, tags=["Simulation"])
app.include_router(publishing_router, tags=["Publishing"])

# Create database tables
Base.metadata.create_all(bind=engine)

# Mount static files for serving images
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Simulation Marketplace Platform API",
        "version": "2.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "database": "connected",
        "api_version": "2.0.0"
    }

@app.get("/api/scenarios/")
async def get_scenarios(db: Session = Depends(get_db)):
    """Get all scenarios with their personas and scenes"""
    try:
        scenarios = db.query(Scenario).order_by(Scenario.created_at.desc()).all()
        
        result = []
        for scenario in scenarios:
            # Get personas for this scenario
            personas = db.query(ScenarioPersona).filter(
                ScenarioPersona.scenario_id == scenario.id
            ).all()
            
            # Get scenes for this scenario
            scenes = db.query(ScenarioScene).filter(
                ScenarioScene.scenario_id == scenario.id
            ).order_by(ScenarioScene.scene_order).all()
            
            scenario_data = {
                "id": scenario.id,
                "title": scenario.title,
                "description": scenario.description,
                "challenge": scenario.challenge,
                "industry": scenario.industry,
                "learning_objectives": scenario.learning_objectives or [],
                "student_role": scenario.student_role,
                "created_at": scenario.created_at.isoformat() if scenario.created_at else None,
                "is_public": scenario.is_public,
                "personas": [
                    {
                        "id": persona.id,
                        "name": persona.name,
                        "role": persona.role,
                        "background": persona.background,
                        "correlation": persona.correlation,
                        "primary_goals": persona.primary_goals or [],
                        "personality_traits": persona.personality_traits or {}
                    }
                    for persona in personas
                ],
                "scenes": [
                    {
                        "id": scene.id,
                        "title": scene.title,
                        "description": scene.description,
                        "user_goal": scene.user_goal,
                        "scene_order": scene.scene_order,
                        "estimated_duration": scene.estimated_duration,
                        "image_url": scene.image_url
                    }
                    for scene in scenes
                ]
            }
            result.append(scenario_data)
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch scenarios: {str(e)}")

# --- USER AUTHENTICATION & MANAGEMENT ---
@app.post("/users/register", response_model=UserResponse)
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        username=user.username,
        password_hash=hashed_password,
        bio=user.bio,
        avatar_url=user.avatar_url,
        profile_public=user.profile_public,
        allow_contact=user.allow_contact
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/users/login", response_model=UserLoginResponse)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": db_user.email})
    
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            username=db_user.username,
            bio=db_user.bio,
            avatar_url=db_user.avatar_url,
            role=db_user.role,
            published_scenarios=db_user.published_scenarios,
            total_simulations=db_user.total_simulations,
            reputation_score=db_user.reputation_score,
            profile_public=db_user.profile_public,
            allow_contact=db_user.allow_contact,
            is_active=db_user.is_active,
            is_verified=db_user.is_verified,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    )

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@app.put("/users/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    # Update fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@app.post("/users/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not authenticate_user(db, current_user.email, password_change.current_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    current_user.password_hash = get_password_hash(password_change.new_password)
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Password changed successfully"}

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile (public information only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only return public profiles
    if not user.profile_public:
        raise HTTPException(status_code=404, detail="Profile is private")
    
    return user

# --- BASIC SCENARIO ENDPOINTS ---
@app.get("/scenarios", response_model=List[dict])
async def get_public_scenarios(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """Get public scenarios for marketplace"""
    scenarios = db.query(Scenario).filter(
        Scenario.is_public == True
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": scenario.id,
            "title": scenario.title,
            "description": scenario.description,
            "category": scenario.category,
            "difficulty_level": scenario.difficulty_level,
            "estimated_duration": scenario.estimated_duration,
            "rating_avg": scenario.rating_avg,
            "rating_count": scenario.rating_count,
            "usage_count": scenario.usage_count
        }
        for scenario in scenarios
    ]

@app.get("/scenarios/{scenario_id}")
async def get_scenario_details(scenario_id: int, db: Session = Depends(get_db)):
    """Get detailed scenario information"""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Count personas and scenes
    persona_count = db.query(ScenarioPersona).filter(ScenarioPersona.scenario_id == scenario_id).count()
    scene_count = db.query(ScenarioScene).filter(ScenarioScene.scenario_id == scenario_id).count()
    
    return {
        "id": scenario.id,
        "title": scenario.title,
        "description": scenario.description,
        "challenge": scenario.challenge,
        "industry": scenario.industry,
        "learning_objectives": scenario.learning_objectives,
        "student_role": scenario.student_role,
        "category": scenario.category,
        "difficulty_level": scenario.difficulty_level,
        "estimated_duration": scenario.estimated_duration,
        "tags": scenario.tags,
        "rating_avg": scenario.rating_avg,
        "rating_count": scenario.rating_count,
        "usage_count": scenario.usage_count,
        "persona_count": persona_count,
        "scene_count": scene_count,
        "is_public": scenario.is_public,
        "created_at": scenario.created_at
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 