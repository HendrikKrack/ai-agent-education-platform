# AI Agent Education Platform - Complete API Reference

## Overview

The AI Agent Education Platform provides a comprehensive REST API for managing users, AI agents, business scenarios, and **linear simulation experiences**. The platform now features an integrated **ChatOrchestrator** system that manages multi-scene simulations with AI persona interactions, enabling immersive educational experiences through PDF-to-simulation pipelines.

**Base URL:** `http://localhost:8000`
**API Version:** 2.0.0
**Authentication:** JWT Bearer tokens

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Scenario Management](#scenario-management)
4. [PDF Processing & AI Analysis](#pdf-processing--ai-analysis)
5. [Linear Simulation System](#linear-simulation-system)
6. [Chat Orchestrator](#chat-orchestrator)
7. [Publishing & Marketplace](#publishing--marketplace)
8. [System Endpoints](#system-endpoints)
9. [Error Handling](#error-handling)

---

## Authentication

### Overview
The API uses JWT (JSON Web Tokens) for authentication. Include the token in the `Authorization` header for protected endpoints.

**Header Format:**
```
Authorization: Bearer <jwt_token>
```

### User Registration

**`POST /users/register`**

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe",
  "role": "user",
  "is_active": true,
  "created_at": "2025-01-06T12:00:00Z"
}
```

### User Login

**`POST /users/login`**

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "username": "johndoe",
    "role": "user"
  }
}
```

---

## User Management

### Get Current User Profile

**`GET /users/me`** 🔒

Get the authenticated user's profile information.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "username": "johndoe",
  "role": "user",
  "published_scenarios": 5,
  "total_simulations": 12,
  "reputation_score": 4.2,
  "created_at": "2025-01-06T12:00:00Z"
}
```

---

## Scenario Management

### Create Scenario

**`POST /scenarios/`** 🔒

Create a new business scenario manually.

**Request Body:**
```json
{
  "title": "E-commerce Platform Launch",
  "description": "Launch a new e-commerce platform in competitive market",
  "industry": "Technology",
  "challenge": "Compete with established players while building customer trust",
  "learning_objectives": [
    "Market analysis and positioning",
    "Customer acquisition strategies",
    "Technology stack decisions"
  ],
  "student_role": "Product Manager",
  "source_type": "manual"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "E-commerce Platform Launch",
  "description": "Launch a new e-commerce platform...",
  "industry": "Technology",
  "challenge": "Compete with established players...",
  "learning_objectives": [
    "Market analysis and positioning",
    "Customer acquisition strategies",
    "Technology stack decisions"
  ],
  "student_role": "Product Manager",
  "source_type": "manual",
  "is_public": false,
  "created_by": 1,
  "created_at": "2025-01-06T12:00:00Z"
}
```

### Get All Scenarios

**`GET /scenarios/`**

Get list of all available scenarios.

**Query Parameters:**
- `skip` (integer, optional) - Number of records to skip (default: 0)
- `limit` (integer, optional) - Number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "title": "E-commerce Platform Launch",
    "description": "Launch a new e-commerce platform...",
    "industry": "Technology",
    "is_public": true,
    "usage_count": 25,
    "created_at": "2025-01-06T12:00:00Z"
  }
]
```

### Get Scenario by ID

**`GET /scenarios/{scenario_id}`**

Get detailed information about a specific scenario including personas and scenes.

**Response:**
```json
{
  "id": 1,
  "title": "E-commerce Platform Launch",
  "description": "Launch a new e-commerce platform...",
  "industry": "Technology",
  "challenge": "Compete with established players...",
  "learning_objectives": ["Market analysis", "Customer acquisition"],
  "student_role": "Product Manager",
  "personas": [
    {
      "id": 1,
      "name": "Sarah Chen",
      "role": "Marketing Director",
      "background": "10+ years in digital marketing...",
      "personality_traits": {
        "analytical": 8,
        "creative": 7,
        "assertive": 6
      }
    }
  ],
  "scenes": [
    {
      "id": 1,
      "title": "Market Analysis Meeting",
      "description": "Initial market research discussion...",
      "user_goal": "Understand target market segments",
      "scene_order": 1,
      "image_url": "https://example.com/scene1.jpg"
    }
  ]
}
```

---

## PDF Processing & AI Analysis

### Upload and Process PDF

**`POST /api/parse-pdf/`**

Upload a PDF case study and process it with AI to extract scenarios, personas, and scenes.

**Request:**
- **Content-Type:** `multipart/form-data`
- **file:** PDF file (required)
- **context_files:** Additional context files (optional)
- **save_to_db:** Boolean to save results (default: false)
- **user_id:** User ID (default: 1)

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/parse-pdf/" \
  -F "file=@business_case.pdf" \
  -F "context_files=@additional_context.txt" \
  -F "save_to_db=true" \
  -F "user_id=1"
```

**Response:**
```json
{
  "status": "completed",
  "scenario_id": 15,
  "ai_result": {
    "title": "KasKazi Network Ltd – Distributing to the Bottom of the Pyramid",
    "description": "This case examines the challenges faced by KasKazi Network...",
    "student_role": "Business Strategy Consultant",
    "key_figures": [
      {
        "name": "Wanjohi",
        "role": "Founder/CEO of KasKazi Network",
        "background": "Entrepreneur with deep market knowledge...",
        "correlation": "Primary decision maker facing strategic challenges",
        "primary_goals": [
          "Achieve year-round business operations",
          "Build sustainable competitive advantage",
          "Expand market reach"
        ],
        "personality_traits": {
          "analytical": 9,
          "creative": 7,
          "assertive": 8,
          "collaborative": 6,
          "detail_oriented": 8
        }
      }
    ],
    "scenes": [
      {
        "title": "Crisis Assessment Meeting",
        "description": "Emergency meeting to assess seasonal contract challenges...",
        "user_goal": "Understand the scope and impact of seasonal dependency",
        "sequence_order": 1,
        "image_url": "https://generated-image-url.com/scene1.jpg"
      }
    ],
    "learning_outcomes": [
      "1. Analyze business model sustainability challenges",
      "2. Evaluate market entry strategies for emerging markets",
      "3. Develop solutions for supply chain continuity"
    ]
  }
}
```

**Status Codes:**
- `200` - PDF processed successfully
- `400` - Invalid file format or missing file
- `500` - Processing error (LlamaParse or OpenAI issues)

---

## Linear Simulation System

### Start Linear Simulation

**`POST /api/simulation/start`**

Start a new linear simulation with ChatOrchestrator integration.

**Request Body:**
```json
{
  "scenario_id": 1,
  "user_id": 1
}
```

**Response:**
```json
{
  "user_progress_id": 123,
  "scenario": {
    "id": 1,
    "title": "KasKazi Network Strategic Challenge",
    "description": "Navigate seasonal contract dependencies...",
    "challenge": "Develop sustainable business model",
    "industry": "Distribution",
    "learning_objectives": [
      "Analyze market dynamics",
      "Develop strategic solutions"
    ],
    "student_role": "Business Strategy Consultant"
  },
  "current_scene": {
    "id": 1,
    "scenario_id": 1,
    "title": "Crisis Assessment Meeting",
    "description": "Emergency meeting in the boardroom...",
    "user_goal": "Assess scope of seasonal dependency crisis",
    "scene_order": 1,
    "estimated_duration": 30,
    "image_url": "https://example.com/scene1.jpg",
    "personas": [
      {
        "id": 1,
        "name": "Wanjohi",
        "role": "Founder/CEO",
        "background": "Experienced entrepreneur...",
        "personality_traits": {
          "analytical": 9,
          "assertive": 8
        }
      }
    ]
  },
  "simulation_status": "waiting_for_begin"
}
```

### Linear Chat with Orchestrator

**`POST /api/simulation/linear-chat`**

Send a message to the ChatOrchestrator for linear simulation experience.

**Request Body:**
```json
{
  "scenario_id": 1,
  "user_id": 1,
  "scene_id": 1,
  "message": "begin"
}
```

**Response:**
```json
{
  "message": "# KasKazi Network Strategic Challenge\n\nWelcome to this multi-scene simulation where you'll navigate complex business challenges...\n\n**Scene 1 — Crisis Assessment Meeting**\n\n*You're in the main conference room with senior leadership, reviewing urgent seasonal contract issues...*\n\n**Objective:** Assess the scope and impact of seasonal dependency\n\n**Active Participants:**\n• @wanjohi: Wanjohi (Founder/CEO)\n\n*You have 20 turns to achieve the objective.*\n\n**@wanjohi:** Welcome to our emergency strategy session. As you can see from the reports, our seasonal contract model is creating significant gaps in our operations. What's your initial assessment of our situation?",
  "scene_id": 1,
  "scene_completed": false,
  "next_scene_id": null
}
```

**Special Commands:**
- `"begin"` - Start the simulation
- `"help"` - Get available commands and current status
- `@mention` - Interact with specific personas (e.g., `@wanjohi`)

### Chat with Business Simulation (Legacy)

**`POST /api/simulate/`**

Legacy endpoint for phase-based business simulations.

**Request Body:**
```json
{
  "user_input": "What should be our market entry strategy?",
  "phase": {
    "title": "Market Analysis",
    "goal": "Complete comprehensive market analysis",
    "deliverables": ["Market size analysis", "Competitor mapping"]
  },
  "case_study": {
    "title": "E-commerce Launch",
    "description": "Launch strategy for new platform",
    "characters": [
      {
        "name": "Marketing Director",
        "role": "Senior Marketing Lead"
      }
    ]
  },
  "attempts": 0
}
```

**Response:**
```json
{
  "ai_response": "**Marketing Director:** Based on our analysis, I recommend a three-phased approach...\n\n**Hint →** Consider analyzing customer acquisition costs for each segment."
}
```

---

## Chat Orchestrator

The ChatOrchestrator manages linear simulation experiences with multi-scene progression and AI persona interactions.

### Orchestrator Features

1. **Scene Management** - Automatic progression through predefined scenes
2. **Persona Interactions** - Dynamic AI character responses based on personality
3. **Goal Tracking** - Monitors objective completion and provides hints
4. **State Management** - Maintains simulation state across sessions
5. **Command System** - Built-in commands (begin, help, @mentions)

### Orchestrator System Prompt Structure

The orchestrator uses a comprehensive system prompt that includes:
- Current scenario and scene context
- Available AI personas with personalities
- Scene objectives and success criteria
- Turn limits and progression rules
- Command handling (begin, help, @mentions)

### Scene Progression Logic

```javascript
// Scene advances when:
// 1. Success criteria met (determined by LLM)
// 2. Turn limit reached (timeout)
// 3. Manual progression command

if (scene_completed || turns_remaining <= 0) {
  advance_to_next_scene();
}
```

---

## Publishing & Marketplace

### Publish Scenario

**`POST /api/publishing/publish-scenario`** 🔒

Publish a scenario to the public marketplace.

**Request Body:**
```json
{
  "scenario_id": 1,
  "category": "business_strategy",
  "difficulty_level": "intermediate",
  "estimated_duration": 60,
  "tags": ["strategy", "market_analysis", "decision_making"]
}
```

**Response:**
```json
{
  "message": "Scenario published successfully",
  "scenario": {
    "id": 1,
    "title": "E-commerce Platform Launch",
    "is_public": true,
    "category": "business_strategy",
    "difficulty_level": "intermediate",
    "published_at": "2025-01-06T12:00:00Z"
  }
}
```

### Get Marketplace Scenarios

**`GET /api/publishing/marketplace`**

Get published scenarios from the marketplace.

**Query Parameters:**
- `category` (string, optional) - Filter by category
- `difficulty` (string, optional) - Filter by difficulty level
- `search` (string, optional) - Search in titles and descriptions
- `page` (integer, optional) - Page number (default: 1)
- `page_size` (integer, optional) - Items per page (default: 20)

**Response:**
```json
{
  "scenarios": [
    {
      "id": 1,
      "title": "E-commerce Platform Launch",
      "description": "Strategic launch simulation...",
      "category": "business_strategy",
      "difficulty_level": "intermediate",
      "estimated_duration": 60,
      "tags": ["strategy", "market_analysis"],
      "rating_avg": 4.5,
      "rating_count": 23,
      "usage_count": 156,
      "created_by": {
        "username": "business_prof",
        "full_name": "Dr. Sarah Johnson"
      }
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

## System Endpoints

### Health Check

**`GET /health/`**

Check the system health and status.

**Response:**
```json
{
  "status": "healthy",
  "framework": "FastAPI",
  "platform": "AI Agent Education Platform",
  "version": "2.0.0",
  "database": "connected",
  "ai_services": {
    "openai": "connected",
    "llamaparse": "connected"
  }
}
```

### Root Endpoint

**`GET /`**

Get basic API information.

**Response:**
```json
{
  "message": "AI Agent Education Platform - PDF to Simulation Pipeline",
  "version": "2.0.0",
  "features": [
    "PDF Processing with AI Analysis",
    "Linear Simulation with ChatOrchestrator", 
    "Multi-Scene Progression",
    "AI Persona Interactions",
    "Marketplace Publishing"
  ]
}
```

### API Documentation

**`GET /docs`**

Interactive API documentation (Swagger UI).

**`GET /redoc`**

Alternative API documentation (ReDoc).

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

### Common HTTP Status Codes

- **200** - Success
- **201** - Created
- **400** - Bad Request (validation error, missing file)
- **401** - Unauthorized (authentication required)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found (scenario, user, scene not found)
- **422** - Unprocessable Entity (request format error)
- **500** - Internal Server Error (AI processing, database error)

### Specific Error Examples

**PDF Processing Error (500):**
```json
{
  "detail": "Failed to parse PDF: LlamaParse service unavailable",
  "error_code": "PDF_PROCESSING_ERROR",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

**Simulation Not Found (404):**
```json
{
  "detail": "No active simulation found for user",
  "error_code": "SIMULATION_NOT_FOUND",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

**Scene Progression Error (400):**
```json
{
  "detail": "Simulation not properly initialized with orchestrator data",
  "error_code": "ORCHESTRATOR_NOT_INITIALIZED",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

---

## Integration Examples

### Python SDK Example

```python
import requests

class AIEducationClient:
    def __init__(self, base_url="http://localhost:8000", token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def upload_pdf_case_study(self, pdf_path, save_to_db=True):
        """Upload and process PDF case study"""
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            data = {'save_to_db': save_to_db, 'user_id': 1}
            response = self.session.post(
                f'{self.base_url}/api/parse-pdf/',
                files=files,
                data=data
            )
        return response.json()
    
    def start_linear_simulation(self, scenario_id, user_id=1):
        """Start a new linear simulation"""
        return self.session.post(
            f'{self.base_url}/api/simulation/start',
            json={
                'scenario_id': scenario_id,
                'user_id': user_id
            }
        ).json()
    
    def chat_with_orchestrator(self, scenario_id, user_id, scene_id, message):
        """Send message to ChatOrchestrator"""
        return self.session.post(
            f'{self.base_url}/api/simulation/linear-chat',
            json={
                'scenario_id': scenario_id,
                'user_id': user_id,
                'scene_id': scene_id,
                'message': message
            }
        ).json()

# Usage Example
client = AIEducationClient()

# 1. Upload and process PDF case study
pdf_result = client.upload_pdf_case_study('harvard_case.pdf', save_to_db=True)
scenario_id = pdf_result['scenario_id']

# 2. Start linear simulation
simulation = client.start_linear_simulation(scenario_id)
scene_id = simulation['current_scene']['id']

# 3. Begin simulation
begin_response = client.chat_with_orchestrator(
    scenario_id, 1, scene_id, "begin"
)

# 4. Interact with personas
response = client.chat_with_orchestrator(
    scenario_id, 1, scene_id, "@wanjohi What are the main challenges?"
)

print(response['message'])
```

### JavaScript/Node.js Example

```javascript
class AIEducationClient {
  constructor(baseUrl = 'http://localhost:8000', token = null) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  async uploadPDFCaseStudy(pdfFile, saveToDb = true) {
    const formData = new FormData();
    formData.append('file', pdfFile);
    formData.append('save_to_db', saveToDb);
    formData.append('user_id', '1');

    const response = await fetch(`${this.baseUrl}/api/parse-pdf/`, {
      method: 'POST',
      body: formData,
      headers: this.token ? { Authorization: `Bearer ${this.token}` } : {}
    });
    return response.json();
  }

  async startLinearSimulation(scenarioId, userId = 1) {
    const response = await fetch(`${this.baseUrl}/api/simulation/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` })
      },
      body: JSON.stringify({
        scenario_id: scenarioId,
        user_id: userId
      })
    });
    return response.json();
  }

  async chatWithOrchestrator(scenarioId, userId, sceneId, message) {
    const response = await fetch(`${this.baseUrl}/api/simulation/linear-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` })
      },
      body: JSON.stringify({
        scenario_id: scenarioId,
        user_id: userId,
        scene_id: sceneId,
        message: message
      })
    });
    return response.json();
  }
}

// Usage Example
const client = new AIEducationClient();

// Upload PDF and start simulation
const pdfFile = document.getElementById('pdf-input').files[0];
const pdfResult = await client.uploadPDFCaseStudy(pdfFile, true);
const scenarioId = pdfResult.scenario_id;

const simulation = await client.startLinearSimulation(scenarioId);
const sceneId = simulation.current_scene.id;

// Begin and interact
const beginResponse = await client.chatWithOrchestrator(
  scenarioId, 1, sceneId, "begin"
);

const chatResponse = await client.chatWithOrchestrator(
  scenarioId, 1, sceneId, "@wanjohi What should be our first priority?"
);

console.log(chatResponse.message);
```

---

## Rate Limiting

### Default Limits
- **PDF Processing:** 5 uploads per hour per user
- **Simulation endpoints:** 100 requests per minute per user
- **Chat endpoints:** 60 messages per minute per simulation
- **General API endpoints:** 1000 requests per hour per user

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1625097600
```

---

## Changelog

### Version 2.0.0 (Current)
- ✅ **ChatOrchestrator Integration** - Linear simulation flow with multi-scene progression
- ✅ **PDF-to-Simulation Pipeline** - AI-powered case study processing
- ✅ **Enhanced Persona System** - Rich AI character interactions with personality traits
- ✅ **Scene Management** - Visual scene progression with AI-generated images
- ✅ **Publishing System** - Marketplace for sharing scenarios
- ✅ **Improved Error Handling** - Comprehensive error responses and logging

### Version 1.0.0 (Legacy)
- Basic agent and scenario management
- Simple simulation execution
- User authentication and profiles

---

## Support

For API support and questions:
- **Documentation:** [GitHub Repository](https://github.com/HendrikKrack/ai-agent-education-platform)
- **Issues:** Create an issue on GitHub
- **Integration Guide:** See `CHAT_ORCHESTRATOR_INTEGRATION.md`

---

**Legend:**
- 🔒 = Authentication required 