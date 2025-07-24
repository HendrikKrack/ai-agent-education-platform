# Scenario Builder Architecture

## Overview

The Scenario Builder is a React-based frontend interface that enables users to create interactive business case study simulations. It integrates with the PDF parser backend to automatically generate scenarios from uploaded documents, while providing manual editing capabilities for personas, scenes, and learning objectives.

## Architecture Flow

```mermaid
graph TD
    A[PDF Upload] --> B[Form Data Processing]
    B --> C[Backend API Call]
    C --> D[AI Processing Response]
    D --> E[State Management]
    E --> F[UI Rendering]
    
    E --> G[Personas State]
    E --> H[Scenes State]
    E --> I[Form Fields State]
    
    G --> J[PersonaCard Components]
    H --> K[SceneCard Components]
    I --> L[Information Accordion]
    
    J --> M[Modal Editing]
    K --> N[Modal Editing]
    
    F --> O[Three Main Accordions]
    O --> P[Information Section]
    O --> Q[Personas Section]
    O --> R[Timeline Section]
    
    M --> S[Trait Sliders & Goals]
    N --> T[Scene Details & Images]
    
    style A fill:#e1f5fe
    style F fill:#c8e6c9
    style M fill:#fff3e0
    style N fill:#fff3e0
    style O fill:#f3e5f5
```

## Key Components

### 1. **File Upload System**
- Drag-and-drop PDF upload interface
- File validation and preview
- Context files support for additional materials
- Visual feedback for upload states

### 2. **State Management**
- `personas`: Permanent persona data with traits and goals
- `tempPersonas`: Draft personas being created/edited
- `scenes`: Timeline scenes with descriptions and images
- Form fields: `name`, `description`, `learningOutcomes`

### 3. **Three-Section Accordion Layout**
- **Information**: Core scenario details and learning outcomes
- **Personas**: Character management with personality traits
- **Timeline**: Sequential scene creation with visual assets

### 4. **Modal Editing System**
- Full-screen editing for personas and scenes
- Real-time trait adjustment with sliders
- Image preview and persona selection
- Save/cancel functionality with validation

### 5. **Component Architecture**
```typescript
ScenarioBuilder (Main Container)
├── Modal (Overlay System)
├── PersonaCard (Character Display/Edit)
├── SceneCard (Timeline Scene Management)
└── Accordion Sections
    ├── Information (Form Fields)
    ├── Personas (Character Grid)
    └── Timeline (Scene Sequence)
```

## Data Processing Flow

### 1. **PDF to Personas Conversion**
- Filters out main character (student role)
- Maps AI personality traits to 1-5 scale sliders
- Formats goals and background descriptions
- Handles both temporary and permanent persona states

### 2. **Scene Generation Processing**
- Sorts scenes by sequence order
- Associates personas with each scene
- Integrates generated images from DALL-E
- Maintains user goals and descriptions

### 3. **Real-time State Updates**
- Immediate UI feedback for all changes
- Separate handling of draft vs. saved content
- Automatic form population from AI results

## UI/UX Features

- **Responsive Design**: Works across desktop and tablet devices
- **Visual Feedback**: Loading states, progress bars, and success indicators
- **Intuitive Editing**: Click-to-edit cards with modal overlays
- **Drag-and-Drop**: Modern file upload experience
- **Accessibility**: Proper ARIA labels and keyboard navigation

## API Integration

`POST /api/parse-pdf/` - Sends PDF and context files, receives structured scenario data with personas, scenes, and metadata for immediate UI population. 