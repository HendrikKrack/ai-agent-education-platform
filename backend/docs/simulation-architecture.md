# Sequential Timeline Simulation Architecture

## Overview
This document outlines the architecture for the sequential timeline simulation system where users progress through database-driven scenarios, interacting with AI personas to achieve specific goals at each scene.

## Core Architecture Flow

```mermaid
graph TD
    A[User enters Chat Simulation] --> B[Load Scenario from Database]
    B --> C[Initialize Simulation State]
    C --> D[Display Scene 1 Context]
    
    D --> E[User Interacts with AI Personas]
    E --> F{Goal Achieved?}
    
    F -->|No| G[AI Provides Guidance/Hints]
    G --> H[Track Attempt Count]
    H --> I{Max Attempts?}
    I -->|No| E
    I -->|Yes| J[Force Progress with Summary]
    
    F -->|Yes| K[Scene Complete - Show Results]
    K --> L{More Scenes?}
    L -->|Yes| M[Progress to Next Scene]
    M --> N[Update Timeline Position]
    N --> D
    
    L -->|No| O[Simulation Complete]
    O --> P[Show Final Results & Analytics]
    
    subgraph "Database Schema"
        Q[Scenarios Table]
        R[Scenes Table - Sequential Order]
        S[Personas Table - Per Scene]
        T[User Progress Table]
        U[Conversation Logs]
    end
    
    subgraph "AI Simulation Engine"
        V[Scene Context Manager]
        W[Persona AI Agents]
        X[Goal Validation System]
        Y[Progress Tracker]
        Z[Hint Generation]
    end
    
    B --> Q
    D --> V
    E --> W
    F --> X
    H --> Y
    G --> Z
    
    style A fill:#e1f5fe
    style O fill:#c8e6c9
    style P fill:#c8e6c9
    style F fill:#fff3e0
    style I fill:#fff3e0
```

## Technical Architecture & Data Flow

```mermaid
graph LR
    subgraph "Frontend - Chat Simulation UI"
        A[Scene Header<br/>Timeline Progress]
        B[AI Persona Chat<br/>Multiple Agents]
        C[Goal Panel<br/>Current Objective]
        D[Progress Tracker<br/>Attempts/Hints]
        E[Navigation<br/>Scene Controls]
    end
    
    subgraph "Backend API Endpoints"
        F["/api/simulation/start<br/>{scenario_id}"]
        G["/api/simulation/scene<br/>{scene_id}"]
        H["/api/simulation/chat<br/>{message, scene_id}"]
        I["/api/simulation/validate-goal<br/>{scene_id, user_input}"]
        J["/api/simulation/progress<br/>{next_scene}"]
    end
    
    subgraph "AI Processing Layer"
        K[Scene Context Loader<br/>Loads personas & goals]
        L[Multi-Persona Chat Engine<br/>GPT-4o with context]
        M[Goal Achievement Validator<br/>Checks completion criteria]
        N[Hint Generator<br/>Provides guidance]
        O[Progress Manager<br/>Handles scene transitions]
    end
    
    subgraph "Database Tables"
        P[scenarios<br/>id, title, description]
        Q[scenes<br/>id, scenario_id, order, title<br/>context, goal, max_attempts]
        R[scene_personas<br/>scene_id, persona_id, role]
        S[personas<br/>id, name, personality, avatar]
        T[user_progress<br/>user_id, scenario_id, current_scene<br/>attempts, completed_scenes]
        U[conversation_logs<br/>session_id, scene_id, messages<br/>timestamp, persona_speaker]
    end
    
    A --> F
    B --> H
    C --> I
    E --> J
    
    F --> K
    H --> L
    I --> M
    J --> O
    
    K --> P
    K --> Q
    L --> R
    L --> S
    M --> Q
    O --> T
    H --> U
    
    style A fill:#e3f2fd
    style B fill:#e3f2fd
    style C fill:#fff3e0
    style D fill:#f3e5f5
    style K fill:#e8f5e8
    style L fill:#e8f5e8
    style M fill:#fff3e0
    style P fill:#fce4ec
    style Q fill:#fce4ec
```

## Conversation Flow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Backend API
    participant AI as AI Engine
    participant DB as Database
    
    U->>F: Start Simulation (scenario_id)
    F->>API: POST /api/simulation/start
    API->>DB: Load scenario & first scene
    API->>AI: Initialize scene context
    AI->>API: Scene setup complete
    API->>F: Scene data + personas + goal
    F->>U: Display scene context & goal
    
    loop For Each User Message
        U->>F: Send message to AI persona
        F->>API: POST /api/simulation/chat
        API->>AI: Process with persona context
        AI->>API: Generate persona response
        API->>DB: Log conversation
        API->>F: AI response + metadata
        F->>U: Display AI response
        
        F->>API: POST /api/simulation/validate-goal
        API->>AI: Check if goal achieved
        AI->>API: Goal status + reasoning
        
        alt Goal Achieved
            API->>F: Goal complete + next scene
            F->>U: Success message + progress
            F->>API: POST /api/simulation/progress
            API->>DB: Update user progress
            API->>F: Next scene data
        else Goal Not Achieved
            alt Max Attempts Reached
                API->>AI: Generate hint/guidance
                AI->>API: Helpful hint
                API->>F: Hint + attempt count
                F->>U: Show hint + try again
            else Force Progress
                API->>F: Summary + force next scene
                F->>U: Scene summary + auto-progress
            end
        end
    end
    
    API->>F: Simulation complete
    F->>U: Final results & analytics
```

## Key Features

### Database-Driven Simulation Flow
- **Scenarios** contain multiple **Scenes** in sequential order
- Each **Scene** has specific **Goals**, **Personas**, and **Context**
- **User Progress** tracks current scene, attempts, and completion status

### Multi-Persona AI Conversations
- Multiple AI agents per scene (e.g., CEO, Customer, Analyst)
- Each persona has distinct personality and role context
- Users must interact with different personas to gather information/achieve goals

### Goal-Based Progression System
- **Clear Objectives**: Each scene has specific, measurable goals
- **Validation Engine**: AI determines when goals are achieved
- **Attempt Tracking**: Limited tries with hints/guidance
- **Forced Progression**: Auto-advance after max attempts with summary

### Enhanced User Experience
- **Timeline Visualization**: Show progress through scenario scenes
- **Goal Panel**: Always visible current objectives
- **Persona Indicators**: Clear identification of which AI is speaking
- **Progress Feedback**: Attempts, hints, completion status

## Implementation Plan

### Backend Changes
1. **New API Endpoints**: Start simulation, scene management, goal validation
2. **AI Engine Enhancement**: Multi-persona context management
3. **Database Extensions**: User progress tracking, conversation logs
4. **Goal Validation**: AI-powered achievement detection

### Frontend Changes
1. **Scene-Based UI**: Replace free chat with structured scenes
2. **Timeline Component**: Visual progress indicator
3. **Goal Dashboard**: Always-visible objectives panel
4. **Persona Management**: Multiple AI avatars and context switching

### Data Flow
1. **Load Scenario** → **Initialize First Scene** → **Set Goals**
2. **User Chats with Personas** → **AI Validates Goals** → **Progress or Retry**
3. **Scene Complete** → **Load Next Scene** → **Repeat Until Simulation End** 