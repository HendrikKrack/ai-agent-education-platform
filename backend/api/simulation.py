"""
Sequential Timeline Simulation API
Handles guided simulation with AI personas, goal validation, and progress tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional, Dict, Any
import json
import time
from datetime import datetime, timedelta
import openai
import os

from database.connection import get_db
from database.models import (
    Scenario, ScenarioScene, ScenarioPersona, User,
    UserProgress, SceneProgress, ConversationLog
)
from database.schemas import (
    SimulationStartRequest, SimulationStartResponse, SimulationScenarioResponse,
    SimulationChatRequest, SimulationChatResponse,
    GoalValidationRequest, GoalValidationResponse,
    SceneProgressRequest, SceneProgressResponse,
    UserProgressResponse, SimulationAnalyticsResponse,
    ScenarioResponse, ScenarioSceneResponse, ScenarioPersonaResponse
)
from .chat_orchestrator import ChatOrchestrator, SimulationState

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

def validate_goal_with_function_calling(
    conversation_history: str,
    scene_goal: str,
    scene_description: str,
    current_attempts: int,
    max_attempts: int,
    db: Session = None,
    user_progress_id: int = None,
    current_scene_id: int = None
) -> dict:
    """
    Use OpenAI function calling to validate if user has achieved the scene goal
    """
    import json
    
    # Define the function for scene progression
    function_definitions = [
        {
            "name": "progress_to_next_scene",
            "description": "Progress to the next scene when the user has achieved the current scene goal",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_achieved": {
                        "type": "boolean",
                        "description": "Whether the user has achieved the scene goal"
                    },
                    "confidence_score": {
                        "type": "number",
                        "description": "Confidence score from 0.0 to 1.0"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of why the goal was or wasn't achieved"
                    },
                    "next_action": {
                        "type": "string",
                        "enum": ["continue", "progress", "hint", "force_progress"],
                        "description": "What action to take next"
                    },
                    "hint_message": {
                        "type": "string",
                        "description": "Optional hint message if the user needs guidance"
                    },
                    "should_progress": {
                        "type": "boolean",
                        "description": "Whether to actually progress to the next scene in the database"
                    }
                },
                "required": ["goal_achieved", "confidence_score", "reasoning", "next_action", "should_progress"]
            }
        }
    ]
    
    # Create the evaluation prompt
    evaluation_prompt = f"""You are a goal validation agent for a business simulation. Analyze the conversation and determine if the user has achieved the scene goal.

SCENE GOAL: {scene_goal}

SCENE DESCRIPTION: {scene_description}

RECENT CONVERSATION:
{conversation_history}

CURRENT ATTEMPTS: {current_attempts}/{max_attempts}

Analyze the conversation and determine:
1. Has the user achieved the scene goal? Consider if they've gathered the necessary information, understood the situation, or completed the required tasks.
2. Confidence score (0.0-1.0) based on how clearly the goal was achieved
3. Brief reasoning for your decision
4. Next action: 
   - "continue" if they need more interaction
   - "progress" if goal is achieved and ready to move on
   - "hint" if they're stuck and need guidance
   - "force_progress" if max attempts reached
5. Optional hint message if action is "hint"
6. Should progress: Set to true if the goal is achieved and you want to actually move to the next scene

Look for indicators like:
- User saying they understand the situation
- User gathering key information from team members
- User expressing readiness to move forward
- User saying "I have everything I need" or "let's move on"
- User demonstrating comprehension of the current challenges
- User asking multiple team members about their perspectives
- User showing they understand the distribution challenges
- User summarizing what they've learned
- User saying "I think I understand" or "I got it"
- User asking to move to the next scene

CRITICAL: If the user has:
1. Interacted with multiple team members (at least 2 different personas)
2. AND either says they understand the challenges OR asks to move to the next scene
3. THEN consider the goal achieved and set should_progress to true

The user should NOT need to interact with every single team member to achieve the goal. Focus on whether they've gained sufficient understanding of the key challenges and obstacles.

Call the progress_to_next_scene function with your analysis."""

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not found in environment variables")
        
        client = openai.OpenAI(api_key=api_key)
        
        # First call to get function call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Updated to current model
            messages=[{"role": "user", "content": evaluation_prompt}],
            tools=[{"type": "function", "function": function_definitions[0]}],
            tool_choice={"type": "function", "function": {"name": "progress_to_next_scene"}},
            max_tokens=300,
            temperature=0.3
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            # Parse the tool call arguments
            tool_call = message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            
            # Check if we should actually progress to the next scene
            should_progress = arguments.get("should_progress", False)
            
            if should_progress and db and user_progress_id and current_scene_id:
                print(f"[DEBUG] Executing scene progression for user {user_progress_id}, scene {current_scene_id}")
                
                # Get user progress
                user_progress = db.query(UserProgress).filter(UserProgress.id == user_progress_id).first()
                if user_progress:
                    # Get current scene
                    current_scene = db.query(ScenarioScene).filter(ScenarioScene.id == current_scene_id).first()
                    if current_scene:
                        # Find next scene
                        next_scene = db.query(ScenarioScene).filter(
                            and_(
                                ScenarioScene.scenario_id == user_progress.scenario_id,
                                ScenarioScene.scene_order > current_scene.scene_order
                            )
                        ).order_by(ScenarioScene.scene_order).first()
                        
                        if next_scene:
                            # Update user progress to next scene
                            user_progress.current_scene_id = next_scene.id
                            user_progress.last_activity = datetime.utcnow()
                            
                            # Mark current scene as completed
                            completed_scenes = user_progress.scenes_completed or []
                            if current_scene_id not in completed_scenes:
                                completed_scenes.append(current_scene_id)
                                user_progress.scenes_completed = completed_scenes
                            
                            # Update scene progress
                            scene_progress = db.query(SceneProgress).filter(
                                and_(
                                    SceneProgress.user_progress_id == user_progress_id,
                                    SceneProgress.scene_id == current_scene_id
                                )
                            ).first()
                            
                            if scene_progress:
                                scene_progress.status = "completed"
                                scene_progress.goal_achieved = True
                                scene_progress.completed_at = datetime.utcnow()
                            
                            # Create scene progress for next scene
                            next_scene_progress = SceneProgress(
                                user_progress_id=user_progress_id,
                                scene_id=next_scene.id,
                                status="in_progress",
                                started_at=datetime.utcnow()
                            )
                            db.add(next_scene_progress)
                            
                            # Commit the changes
                            db.commit()
                            print(f"[DEBUG] Successfully progressed to scene {next_scene.id}")
                            
                            # Add progression info to result
                            arguments["next_scene_id"] = next_scene.id
                            arguments["next_scene_title"] = next_scene.title
                        else:
                            # No more scenes - simulation complete
                            user_progress.simulation_status = "completed"
                            user_progress.completed_at = datetime.utcnow()
                            db.commit()
                            print(f"[DEBUG] Simulation completed")
                            arguments["simulation_complete"] = True
            
            # Return the parsed result
            return {
                "goal_achieved": arguments.get("goal_achieved", False),
                "confidence_score": arguments.get("confidence_score", 0.0),
                "reasoning": arguments.get("reasoning", ""),
                "next_action": arguments.get("next_action", "continue"),
                "hint_message": arguments.get("hint_message"),
                "next_scene_id": arguments.get("next_scene_id"),
                "next_scene_title": arguments.get("next_scene_title"),
                "simulation_complete": arguments.get("simulation_complete", False)
            }
        else:
            # Fallback if no function call
            return {
                "goal_achieved": False,
                "confidence_score": 0.0,
                "reasoning": "No function call made",
                "next_action": "continue",
                "hint_message": None
            }
            
    except Exception as e:
        print(f"[ERROR] Goal validation failed: {str(e)}")
        return {
            "goal_achieved": False,
            "confidence_score": 0.0,
            "reasoning": f"Error during validation: {str(e)}",
            "next_action": "continue",
            "hint_message": None
        }

@router.post("/start", response_model=SimulationStartResponse)
async def start_simulation(
    request: SimulationStartRequest,
    db: Session = Depends(get_db)
):
    """Start a new simulation or resume existing one"""
    
    # Verify scenario exists
    scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Get first scene in order
    first_scene = db.query(ScenarioScene).filter(
        ScenarioScene.scenario_id == request.scenario_id
    ).order_by(ScenarioScene.scene_order).first()
    
    if not first_scene:
        raise HTTPException(status_code=400, detail="Scenario has no scenes")
    
    # Check for existing progress
    existing_progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == request.user_id,
            UserProgress.scenario_id == request.scenario_id,
            UserProgress.simulation_status.in_(["not_started", "in_progress"])
        )
    ).first()
    
    if existing_progress:
        # Resume existing simulation
        user_progress = existing_progress
        user_progress.session_count += 1
        user_progress.last_activity = datetime.utcnow()
        
        # Get current scene
        if user_progress.current_scene_id:
            current_scene = db.query(ScenarioScene).filter(
                ScenarioScene.id == user_progress.current_scene_id
            ).first()
        else:
            current_scene = first_scene
            user_progress.current_scene_id = first_scene.id
            user_progress.simulation_status = "in_progress"
    else:
        # Get all scenes and personas for orchestrator setup
        all_scenes = db.query(ScenarioScene).filter(
            ScenarioScene.scenario_id == scenario.id
        ).order_by(ScenarioScene.scene_order).all()
        
        all_personas = db.query(ScenarioPersona).filter(
            ScenarioPersona.scenario_id == scenario.id
        ).all()
        
        # Prepare scenario data for orchestrator
        scenario_data = {
            "id": scenario.id,
            "title": scenario.title,
            "description": scenario.description,
            "challenge": scenario.challenge,
            "scenes": [
                {
                    "id": scene.id,
                    "title": scene.title,
                    "description": scene.description,
                    "objectives": [scene.user_goal] if scene.user_goal else ["Complete the scene interaction"],
                    "image_url": scene.image_url,
                    "agent_ids": [p.name.lower().replace(" ", "_") for p in all_personas],  # All personas available
                    "max_turns": scene.timeout_turns if scene.timeout_turns is not None else 15,
                    "success_criteria": f"User achieves: {scene.user_goal or 'scene completion'}"
                }
                for scene in all_scenes
            ],
            "personas": [
                {
                    "id": persona.name.lower().replace(" ", "_"),
                    "identity": {
                        "name": persona.name,
                        "role": persona.role,
                        "bio": persona.background or "Professional team member"
                    },
                    "personality": {
                        "goals": persona.primary_goals or ["Support team objectives"],
                                                 "traits": persona.personality_traits or "Professional and collaborative"
                    }
                }
                for persona in all_personas
            ]
        }
        
        # Create new progress record with orchestrator state
        user_progress = UserProgress(
            user_id=request.user_id,
            scenario_id=request.scenario_id,
            current_scene_id=first_scene.id,
            simulation_status="waiting_for_begin",  # Changed from "in_progress"
            session_count=1,
            scenes_completed=[],
            orchestrator_data=scenario_data,  # Store orchestrator data
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        db.add(user_progress)
        db.flush()  # Get ID
        
        # Create scene progress for first scene
        scene_progress = SceneProgress(
            user_progress_id=user_progress.id,
            scene_id=first_scene.id,
            status="in_progress",
            started_at=datetime.utcnow()
        )
        db.add(scene_progress)
        current_scene = first_scene
    
    db.commit()
    
    # Prepare response data
    # Ensure learning_objectives is always a list
    learning_objectives = scenario.learning_objectives
    if isinstance(learning_objectives, str):
        learning_objectives = [learning_objectives]
    elif learning_objectives is None:
        learning_objectives = []
    scenario_data = SimulationScenarioResponse(
        id=scenario.id,
        title=scenario.title,
        description=scenario.description,
        challenge=scenario.challenge,
        industry=scenario.industry,
        learning_objectives=learning_objectives,
        student_role=scenario.student_role
    )
    
    # Get all personas for the scenario (not just scene-specific ones)
    main_character_name = (scenario.student_role or '').strip().lower()
    scene_personas = db.query(ScenarioPersona).filter(
        ScenarioPersona.scenario_id == scenario.id
    ).all()

    personas_data = [
        ScenarioPersonaResponse(
            id=persona.id,
            scenario_id=persona.scenario_id,
            name=persona.name,
            role=persona.role,
            background=persona.background,
            correlation=persona.correlation,
            primary_goals=(
                [persona.primary_goals] if isinstance(persona.primary_goals, str) and persona.primary_goals else
                persona.primary_goals if isinstance(persona.primary_goals, list) else []
            ),
            personality_traits=persona.personality_traits or {},
            created_at=persona.created_at,
            updated_at=persona.updated_at
        ) for persona in scene_personas
        if persona.name.strip().lower() != main_character_name
    ]
    
    scene_data = ScenarioSceneResponse(
        id=current_scene.id,
        scenario_id=current_scene.scenario_id,
        title=current_scene.title,
        description=current_scene.description,
        user_goal=current_scene.user_goal,
        scene_order=current_scene.scene_order,
        estimated_duration=current_scene.estimated_duration,
        image_url=current_scene.image_url,
        image_prompt=current_scene.image_prompt,
        timeout_turns=current_scene.timeout_turns,  # Ensure this is included
        success_metric=current_scene.success_metric,  # Ensure this is included
        created_at=current_scene.created_at,
        updated_at=current_scene.updated_at,
        personas=personas_data
    )
    
    return SimulationStartResponse(
        user_progress_id=user_progress.id,
        scenario=scenario_data,
        current_scene=scene_data,
        simulation_status=user_progress.simulation_status
    )

@router.post("/chat", response_model=SimulationChatResponse)
async def chat_with_persona(
    request: SimulationChatRequest,
    db: Session = Depends(get_db)
):
    """Send message to AI persona and get response"""
    
    start_time = time.time()
    
    # Get user progress and validate
    user_progress = db.query(UserProgress).filter(
        UserProgress.id == request.user_progress_id
    ).first()
    
    if not user_progress:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    # Get scene and personas
    scene = db.query(ScenarioScene).filter(
        ScenarioScene.id == request.scene_id
    ).first()
    
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get all personas for the scenario
    scene_personas = db.query(ScenarioPersona).filter(
        ScenarioPersona.scenario_id == scene.scenario_id
    ).all()
    
    if not scene_personas:
        raise HTTPException(status_code=400, detail="No personas found for scene")
    
    # Determine target persona
    if request.target_persona_id:
        target_persona = next((p for p in scene_personas if p.id == request.target_persona_id), None)
        if not target_persona:
            raise HTTPException(status_code=400, detail="Target persona not found in scene")
    else:
        # Use first persona if none specified
        target_persona = scene_personas[0]
    
    # Get recent conversation context
    recent_messages = db.query(ConversationLog).filter(
        and_(
            ConversationLog.user_progress_id == request.user_progress_id,
            ConversationLog.scene_id == request.scene_id
        )
    ).order_by(desc(ConversationLog.message_order)).limit(10).all()
    
    # Get current attempt number
    scene_progress = db.query(SceneProgress).filter(
        and_(
            SceneProgress.user_progress_id == request.user_progress_id,
            SceneProgress.scene_id == request.scene_id
        )
    ).first()
    
    current_attempt = scene_progress.attempts if scene_progress else 1
    
    # Get next message order
    last_message = db.query(ConversationLog).filter(
        and_(
            ConversationLog.user_progress_id == request.user_progress_id,
            ConversationLog.scene_id == request.scene_id
        )
    ).order_by(desc(ConversationLog.message_order)).first()
    
    next_message_order = (last_message.message_order + 1) if last_message else 1
    
    # Log user message
    user_log = ConversationLog(
        user_progress_id=request.user_progress_id,
        scene_id=request.scene_id,
        message_type="user",
        sender_name="User",
        message_content=request.message,
        message_order=next_message_order,
        attempt_number=current_attempt,
        timestamp=datetime.utcnow()
    )
    db.add(user_log)
    db.flush()
    
    # Build AI context
    conversation_context = []
    for msg in reversed(recent_messages[-6:]):  # Last 6 messages for context
        role = "user" if msg.message_type == "user" else "assistant"
        conversation_context.append({
            "role": role,
            "content": msg.message_content
        })
    
    # Add current user message
    conversation_context.append({
        "role": "user",
        "content": request.message
    })
    
    # Create AI prompt with persona and scene context
    system_prompt = f"""You are {target_persona.name}, a {target_persona.role} in this business simulation.

PERSONA BACKGROUND:
{target_persona.background}

PERSONA CORRELATION TO CASE:
{target_persona.correlation}

PERSONALITY TRAITS: {json.dumps(target_persona.personality_traits)}

SCENE CONTEXT:
Title: {scene.title}
Description: {scene.description}
User Goal: {scene.user_goal}

SIMULATION INSTRUCTIONS:
- Stay in character as {target_persona.name}
- Respond naturally based on your role and personality
- Help guide the user toward the scene goal through realistic business interaction
- Don't directly give away answers, but provide realistic business insights
- Keep responses concise and professional
- If the user seems stuck, provide subtle hints through natural conversation
"""
    
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt}
            ] + conversation_context,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        processing_time = time.time() - start_time
        
        # Log AI response
        ai_log = ConversationLog(
            user_progress_id=request.user_progress_id,
            scene_id=request.scene_id,
            message_type="ai_persona",
            sender_name=target_persona.name,
            persona_id=target_persona.id,
            message_content=ai_response,
            message_order=next_message_order + 1,
            attempt_number=current_attempt,
            ai_model_version="gpt-4o",
            processing_time=processing_time,
            timestamp=datetime.utcnow()
        )
        db.add(ai_log)
        
        # Update scene progress
        if scene_progress:
            scene_progress.messages_sent += 1
            scene_progress.ai_responses += 1
        else:
            scene_progress = SceneProgress(
                user_progress_id=request.user_progress_id,
                scene_id=request.scene_id,
                status="in_progress",
                messages_sent=1,
                ai_responses=1,
                attempts=1,
                started_at=datetime.utcnow()
            )
            db.add(scene_progress)
        
        # Update user progress
        user_progress.last_activity = datetime.utcnow()
        
        db.commit()
        
        return SimulationChatResponse(
            message_id=ai_log.id,
            persona_name=target_persona.name,
            persona_response=ai_response,
            message_order=next_message_order + 1,
            processing_time=processing_time,
            ai_model_version="gpt-4o"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}"
        )

@router.post("/validate-goal", response_model=GoalValidationResponse)
async def validate_scene_goal(
    request: GoalValidationRequest,
    db: Session = Depends(get_db)
):
    """Check if user has achieved the scene goal"""
    
    # Get user progress and scene
    user_progress = db.query(UserProgress).filter(
        UserProgress.id == request.user_progress_id
    ).first()
    
    if not user_progress:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    scene = db.query(ScenarioScene).filter(
        ScenarioScene.id == request.scene_id
    ).first()
    
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get recent conversation
    recent_messages = db.query(ConversationLog).filter(
        and_(
            ConversationLog.user_progress_id == request.user_progress_id,
            ConversationLog.scene_id == request.scene_id
        )
    ).order_by(desc(ConversationLog.message_order)).limit(10).all()
    
    if not recent_messages:
        return GoalValidationResponse(
            goal_achieved=False,
            confidence_score=0.0,
            reasoning="No conversation yet",
            next_action="continue"
        )
    
    # Build conversation summary for AI evaluation
    conversation_summary = []
    for msg in reversed(recent_messages):
        speaker = msg.sender_name or "System"
        conversation_summary.append(f"{speaker}: {msg.message_content}")
    
    conversation_text = "\n".join(conversation_summary)
    
    # Get scene progress for attempt tracking
    scene_progress = db.query(SceneProgress).filter(
        and_(
            SceneProgress.user_progress_id == request.user_progress_id,
            SceneProgress.scene_id == request.scene_id
        )
    ).first()
    
    current_attempts = scene_progress.attempts if scene_progress else 0
    max_attempts = scene.max_attempts or 5
    
    # AI evaluation prompt
    goal_for_validation = scene.success_metric or scene.user_goal
    evaluation_prompt = f"""Evaluate whether the user has achieved the scene goal based on the conversation.

SCENE GOAL: {goal_for_validation}

SCENE DESCRIPTION: {scene.description}

RECENT CONVERSATION:
{conversation_text}

CURRENT ATTEMPTS: {current_attempts}/{max_attempts}

Analyze the conversation and determine:
1. Has the user achieved the scene goal? (true/false)
2. Confidence score (0.0-1.0) 
3. Brief reasoning for your decision
4. Next recommended action: "continue", "progress", "hint", or "force_progress"
5. If action is "hint", provide a helpful hint message

Respond in JSON format:
{{
    "goal_achieved": boolean,
    "confidence_score": float,
    "reasoning": "string",
    "next_action": "string",
    "hint_message": "string or null"
}}
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": evaluation_prompt}],
            max_tokens=300,
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Update scene progress if goal achieved
        if result["goal_achieved"] and scene_progress:
            scene_progress.goal_achieved = True
            scene_progress.goal_achievement_score = result["confidence_score"] * 100
            
            # Mark conversation that led to progress
            if recent_messages:
                recent_messages[0].led_to_progress = True
        
        # Check if we should force progression
        if current_attempts >= max_attempts and not result["goal_achieved"]:
            result["next_action"] = "force_progress"
            result["hint_message"] = f"You've reached the maximum attempts ({max_attempts}). Let's move to the next scene with a summary."
        
        db.commit()
        
        return GoalValidationResponse(
            goal_achieved=result["goal_achieved"],
            confidence_score=result["confidence_score"],
            reasoning=result["reasoning"],
            next_action=result["next_action"],
            hint_message=result.get("hint_message")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Goal validation failed: {str(e)}"
        )

@router.post("/progress", response_model=SceneProgressResponse)
async def progress_to_next_scene(
    request: SceneProgressRequest,
    db: Session = Depends(get_db)
):
    """Move user to the next scene in the simulation"""
    
    # Get user progress
    user_progress = db.query(UserProgress).filter(
        UserProgress.id == request.user_progress_id
    ).first()
    
    if not user_progress:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    # Get current scene
    current_scene = db.query(ScenarioScene).filter(
        ScenarioScene.id == request.current_scene_id
    ).first()
    
    if not current_scene:
        raise HTTPException(status_code=404, detail="Current scene not found")
    
    # Update scene progress
    scene_progress = db.query(SceneProgress).filter(
        and_(
            SceneProgress.user_progress_id == request.user_progress_id,
            SceneProgress.scene_id == request.current_scene_id
        )
    ).first()
    
    if scene_progress:
        scene_progress.status = "completed"
        scene_progress.goal_achieved = request.goal_achieved
        scene_progress.forced_progression = request.forced_progression
        scene_progress.completed_at = datetime.utcnow()
        
        if request.forced_progression:
            user_progress.forced_progressions += 1
    
    # Update user progress - add completed scene
    completed_scenes = user_progress.scenes_completed or []
    if request.current_scene_id not in completed_scenes:
        completed_scenes.append(request.current_scene_id)
        user_progress.scenes_completed = completed_scenes
    
    # Find next scene
    next_scene = db.query(ScenarioScene).filter(
        and_(
            ScenarioScene.scenario_id == user_progress.scenario_id,
            ScenarioScene.scene_order > current_scene.scene_order
        )
    ).order_by(ScenarioScene.scene_order).first()
    
    if next_scene:
        # Move to next scene
        user_progress.current_scene_id = next_scene.id
        user_progress.last_activity = datetime.utcnow()
        
        # Create scene progress for next scene
        next_scene_progress = SceneProgress(
            user_progress_id=request.user_progress_id,
            scene_id=next_scene.id,
            status="in_progress",
            started_at=datetime.utcnow()
        )
        db.add(next_scene_progress)
        
        # Get all personas for the scenario
        scene_personas = db.query(ScenarioPersona).filter(
            ScenarioPersona.scenario_id == user_progress.scenario_id
        ).all()
        
        personas_data = [
            ScenarioPersonaResponse(
                id=persona.id,
                scenario_id=persona.scenario_id,
                name=persona.name,
                role=persona.role,
                background=persona.background,
                correlation=persona.correlation,
                primary_goals=persona.primary_goals or [],
                personality_traits=persona.personality_traits or {},
                created_at=persona.created_at,
                updated_at=persona.updated_at
            ) for persona in scene_personas
        ]
        
        next_scene_data = ScenarioSceneResponse(
            id=next_scene.id,
            scenario_id=next_scene.scenario_id,
            title=next_scene.title,
            description=next_scene.description,
            user_goal=next_scene.user_goal,
            scene_order=next_scene.scene_order,
            estimated_duration=next_scene.estimated_duration,
            image_url=next_scene.image_url,
            image_prompt=next_scene.image_prompt,
            timeout_turns=next_scene.timeout_turns,  # Ensure this is included
            success_metric=next_scene.success_metric,  # Ensure this is included
            created_at=next_scene.created_at,
            updated_at=next_scene.updated_at,
            personas=personas_data
        )
        
        db.commit()
        
        return SceneProgressResponse(
            success=True,
            next_scene=next_scene_data,
            simulation_complete=False
        )
    else:
        # Simulation complete
        user_progress.simulation_status = "completed"
        user_progress.completed_at = datetime.utcnow()
        user_progress.completion_percentage = 100.0
        
        # Calculate final score (simple average of scene scores)
        all_scene_progress = db.query(SceneProgress).filter(
            SceneProgress.user_progress_id == request.user_progress_id
        ).all()
        
        if all_scene_progress:
            scores = [sp.goal_achievement_score for sp in all_scene_progress if sp.goal_achievement_score]
            if scores:
                user_progress.final_score = sum(scores) / len(scores)
        
        db.commit()
        
        return SceneProgressResponse(
            success=True,
            simulation_complete=True,
            completion_summary="Congratulations! You have completed the simulation."
        )

@router.get("/progress/{user_progress_id}", response_model=UserProgressResponse)
async def get_user_progress(
    user_progress_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed user progress for a simulation"""
    
    user_progress = db.query(UserProgress).filter(
        UserProgress.id == user_progress_id
    ).first()
    
    if not user_progress:
        raise HTTPException(status_code=404, detail="User progress not found")
    
    return UserProgressResponse(
        id=user_progress.id,
        user_id=user_progress.user_id,
        scenario_id=user_progress.scenario_id,
        current_scene_id=user_progress.current_scene_id,
        simulation_status=user_progress.simulation_status,
        scenes_completed=user_progress.scenes_completed or [],
        total_attempts=user_progress.total_attempts,
        hints_used=user_progress.hints_used,
        forced_progressions=user_progress.forced_progressions,
        completion_percentage=user_progress.completion_percentage,
        total_time_spent=user_progress.total_time_spent,
        session_count=user_progress.session_count,
        final_score=user_progress.final_score,
        started_at=user_progress.started_at,
        completed_at=user_progress.completed_at,
        last_activity=user_progress.last_activity
    ) 

@router.get("/scenes/{scene_id}", response_model=ScenarioSceneResponse)
async def get_scene_by_id(
    scene_id: int,
    db: Session = Depends(get_db)
):
    """Get scene data by ID"""
    
    scene = db.query(ScenarioScene).filter(ScenarioScene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get personas for this scene
    scene_personas = db.query(ScenarioPersona).filter(
        ScenarioPersona.scenario_id == scene.scenario_id
    ).all()
    
    personas_data = [
        ScenarioPersonaResponse(
            id=persona.id,
            scenario_id=persona.scenario_id,
            name=persona.name,
            role=persona.role,
            background=persona.background,
            correlation=persona.correlation,
            primary_goals=(
                [persona.primary_goals] if isinstance(persona.primary_goals, str) and persona.primary_goals else
                persona.primary_goals if isinstance(persona.primary_goals, list) else []
            ),
            personality_traits=persona.personality_traits or {},
            created_at=persona.created_at,
            updated_at=persona.updated_at
        ) for persona in scene_personas
    ]
    
    return ScenarioSceneResponse(
        id=scene.id,
        scenario_id=scene.scenario_id,
        title=scene.title,
        description=scene.description,
        user_goal=scene.user_goal,
        scene_order=scene.scene_order,
        estimated_duration=scene.estimated_duration,
        image_url=scene.image_url,
        image_prompt=scene.image_prompt,
        timeout_turns=scene.timeout_turns,  # Ensure this is included
        success_metric=scene.success_metric,  # Ensure this is included
        created_at=scene.created_at,
        updated_at=scene.updated_at,
        personas=personas_data
    )

@router.post("/linear-chat", response_model=SimulationChatResponse)
async def linear_simulation_chat(
    request: SimulationChatRequest,
    db: Session = Depends(get_db)
):
    """Handle orchestrated chat interactions in linear simulation"""
    try:
        # Get user progress - handle both old and new request formats
        if request.user_progress_id:
            user_progress = db.query(UserProgress).filter(
                UserProgress.id == request.user_progress_id
            ).first()
        else:
            user_progress = db.query(UserProgress).filter(
                UserProgress.user_id == request.user_id,
                UserProgress.scenario_id == request.scenario_id
            ).first()
        
        if not user_progress:
            raise HTTPException(status_code=404, detail="No active simulation found")
        
        if not user_progress.orchestrator_data:
            raise HTTPException(status_code=400, detail="Simulation not properly initialized")
        
        # Initialize orchestrator with stored data
        orchestrator = ChatOrchestrator(user_progress.orchestrator_data)
        
        # Load saved state if it exists
        if user_progress.orchestrator_data and 'state' in user_progress.orchestrator_data:
            saved_state = user_progress.orchestrator_data['state']
            orchestrator.state.simulation_started = saved_state.get('simulation_started', False)
            orchestrator.state.user_ready = saved_state.get('user_ready', False)
            orchestrator.state.current_scene_index = saved_state.get('current_scene_index', 0)
            orchestrator.state.turn_count = saved_state.get('turn_count', 0)
            orchestrator.state.state_variables = saved_state.get('state_variables', {})
            print(f"[DEBUG] Loaded state - simulation_started: {orchestrator.state.simulation_started}")
        else:
            print(f"[DEBUG] No saved state found. orchestrator_data keys: {list(user_progress.orchestrator_data.keys()) if user_progress.orchestrator_data else 'None'}")
        
        # Handle "begin" command to start simulation
        if request.message.lower().strip() == "begin":
            if orchestrator.state.simulation_started:
                ai_response = "The simulation has already begun. You can now interact with team members using @mentions (e.g., @rahul_ashok) or ask for help."
                persona_name = "ChatOrchestrator"
                persona_id = None
            else:
                # Start simulation
                orchestrator.state.simulation_started = True
                orchestrator.state.user_ready = True
                user_progress.simulation_status = "in_progress"
                
                # Don't overwrite orchestrator_data, just update the state
                # user_progress.orchestrator_data already contains the scenario data
                
                # Save the updated state immediately
                state_dict = {
                    'current_scene_id': orchestrator.state.current_scene_id,
                    'current_scene_index': orchestrator.state.current_scene_index,
                    'turn_count': orchestrator.state.turn_count,
                    'simulation_started': orchestrator.state.simulation_started,
                    'user_ready': orchestrator.state.user_ready,
                    'state_variables': orchestrator.state.state_variables
                }
                
                if user_progress.orchestrator_data:
                    user_progress.orchestrator_data['state'] = state_dict
                else:
                    user_progress.orchestrator_data = {'state': state_dict}
                
                # Mark the JSON field as modified so SQLAlchemy will update it
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(user_progress, "orchestrator_data")
                
                # Commit the state change immediately
                db.commit()
                print(f"[DEBUG] Saved state after begin - simulation_started: {state_dict['simulation_started']}")
                
                # Generate cinematic prologue
                scenario = user_progress.orchestrator_data
                prologue = f"""# {scenario['title']}

{scenario['description']}

**Challenge:** {scenario['challenge']}

You are about to enter a multi-scene simulation where you'll interact with various team members to achieve specific objectives. Each scene has its own goals and participants.

**Available Agents:**
"""
                for persona in scenario['personas']:
                    name = persona['identity']['name']
                    role = persona['identity']['role']
                    bio = persona['identity']['bio']
                    prologue += f"• @{persona['id']}: {name} ({role}) - {bio}\n"
                
                prologue += f"""
**Instructions:** Use @mentions to speak with specific agents (e.g., @{scenario['personas'][0]['id']}). Type 'help' for assistance.

{orchestrator.generate_scene_introduction()}

*The simulation begins now...*
"""
                ai_response = prologue
                persona_name = "ChatOrchestrator"
                persona_id = None
        
        elif request.message.lower().strip() == "help":
            ai_response = f"""**Help - Simulation Commands**

**@mention syntax:** Use @agent_id to speak with specific agents
**Current Goal:** {orchestrator._get_current_scene_goal()}
**Turns Remaining:** {orchestrator._get_turns_remaining()}

**Available Commands:**
• help - Show this help
• begin - Start the simulation (if not started)

**Current Scene:** Scene {orchestrator.state.current_scene_index + 1} of {len(orchestrator.scenes)}
"""
            persona_name = "ChatOrchestrator"
            persona_id = None
        
        else:
            # Regular chat interaction
            if not orchestrator.state.simulation_started:
                ai_response = """Welcome to the simulation! 

Please type **"begin"** when you're ready to start, or **"help"** for more information."""
                persona_name = "ChatOrchestrator"
                persona_id = None
            else:
                # Check if user is addressing a specific persona with @mention
                import re
                mention_match = re.search(r'@(\w+)', request.message)
                
                print(f"[DEBUG] User message: {request.message}")
                print(f"[DEBUG] Simulation started: {orchestrator.state.simulation_started}")
                print(f"[DEBUG] Mention match: {mention_match.group(1) if mention_match else None}")
                
                if mention_match:
                    # User is addressing a specific persona
                    persona_id = mention_match.group(1)
                    
                    # Find the persona in the scenario data with fuzzy matching
                    target_persona = None
                    available_personas = [p['id'] for p in orchestrator.scenario.get('personas', [])]
                    print(f"[DEBUG] Looking for persona: {persona_id}")
                    print(f"[DEBUG] Available personas: {available_personas}")
                    
                    # Create a mapping of name variations to persona IDs
                    name_mapping = {}
                    for persona in orchestrator.scenario.get('personas', []):
                        name = persona['identity']['name'].lower()
                        # Add various name variations
                        name_mapping[name] = persona['id']
                        name_mapping[name.replace("'", "").replace(" ", "_")] = persona['id']
                        name_mapping[name.replace("'", "").replace(" ", "")] = persona['id']
                        # Add first name only
                        first_name = name.split()[0]
                        name_mapping[first_name] = persona['id']
                        name_mapping[first_name.replace("'", "")] = persona['id']
                    
                    print(f"[DEBUG] Name mapping: {name_mapping}")
                    
                    # Try to find the persona by name
                    search_name = persona_id.lower()
                    if search_name in name_mapping:
                        persona_id = name_mapping[search_name]
                        target_persona = next((p for p in orchestrator.scenario.get('personas', []) if p['id'] == persona_id), None)
                    else:
                        # Try fuzzy matching
                        for name, pid in name_mapping.items():
                            if (search_name in name or name in search_name or
                                search_name.replace("'", "").replace("_", "") in name.replace("'", "").replace("_", "")):
                                persona_id = pid
                                target_persona = next((p for p in orchestrator.scenario.get('personas', []) if p['id'] == persona_id), None)
                                break
                    
                    if target_persona:
                        # Create a more focused system prompt for persona interaction
                        system_prompt = f"""You are {target_persona['identity']['name']}, a {target_persona['identity']['role']} in this business simulation.

PERSONA BACKGROUND: {target_persona['identity']['bio']}

CURRENT SCENE: {orchestrator.scenario.get('scenes', [{}])[orchestrator.state.current_scene_index].get('title', '...')} - {orchestrator.scenario.get('scenes', [{}])[orchestrator.state.current_scene_index].get('description', '...')}

SCENARIO CONTEXT: {orchestrator.scenario.get('description', '')}

PERSONALITY: {target_persona.get('personality', {})}

You are in a meeting about {orchestrator.scenario.get('title', '...')} to address the challenges of {orchestrator.scenario.get('challenge', '')}. Respond as {target_persona['identity']['name']} would, providing information and insights relevant to your role and the current challenges. Be professional and provide specific insights about the distribution network, kiosks, or your role in the business.

This is about {orchestrator.scenario.get('title', '...')} and its challenges, NOT about any other company or system.

User's message: {request.message}"""
                        persona_name = target_persona['identity']['name']
                    else:
                        # Fallback to orchestrator
                        system_prompt = f"""You are the ChatOrchestrator managing a business simulation about {orchestrator.scenario.get('title', '...')}.

Available personas: {', '.join([p['id'] for p in orchestrator.scenario.get('personas', [])])}

Gently redirect them to use a valid persona mention or provide general guidance."""
                        persona_name = "ChatOrchestrator"
                        persona_id = None
                else:
                    # General orchestrator response
                    system_prompt = f"""You are the ChatOrchestrator for a business simulation about {orchestrator.scenario.get('title', '...')}.

CURRENT SCENE: {orchestrator.scenario.get('scenes', [{}])[orchestrator.state.current_scene_index].get('title', '...')}
OBJECTIVE: {orchestrator.scenario.get('scenes', [{}])[orchestrator.state.current_scene_index].get('objectives', ['...'])[0]}

The user can:
- Use @mentions to talk to specific team members (e.g., {', '.join([p['id'] for p in orchestrator.scenario.get('personas', [])])})
- Ask general questions about the situation
- Request help or guidance

This is about {orchestrator.scenario.get('title', '...')} and its challenges, NOT about any other company or system.

Respond helpfully and guide them toward productive interactions with the team members. If they ask about previous conversations, remind them that you can only see the current message and suggest they ask the specific person again.

User's message: {request.message}"""
                    persona_name = "ChatOrchestrator"
                    persona_id = None
                
                # Make OpenAI API call
                import openai
                import os
                
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.message}
                    ],
                    max_tokens=600,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
        
        # Check for goal completion and scene progression using AI function calling
        scene_completed = False
        next_scene_id = None
        
        # Only check goal completion if simulation is started and not a system command
        if (orchestrator.state.simulation_started and 
            request.message.lower().strip() not in ["begin", "help"]):
            
            # Get current scene goal
            current_scene = orchestrator.scenes[orchestrator.state.current_scene_index] if orchestrator.scenes else None
            if current_scene and current_scene.get('objectives'):
                scene_goal = current_scene['objectives'][0]
                scene_description = current_scene.get('description', '')
                
                # Get recent conversation for context - include the current message
                scene_id_to_use = request.scene_id if request.scene_id is not None else user_progress.current_scene_id
                recent_messages = db.query(ConversationLog).filter(
                    and_(
                        ConversationLog.user_progress_id == user_progress.id,
                        ConversationLog.scene_id == scene_id_to_use
                    )
                ).order_by(desc(ConversationLog.message_order)).limit(10).all()
                
                # Build conversation history
                conversation_history = []
                for msg in reversed(recent_messages):
                    speaker = msg.sender_name or "System"
                    conversation_history.append(f"{speaker}: {msg.message_content}")
                
                # Add the current user message
                conversation_history.append(f"User: {request.message}")
                
                conversation_text = "\n".join(conversation_history)
                print(f"[DEBUG] Conversation history: {conversation_text[:500]}...")
                
                # Get current attempts
                scene_progress = db.query(SceneProgress).filter(
                    and_(
                        SceneProgress.user_progress_id == user_progress.id,
                        SceneProgress.scene_id == scene_id_to_use
                    )
                ).first()
                
                current_attempts = scene_progress.attempts if scene_progress else 0
                max_attempts = current_scene.get('max_attempts', 5)
                print(f"[DEBUG] Current attempts: {current_attempts}/{max_attempts}")
                
                # Use AI function calling to validate goal
                try:
                    validation_result = validate_goal_with_function_calling(
                        conversation_history=conversation_text,
                        scene_goal=scene_goal,
                        scene_description=scene_description,
                        current_attempts=current_attempts,
                        max_attempts=max_attempts,
                        db=db,
                        user_progress_id=user_progress.id,
                        current_scene_id=scene_id_to_use
                    )
                    
                    print(f"[DEBUG] Goal validation result: {validation_result}")
                except Exception as e:
                    print(f"[ERROR] Goal validation failed: {str(e)}")
                    # Fallback to simple validation
                    validation_result = {
                        "goal_achieved": False,
                        "confidence_score": 0.0,
                        "reasoning": f"Error during validation: {str(e)}",
                        "next_action": "continue",
                        "hint_message": None,
                        "next_scene_id": None,
                        "next_scene_title": None,
                        "simulation_complete": False
                    }
                
                # Handle the validation result
                if validation_result.get("next_scene_id") or validation_result.get("simulation_complete"):
                    # Scene progression was triggered by the AI function call
                    scene_completed = True
                    next_scene_id = validation_result.get("next_scene_id")
                    
                    if validation_result.get("simulation_complete"):
                        ai_response += "\n\n🎉 **Congratulations! You have completed the entire simulation.**"
                    elif validation_result.get("next_scene_title"):
                        ai_response += f"\n\n🎉 **Scene Completed!** Moving to next scene:\n\n**{validation_result['next_scene_title']}**\n\n**Objective:** Continue working with the team to address the challenges of {orchestrator.scenario.get('title', '...')}."
                    
                    # Update orchestrator state to match database
                    if next_scene_id:
                        # Find the scene index for the new scene
                        for i, scene in enumerate(orchestrator.scenes):
                            if scene.get('id') == next_scene_id:
                                orchestrator.state.current_scene_index = i
                                break
                        orchestrator.state.turn_count = 0
                        orchestrator.state.scene_completed = False
                        orchestrator.state.current_scene_id = next_scene_id
                
                elif validation_result["next_action"] == "hint" and validation_result["hint_message"]:
                    # Add hint to response
                    ai_response += f"\n\n💡 **Hint:** {validation_result['hint_message']}"
                
                elif validation_result["next_action"] == "force_progress":
                    # Force progression due to max attempts - handled by the function call now
                    pass
        
        # Update orchestrator state in database
        user_progress.last_activity = datetime.utcnow()
        
        # Save updated orchestrator state - ALWAYS save the state
        state_dict = {
            'current_scene_id': orchestrator.state.current_scene_id,
            'current_scene_index': orchestrator.state.current_scene_index,
            'turn_count': orchestrator.state.turn_count,
            'simulation_started': orchestrator.state.simulation_started,
            'user_ready': orchestrator.state.user_ready,
            'state_variables': orchestrator.state.state_variables
        }
        
        # Ensure orchestrator_data exists and update state
        if not user_progress.orchestrator_data:
            user_progress.orchestrator_data = {}
        
        # Always update the state - Force SQLAlchemy to detect JSON change
        user_progress.orchestrator_data['state'] = state_dict
        # Mark the JSON field as modified so SQLAlchemy will update it
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user_progress, "orchestrator_data")
        print(f"[DEBUG] Saving state at end - simulation_started: {state_dict['simulation_started']}")
        
        # Log conversation with persona information
        conversation_log = ConversationLog(
            user_progress_id=user_progress.id,
            scene_id=request.scene_id or user_progress.current_scene_id,
            message_type="ai_persona" if persona_name != "ChatOrchestrator" else "orchestrator",
            sender_name=persona_name,
            persona_id=persona_id,  # This will be None for orchestrator messages
            message_content=f"User: {request.message}\n\n{persona_name}: {ai_response}",
            message_order=1,  # Simplified for now
            timestamp=datetime.utcnow()
        )
        db.add(conversation_log)
        
        # Commit everything including the state update
        db.commit()
        print(f"[DEBUG] Final commit - simulation_started: {state_dict['simulation_started']}")
        
        return SimulationChatResponse(
            message=ai_response,
            scene_id=request.scene_id or user_progress.current_scene_id,
            scene_completed=scene_completed,
            next_scene_id=next_scene_id,
            persona_name=persona_name,
            persona_id=persona_id
        )
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Linear simulation chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}") 