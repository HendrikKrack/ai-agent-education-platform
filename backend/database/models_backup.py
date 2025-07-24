# Enhanced Database Models for CrewAI Agent Builder Platform
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON, Table, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Junction tables for many-to-many relationships
scenario_agents = Table(
    'scenario_agents',
    Base.metadata,
    Column('scenario_id', Integer, ForeignKey('scenarios.id'), primary_key=True),
    Column('agent_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

# Removed scenario_tasks table - tasks now directly belong to scenarios

# Junction tables for simulation execution tracking
simulation_agents = Table(
    'simulation_agents',
    Base.metadata,
    Column('simulation_id', Integer, ForeignKey('simulations.id'), primary_key=True),
    Column('agent_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('agent_snapshot', JSON, nullable=True),  # Store agent config at time of simulation
    Column('assigned_role', String, nullable=True),  # Role assigned in this simulation (e.g., "marketing", "finance")
    Column('execution_order', Integer, default=0),   # Order in which agents execute
    Column('status', String, default='pending'),     # pending, running, completed, failed
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

simulation_tasks = Table(
    'simulation_tasks',
    Base.metadata,
    Column('simulation_id', Integer, ForeignKey('simulations.id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('agent_id', Integer, ForeignKey('agents.id'), nullable=True),  # Which agent is assigned
    Column('task_snapshot', JSON, nullable=True),   # Store task config at time of simulation
    Column('execution_order', Integer, default=0),  # Order in which tasks execute
    Column('status', String, default='pending'),    # pending, running, completed, failed
    Column('task_output', Text, nullable=True),     # Individual task result
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

# User favorites for agents and tools
user_favorite_agents = Table(
    'user_favorite_agents',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('agent_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

user_favorite_tools = Table(
    'user_favorite_tools',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('tool_id', Integer, ForeignKey('tools.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    username = Column(String, unique=True, index=True)  # For public profile
    password_hash = Column(String)  # Hashed password for authentication
    bio = Column(Text, nullable=True)  # User bio for public profile
    avatar_url = Column(String, nullable=True)  # Profile picture
    role = Column(String, default="user")  # admin, teacher, student, user
    
    # Community stats
    public_agents_count = Column(Integer, default=0)
    public_tools_count = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)  # How many times their content was used
    reputation_score = Column(Float, default=0.0)  # Community reputation
    
    # Settings
    profile_public = Column(Boolean, default=True)  # Whether profile is public
    allow_contact = Column(Boolean, default=True)  # Whether others can contact them
    
    # Account status
    is_active = Column(Boolean, default=True)  # Account active status
    is_verified = Column(Boolean, default=False)  # Email verification status
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenarios = relationship("Scenario", back_populates="creator")
    agents = relationship("Agent", back_populates="creator")
    tasks = relationship("Task", back_populates="creator")
    tools = relationship("Tool", back_populates="creator")
    simulations = relationship("Simulation", back_populates="user")
    
    # Reviews given by this user
    agent_reviews = relationship("AgentReview", back_populates="reviewer")
    tool_reviews = relationship("ToolReview", back_populates="reviewer")
    
    # Favorites
    favorite_agents = relationship("Agent", secondary=user_favorite_agents, back_populates="favorited_by")
    favorite_tools = relationship("Tool", secondary=user_favorite_tools, back_populates="favorited_by")
    
    # Simulation progress tracking
    progress_records = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")

class Scenario(Base):
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    challenge = Column(Text)  # The core challenge/problem to solve
    industry = Column(String)
    learning_objectives = Column(JSON)  # List of learning goals
    
    # Source information
    source_type = Column(String, default="manual")  # manual, pdf_upload, template
    pdf_content = Column(Text, nullable=True)  # Original PDF content if uploaded
    
    # Publishing extensions for PDF-to-scenario
    student_role = Column(String, nullable=True)  # Role student assumes in scenario
    category = Column(String, nullable=True)  # Leadership, Strategy, Operations, etc.
    difficulty_level = Column(String, nullable=True)  # Beginner, Intermediate, Advanced
    estimated_duration = Column(Integer, nullable=True)  # Total scenario time in minutes
    tags = Column(JSON, nullable=True)  # Searchable tags array
    
    # PDF processing metadata
    pdf_title = Column(String, nullable=True)  # Extracted from PDF header
    pdf_source = Column(String, nullable=True)  # Harvard, Wharton, etc.
    processing_version = Column(String, default="1.0")  # AI model version used
    
    # Community ratings
    rating_avg = Column(Float, default=0.0)  # Average user rating
    rating_count = Column(Integer, default=0)  # Number of ratings
    
    # Sharing settings
    is_public = Column(Boolean, default=False)  # Public scenarios can be used by anyone
    is_template = Column(Boolean, default=False)  # Template scenarios with suggested agents/tasks
    allow_remixes = Column(Boolean, default=True)  # Allow others to create variations
    
    # Community metrics
    usage_count = Column(Integer, default=0)  # How many times used
    clone_count = Column(Integer, default=0)  # How many times cloned
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="scenarios")
    simulations = relationship("Simulation", back_populates="scenario")
    tasks = relationship("Task", back_populates="scenario", cascade="all, delete-orphan")  # Direct relationship
    personas = relationship("ScenarioPersona", back_populates="scenario", cascade="all, delete-orphan")
    scenes = relationship("ScenarioScene", back_populates="scenario", cascade="all, delete-orphan")
    files = relationship("ScenarioFile", back_populates="scenario", cascade="all, delete-orphan")
    
    # Many-to-many relationships (for suggested agents, not required)
    suggested_agents = relationship("Agent", secondary=scenario_agents, back_populates="scenarios")

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)
    goal = Column(Text)
    backstory = Column(Text)
    tools = Column(JSON)  # List of tool IDs/names
    verbose = Column(Boolean, default=True)
    allow_delegation = Column(Boolean, default=False)
    reasoning = Column(Boolean, default=True)
    
    # Agent categorization
    category = Column(String, nullable=True)  # business, technical, creative, analytical
    tags = Column(JSON, nullable=True)  # Searchable tags
    
    # Sharing settings
    is_public = Column(Boolean, default=False)  # Public agents can be used by anyone
    is_template = Column(Boolean, default=False)  # Template agents for suggestions
    allow_remixes = Column(Boolean, default=True)  # Allow others to create variations
    original_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)  # If this is a remix
    
    # Community metrics
    usage_count = Column(Integer, default=0)  # How many times used in simulations
    clone_count = Column(Integer, default=0)  # How many times cloned
    average_rating = Column(Float, default=0.0)  # Average user rating
    rating_count = Column(Integer, default=0)  # Number of ratings
    
    # Version control
    version = Column(String, default="1.0.0")
    version_notes = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="agents")
    reviews = relationship("AgentReview", back_populates="agent")
    original_agent = relationship("Agent", remote_side=[id])  # Self-referential for remixes
    
    # Many-to-many relationships
    scenarios = relationship("Scenario", secondary=scenario_agents, back_populates="suggested_agents")
    favorited_by = relationship("User", secondary=user_favorite_agents, back_populates="favorite_agents")
    simulations_used_in = relationship("Simulation", secondary=simulation_agents, back_populates="executed_agents")

class Tool(Base):
    __tablename__ = "tools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    tool_type = Column(String)  # web_search, file_read, api_call, custom, etc.
    
    # Tool configuration
    configuration = Column(JSON)  # Tool-specific configuration
    required_credentials = Column(JSON, nullable=True)  # What API keys/credentials needed
    usage_instructions = Column(Text, nullable=True)  # How to use this tool
    
    # Code for custom tools
    code = Column(Text, nullable=True)  # Python code for custom tools
    requirements = Column(JSON, nullable=True)  # Python dependencies
    
    # Categorization
    category = Column(String, nullable=True)  # web, file, api, data, communication
    tags = Column(JSON, nullable=True)  # Searchable tags
    
    # Sharing settings
    is_public = Column(Boolean, default=False)  # Public tools can be used by anyone
    is_verified = Column(Boolean, default=False)  # Verified by platform admins
    allow_remixes = Column(Boolean, default=True)  # Allow others to create variations
    original_tool_id = Column(Integer, ForeignKey("tools.id"), nullable=True)  # If this is a remix
    
    # Community metrics
    usage_count = Column(Integer, default=0)  # How many times used
    clone_count = Column(Integer, default=0)  # How many times cloned
    average_rating = Column(Float, default=0.0)  # Average user rating
    rating_count = Column(Integer, default=0)  # Number of ratings
    
    # Version control
    version = Column(String, default="1.0.0")
    version_notes = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="tools")
    reviews = relationship("ToolReview", back_populates="tool")
    original_tool = relationship("Tool", remote_side=[id])  # Self-referential for remixes
    favorited_by = relationship("User", secondary=user_favorite_tools, back_populates="favorite_tools")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    expected_output = Column(Text)  # What the task should produce
    
    # Task configuration
    tools = Column(JSON, nullable=True)  # Specific tools for this task
    context = Column(JSON, nullable=True)  # Additional context or constraints
    
    # Scenario assignment (tasks belong to scenarios, not agents)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    
    # Optional agent assignment (for pre-configured scenarios)
    assigned_agent_role = Column(String, nullable=True)  # e.g., "marketing", "finance" (role-based, not specific agent)
    
    # Task execution order and dependencies
    execution_order = Column(Integer, default=0)  # Order within scenario
    depends_on_tasks = Column(JSON, nullable=True)  # Array of task IDs this depends on
    
    # Task categorization
    category = Column(String, nullable=True)  # analysis, research, planning, execution
    tags = Column(JSON, nullable=True)  # Searchable tags
    
    # Sharing settings
    is_public = Column(Boolean, default=False)  # Public tasks can be used by anyone
    is_template = Column(Boolean, default=False)  # Template tasks for suggestions
    allow_remixes = Column(Boolean, default=True)  # Allow others to create variations
    
    # Community metrics
    usage_count = Column(Integer, default=0)  # How many times used
    clone_count = Column(Integer, default=0)  # How many times cloned
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="tasks")
    scenario = relationship("Scenario", back_populates="tasks")
    
    # Simulations where this task was executed
    simulations_used_in = relationship("Simulation", secondary=simulation_tasks, back_populates="executed_tasks")

class AgentReview(Base):
    __tablename__ = "agent_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    
    rating = Column(Integer)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    pros = Column(JSON, nullable=True)  # List of positive aspects
    cons = Column(JSON, nullable=True)  # List of negative aspects
    use_case = Column(String, nullable=True)  # What they used it for
    
    # Helpful votes
    helpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="reviews")
    reviewer = relationship("User", back_populates="agent_reviews")

class ToolReview(Base):
    __tablename__ = "tool_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("tools.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    
    rating = Column(Integer)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    pros = Column(JSON, nullable=True)  # List of positive aspects
    cons = Column(JSON, nullable=True)  # List of negative aspects
    use_case = Column(String, nullable=True)  # What they used it for
    
    # Helpful votes
    helpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tool = relationship("Tool", back_populates="reviews")
    reviewer = relationship("User", back_populates="tool_reviews")

class Simulation(Base):
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Dynamic crew configuration
    selected_agent_ids = Column(JSON)  # Array of agent IDs selected for this simulation
    agent_role_assignments = Column(JSON)  # Map of agent_id -> role (e.g., {1: "marketing", 2: "finance"})
    process_type = Column(String, default="sequential")  # sequential, hierarchical, collaborative
    crew_configuration = Column(JSON, nullable=True)  # Stores the actual CrewAI crew setup (generated dynamically)
    
    # Execution details
    status = Column(String, default="created")  # created, running, completed, failed, failed_missing_resources
    crew_output = Column(Text, nullable=True)  # Final crew result
    execution_log = Column(JSON, nullable=True)  # Detailed execution steps
    error_details = Column(JSON, nullable=True)  # Details about any errors (missing agents/tasks)
    
    # Resource availability tracking
    missing_agents = Column(JSON, nullable=True)  # List of agent IDs that couldn't be accessed
    missing_tasks = Column(JSON, nullable=True)   # List of task IDs that couldn't be accessed
    fallback_used = Column(Boolean, default=False)  # Whether fallback agents/tasks were used
    
    # Sharing settings
    is_public = Column(Boolean, default=False)  # Public simulations can be viewed by others
    allow_sharing = Column(Boolean, default=False)  # Allow others to see the results
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    scenario = relationship("Scenario", back_populates="simulations")
    user = relationship("User", back_populates="simulations")
    messages = relationship("SimulationMessage", back_populates="simulation")
    
    # Many-to-many relationships for execution tracking
    executed_agents = relationship("Agent", secondary=simulation_agents, back_populates="simulations_used_in")
    executed_tasks = relationship("Task", secondary=simulation_tasks, back_populates="simulations_used_in")

class SimulationMessage(Base):
    __tablename__ = "simulation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"))
    
    # Message content
    user_message = Column(Text)
    crew_response = Column(Text)
    agent_responses = Column(JSON, nullable=True)  # Individual agent responses
    
    # Message metadata
    message_type = Column(String, default="chat")  # chat, system, error
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    simulation = relationship("Simulation", back_populates="messages")

# Collections/Bundles - Users can create curated collections
class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    
    # Collection contents
    agents = Column(JSON, nullable=True)  # List of agent IDs
    tools = Column(JSON, nullable=True)  # List of tool IDs
    scenarios = Column(JSON, nullable=True)  # List of scenario IDs
    
    # Sharing settings
    is_public = Column(Boolean, default=False)
    tags = Column(JSON, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")

# Template data for AI suggestions  
class AgentTemplate(Base):
    __tablename__ = "agent_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    goal = Column(Text)
    backstory = Column(Text)
    tools = Column(JSON)
    category = Column(String)  # business, technical, creative, analytical
    industries = Column(JSON)  # Which industries this agent is good for
    use_cases = Column(JSON)  # Common use cases
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TaskTemplate(Base):
    __tablename__ = "task_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    expected_output = Column(Text)
    category = Column(String)  # analysis, research, planning, execution
    agent_roles = Column(JSON)  # What agent roles this task is good for
    industries = Column(JSON)  # Which industries this task is good for
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Fallback configurations for graceful error handling
class SimulationFallback(Base):
    __tablename__ = "simulation_fallbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    
    # Fallback configurations
    fallback_agents = Column(JSON)  # List of public agent IDs to use as fallbacks
    fallback_tasks = Column(JSON)   # List of public task IDs to use as fallbacks
    fallback_strategy = Column(String, default="substitute")  # substitute, skip, fail
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenario = relationship("Scenario")
    creator = relationship("User")

# --- PDF-TO-SCENARIO PUBLISHING MODELS ---

# Junction table for scene-persona relationships
scene_personas = Table(
    'scene_personas',
    Base.metadata,
    Column('scene_id', Integer, ForeignKey('scenario_scenes.id'), primary_key=True),
    Column('persona_id', Integer, ForeignKey('scenario_personas.id'), primary_key=True),
    Column('involvement_level', String, default='participant'),  # key, participant, mentioned
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

class ScenarioPersona(Base):
    __tablename__ = "scenario_personas"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    
    # Persona details from AI processing
    name = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    background = Column(Text, nullable=True)
    correlation = Column(Text, nullable=True)  # How they relate to the case
    
    # Goals and traits from AI
    primary_goals = Column(JSON, nullable=True)  # Array of goal strings
    personality_traits = Column(JSON, nullable=True)  # {analytical: 8, creative: 7, assertive: 6, ...}
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenario = relationship("Scenario", back_populates="personas")
    scenes = relationship("ScenarioScene", secondary=scene_personas, back_populates="personas")

class ScenarioScene(Base):
    __tablename__ = "scenario_scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    
    # Scene details from AI processing
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    user_goal = Column(Text, nullable=True)  # What the student should accomplish
    
    # Scene organization
    scene_order = Column(Integer, default=0)  # Order in timeline
    estimated_duration = Column(Integer, nullable=True)  # Minutes for this scene
    
    # Sequential simulation enhancements
    goal_criteria = Column(JSON, nullable=True)  # Specific criteria for goal achievement
    max_attempts = Column(Integer, default=5)  # Maximum attempts before forced progression
    success_threshold = Column(Float, default=0.7)  # AI confidence threshold for goal achievement
    hint_triggers = Column(JSON, nullable=True)  # Conditions that trigger hints
    
    # Context for AI personas
    scene_context = Column(Text, nullable=True)  # Additional context for AI personas in this scene
    persona_instructions = Column(JSON, nullable=True)  # Specific instructions per persona for this scene
    
    # Visual assets
    image_url = Column(String, nullable=True)  # DALL-E generated image
    image_prompt = Column(Text, nullable=True)  # Original prompt used for image
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenario = relationship("Scenario", back_populates="scenes")
    personas = relationship("ScenarioPersona", secondary=scene_personas, back_populates="scenes")

class ScenarioFile(Base):
    __tablename__ = "scenario_files"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    
    # File details
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=True)  # Local storage path
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_type = Column(String, default="pdf")  # pdf, docx, etc.
    
    # Content storage
    original_content = Column(Text, nullable=True)  # Raw file content
    processed_content = Column(Text, nullable=True)  # Cleaned content used for AI
    
    # Processing tracking
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_log = Column(JSON, nullable=True)  # AI processing details and debug info
    llamaparse_job_id = Column(String, nullable=True)  # LlamaParse job tracking
    
    # Metadata
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    scenario = relationship("Scenario", back_populates="files")

class ScenarioReview(Base):
    __tablename__ = "scenario_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    pros = Column(JSON, nullable=True)  # Array of positive aspects
    cons = Column(JSON, nullable=True)  # Array of negative aspects
    use_case = Column(String, nullable=True)  # How they used the scenario
    
    # Community engagement
    helpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scenario = relationship("Scenario")
    reviewer = relationship("User")

# Sequential Simulation System Models

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    
    # Current simulation state
    current_scene_id = Column(Integer, ForeignKey("scenario_scenes.id"), nullable=True)
    simulation_status = Column(String, default="not_started")  # not_started, in_progress, completed, abandoned
    
    # Progress tracking
    scenes_completed = Column(JSON, default=list)  # Array of completed scene IDs
    total_attempts = Column(Integer, default=0)  # Total attempts across all scenes
    hints_used = Column(Integer, default=0)  # Total hints requested
    forced_progressions = Column(Integer, default=0)  # Times auto-advanced due to max attempts
    
    # Performance metrics
    completion_percentage = Column(Float, default=0.0)  # 0-100%
    average_attempts_per_scene = Column(Float, default=0.0)
    total_time_spent = Column(Integer, default=0)  # Total time in seconds
    
    # Session tracking
    session_count = Column(Integer, default=0)  # Number of separate sessions
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Final results
    final_score = Column(Float, nullable=True)  # Overall performance score
    completion_notes = Column(Text, nullable=True)  # AI-generated summary of performance
    
    # Metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    scenario = relationship("Scenario")
    current_scene = relationship("ScenarioScene", foreign_keys=[current_scene_id])
    scene_progress = relationship("SceneProgress", back_populates="user_progress", cascade="all, delete-orphan")
    conversation_logs = relationship("ConversationLog", back_populates="user_progress", cascade="all, delete-orphan")

class SceneProgress(Base):
    __tablename__ = "scene_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False)
    scene_id = Column(Integer, ForeignKey("scenario_scenes.id"), nullable=False)
    
    # Scene-specific progress
    status = Column(String, default="not_started")  # not_started, in_progress, completed, skipped
    attempts = Column(Integer, default=0)  # Attempts for this specific scene
    hints_used = Column(Integer, default=0)  # Hints requested for this scene
    goal_achieved = Column(Boolean, default=False)  # Whether the scene goal was achieved
    forced_progression = Column(Boolean, default=False)  # Whether auto-advanced
    
    # Performance data
    time_spent = Column(Integer, default=0)  # Time spent in seconds on this scene
    messages_sent = Column(Integer, default=0)  # Number of messages sent by user
    ai_responses = Column(Integer, default=0)  # Number of AI responses received
    
    # AI evaluation
    goal_achievement_score = Column(Float, nullable=True)  # AI-scored performance (0-100)
    interaction_quality = Column(Float, nullable=True)  # Quality of user interactions
    scene_feedback = Column(Text, nullable=True)  # AI-generated feedback for this scene
    
    # Metadata
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user_progress = relationship("UserProgress", back_populates="scene_progress")
    scene = relationship("ScenarioScene")

class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False)
    scene_id = Column(Integer, ForeignKey("scenario_scenes.id"), nullable=False)
    
    # Message details
    message_type = Column(String, nullable=False)  # user, ai_persona, system, hint
    sender_name = Column(String, nullable=True)  # Persona name if AI, user name if user
    persona_id = Column(Integer, ForeignKey("scenario_personas.id"), nullable=True)  # If AI persona
    message_content = Column(Text, nullable=False)
    
    # Context and metadata
    message_order = Column(Integer, nullable=False)  # Order within the scene
    attempt_number = Column(Integer, default=1)  # Which attempt this message belongs to
    is_hint = Column(Boolean, default=False)  # Whether this is a hint message
    
    # AI processing context
    ai_context_used = Column(JSON, nullable=True)  # Context passed to AI for this message
    ai_model_version = Column(String, nullable=True)  # GPT model version used
    processing_time = Column(Float, nullable=True)  # AI response time in seconds
    
    # User interaction tracking
    user_reaction = Column(String, nullable=True)  # positive, negative, neutral (if tracked)
    led_to_progress = Column(Boolean, default=False)  # Whether this message led to goal achievement
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_progress = relationship("UserProgress", back_populates="conversation_logs")
    scene = relationship("ScenarioScene")
    persona = relationship("ScenarioPersona", foreign_keys=[persona_id]) 