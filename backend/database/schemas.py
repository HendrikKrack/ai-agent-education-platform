# Enhanced Pydantic Schemas for CrewAI Agent Builder Platform
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- SCENARIO SCHEMAS ---
class ScenarioCreate(BaseModel):
    title: str
    description: str
    industry: str
    challenge: str
    learning_objectives: List[str]
    source_type: str = "manual"
    pdf_content: Optional[str] = None
    is_public: bool = False
    is_template: bool = False
    allow_remixes: bool = True

class ScenarioResponse(BaseModel):
    id: int
    title: str
    description: str
    industry: Optional[str] = None
    challenge: str
    learning_objectives: List[str]
    source_type: str
    pdf_content: Optional[str] = None
    is_public: bool
    is_template: bool
    allow_remixes: bool
    usage_count: int
    clone_count: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ScenarioUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    challenge: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    student_role: Optional[str] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_duration: Optional[int] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    allow_remixes: Optional[bool] = None

# --- PDF-TO-SCENARIO PUBLISHING SCHEMAS ---

class PersonalityTraits(BaseModel):
    analytical: Optional[int] = None
    creative: Optional[int] = None
    assertive: Optional[int] = None
    collaborative: Optional[int] = None
    detail_oriented: Optional[int] = None

class ScenarioPersonaCreate(BaseModel):
    name: str
    role: str
    background: Optional[str] = None
    correlation: Optional[str] = None
    primary_goals: Optional[List[str]] = None
    personality_traits: Optional[PersonalityTraits] = None

class ScenarioPersonaResponse(BaseModel):
    id: int
    scenario_id: int
    name: str
    role: str
    background: Optional[str]
    correlation: Optional[str]
    primary_goals: Optional[List[str]]
    personality_traits: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ScenarioSceneCreate(BaseModel):
    title: str
    description: str
    user_goal: Optional[str] = None
    scene_order: int = 0
    estimated_duration: Optional[int] = None
    image_url: Optional[str] = None
    image_prompt: Optional[str] = None
    # New fields
    timeout_turns: Optional[int] = None
    success_metric: Optional[str] = None
    persona_ids: Optional[List[int]] = None  # IDs of personas involved

class ScenarioSceneResponse(BaseModel):
    id: int
    scenario_id: int
    title: str
    description: str
    user_goal: Optional[str]
    scene_order: int
    estimated_duration: Optional[int]
    image_url: Optional[str]
    image_prompt: Optional[str]
    # New fields
    timeout_turns: Optional[int] = None
    success_metric: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    personas: Optional[List[ScenarioPersonaResponse]] = None
    
    class Config:
        from_attributes = True

class ScenarioFileResponse(BaseModel):
    id: int
    scenario_id: int
    filename: str
    file_size: Optional[int]
    file_type: str
    processing_status: str
    uploaded_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ScenarioReviewCreate(BaseModel):
    rating: int
    review_text: Optional[str] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    use_case: Optional[str] = None

class ScenarioReviewResponse(BaseModel):
    id: int
    scenario_id: int
    reviewer_id: int
    rating: int
    review_text: Optional[str]
    pros: Optional[List[str]]
    cons: Optional[List[str]]
    use_case: Optional[str]
    helpful_votes: int
    total_votes: int
    created_at: datetime
    reviewer: Optional[Dict[str, Any]] = None  # Basic user info
    
    class Config:
        from_attributes = True

# Enhanced scenario response with publishing data
class ScenarioPublishingResponse(BaseModel):
    id: int
    title: str
    description: str
    challenge: str
    industry: str
    learning_objectives: List[str]
    student_role: Optional[str]
    category: Optional[str]
    difficulty_level: Optional[str]
    estimated_duration: Optional[int]
    tags: Optional[List[str]]
    pdf_title: Optional[str]
    pdf_source: Optional[str]
    processing_version: str
    rating_avg: float
    rating_count: int
    source_type: str
    is_public: bool
    is_template: bool
    allow_remixes: bool
    usage_count: int
    clone_count: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    personas: Optional[List[ScenarioPersonaResponse]] = None
    scenes: Optional[List[ScenarioSceneResponse]] = None
    files: Optional[List[ScenarioFileResponse]] = None
    reviews: Optional[List[ScenarioReviewResponse]] = None
    creator: Optional[Dict[str, Any]] = None  # Basic user info
    
    class Config:
        from_attributes = True

# Publishing workflow schemas
class ScenarioPublishRequest(BaseModel):
    category: str
    difficulty_level: str
    tags: Optional[List[str]] = None
    estimated_duration: Optional[int] = None

class MarketplaceFilters(BaseModel):
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    tags: Optional[List[str]] = None
    min_rating: Optional[float] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20

class MarketplaceResponse(BaseModel):
    scenarios: List[ScenarioPublishingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# AI Processing result schema (from parse_pdf)
class AIProcessingResult(BaseModel):
    title: str
    description: str
    student_role: str
    key_figures: List[Dict[str, Any]]  # Personas from AI
    scenes: List[Dict[str, Any]]       # Scenes from AI
    learning_outcomes: List[str]

# --- SIMULATION SCHEMAS (Dynamic Crew Assembly) ---
class DynamicSimulationCreate(BaseModel):
    scenario_id: int
    selected_agent_ids: List[int]  # Agents chosen for this simulation
    agent_role_assignments: Optional[Dict[int, str]] = None  # Map agent_id -> role (e.g., {1: "marketing", 2: "finance"})
    process_type: str = "sequential"  # sequential, hierarchical, collaborative

class SimulationCreate(BaseModel):
    scenario_id: int
    crew_configuration: Optional[Dict[str, Any]] = None
    process_type: str = "sequential"

class SimulationResponse(BaseModel):
    id: int
    scenario_id: int
    user_id: Optional[int]
    selected_agent_ids: Optional[List[int]]
    agent_role_assignments: Optional[Dict[int, str]]
    process_type: str
    crew_configuration: Optional[Dict[str, Any]]
    status: str
    crew_output: Optional[str]
    execution_log: Optional[Dict[str, Any]]
    error_details: Optional[Dict[str, Any]]
    missing_agents: Optional[List[int]]
    missing_tasks: Optional[List[int]]
    fallback_used: bool
    is_public: bool
    allow_sharing: bool
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SimulationFallbackCreate(BaseModel):
    scenario_id: int
    fallback_agents: List[int] = []
    fallback_tasks: List[int] = []
    fallback_strategy: str = "substitute"  # substitute, skip, fail

class SimulationFallbackResponse(BaseModel):
    id: int
    scenario_id: int
    fallback_agents: List[int]
    fallback_tasks: List[int]
    fallback_strategy: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True



# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    email: str
    full_name: str
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "user"
    profile_public: bool = True
    allow_contact: bool = True

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    username: str
    bio: Optional[str]
    avatar_url: Optional[str]
    role: str
    published_scenarios: int
    total_simulations: int
    reputation_score: float
    profile_public: bool
    allow_contact: bool
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_public: Optional[bool] = None
    allow_contact: Optional[bool] = None

# --- USER AUTHENTICATION SCHEMAS ---
class UserRegister(BaseModel):
    email: str
    full_name: str
    username: str
    password: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_public: bool = True
    allow_contact: bool = True

class UserLogin(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class PasswordReset(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# --- COLLECTION SCHEMAS ---
class CollectionCreate(BaseModel):
    name: str
    description: str
    agents: List[int] = []
    tools: List[int] = []
    scenarios: List[int] = []
    is_public: bool = False
    tags: List[str] = []

class CollectionResponse(BaseModel):
    id: int
    name: str
    description: str
    agents: Optional[List[int]]
    tools: Optional[List[int]]
    scenarios: Optional[List[int]]
    is_public: bool
    tags: Optional[List[str]]
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- SEQUENTIAL SIMULATION SYSTEM SCHEMAS ---

class SimulationStartRequest(BaseModel):
    scenario_id: int
    user_id: int

class SimulationScenarioResponse(BaseModel):
    id: int
    title: str
    description: str
    challenge: str
    industry: Optional[str] = None
    learning_objectives: List[str]
    student_role: Optional[str] = None
    
    class Config:
        from_attributes = True

class SimulationStartResponse(BaseModel):
    user_progress_id: int
    scenario: SimulationScenarioResponse
    current_scene: ScenarioSceneResponse
    simulation_status: str
    
    class Config:
        from_attributes = True

class SimulationChatRequest(BaseModel):
    # Support both old and new formats
    user_progress_id: Optional[int] = None
    scenario_id: Optional[int] = None
    user_id: Optional[int] = None
    scene_id: Optional[int] = None
    message: str
    target_persona_id: Optional[int] = None  # Which persona to address

class SimulationChatResponse(BaseModel):
    # Support both formats - regular chat and linear simulation
    message_id: Optional[int] = None
    persona_name: Optional[str] = None
    persona_response: Optional[str] = None
    message_order: Optional[int] = None
    processing_time: Optional[float] = None
    ai_model_version: Optional[str] = None
    
    # Linear simulation format
    message: Optional[str] = None
    scene_id: Optional[int] = None
    scene_completed: Optional[bool] = None
    next_scene_id: Optional[int] = None
    persona_id: Optional[str] = None  # Persona ID for @mentions
    
    class Config:
        from_attributes = True

class GoalValidationRequest(BaseModel):
    user_progress_id: int
    scene_id: int
    recent_messages: Optional[List[str]] = None  # Recent conversation context

class GoalValidationResponse(BaseModel):
    goal_achieved: bool
    confidence_score: float
    reasoning: str
    next_action: str  # "continue", "progress", "hint", "force_progress"
    hint_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class SceneProgressRequest(BaseModel):
    user_progress_id: int
    current_scene_id: int
    goal_achieved: bool = False
    forced_progression: bool = False

class SceneProgressResponse(BaseModel):
    success: bool
    next_scene: Optional[ScenarioSceneResponse] = None
    simulation_complete: bool = False
    completion_summary: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserProgressResponse(BaseModel):
    id: int
    user_id: int
    scenario_id: int
    current_scene_id: Optional[int]
    simulation_status: str
    scenes_completed: List[int]
    total_attempts: int
    hints_used: int
    forced_progressions: int
    completion_percentage: float
    total_time_spent: int
    session_count: int
    final_score: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
    last_activity: datetime
    
    class Config:
        from_attributes = True

class SceneProgressResponse(BaseModel):
    id: int
    scene_id: int
    status: str
    attempts: int
    hints_used: int
    goal_achieved: bool
    forced_progression: bool
    time_spent: int
    messages_sent: int
    ai_responses: int
    goal_achievement_score: Optional[float]
    interaction_quality: Optional[float]
    scene_feedback: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ConversationLogResponse(BaseModel):
    id: int
    scene_id: int
    message_type: str
    sender_name: Optional[str]
    persona_id: Optional[int]
    message_content: str
    message_order: int
    attempt_number: int
    is_hint: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SimulationAnalyticsResponse(BaseModel):
    user_progress: UserProgressResponse
    scene_progress: List[SceneProgressResponse]
    conversation_summary: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    
    class Config:
        from_attributes = True

# Enhanced scene response with simulation features
class SimulationSceneResponse(ScenarioSceneResponse):
    goal_criteria: Optional[List[str]] = None
    max_attempts: int
    success_threshold: float
    hint_triggers: Optional[List[str]] = None
    scene_context: Optional[str] = None
    persona_instructions: Optional[Dict[str, str]] = None
    
    class Config:
        from_attributes = True

# --- LEGACY SCHEMAS (for backwards compatibility) ---
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    simulation_id: int
    user_message: str
    crew_response: str
    timestamp: str 