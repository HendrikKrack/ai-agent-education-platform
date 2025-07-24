# PDF Parser Architecture

## Overview

The PDF parser transforms business case study PDFs into interactive educational scenarios through a multi-stage AI processing pipeline. It extracts content, generates personas, creates timeline scenes, and produces visual assets for immersive learning experiences.

## Architecture Flow

```mermaid
graph TD
    A[PDF Upload] --> B[LlamaParse API]
    B --> C[Content Cleaning]
    C --> D[First AI Call - GPT-4o]
    D --> E[Extract Personas & Metadata]
    E --> F[Second AI Call - GPT-4o]
    F --> G[Generate Timeline Scenes]
    G --> H[DALL-E Image Generation]
    H --> I[Structured JSON Response]
    
    D --> J[Title, Description, Student Role]
    D --> K[Key Figures with Traits]
    D --> L[Learning Outcomes]
    
    F --> M[Scene 1: Crisis Assessment]
    F --> N[Scene 2: Root Cause Analysis] 
    F --> O[Scene 3: Strategy Development]
    F --> P[Scene 4: Implementation]
    
    H --> Q[Professional Scene Images]
    
    style A fill:#e1f5fe
    style I fill:#c8e6c9
    style D fill:#fff3e0
    style F fill:#fff3e0
    style H fill:#f3e5f5
```

## Key Components

### 1. **PDF Processing** (`LlamaParse`)
- Converts PDF to clean markdown
- Handles complex layouts and tables
- Preserves document structure

### 2. **Content Preprocessing**
- Removes metadata and formatting artifacts
- Extracts title from headers
- Cleans and normalizes text content

### 3. **Two-Stage AI Processing**
- **Stage 1**: Extracts personas, roles, and case overview
- **Stage 2**: Generates 4 interactive timeline scenes with specific goals

### 4. **Image Generation** (`DALL-E 3`)
- Creates professional scene illustrations
- Parallel processing for performance
- Business-appropriate visual style

### 5. **Response Structure**
```json
{
  "title": "Case Study Title",
  "description": "Comprehensive case overview",
  "student_role": "Decision maker role",
  "key_figures": [...], // Personas with traits
  "scenes": [...],      // Timeline with images
  "learning_outcomes": [...]
}
```

## Performance Features

- **Parallel Processing**: Multiple files and images processed simultaneously
- **Robust Error Handling**: Fallback scenes if AI generation fails
- **Comprehensive Logging**: Detailed debugging for troubleshooting
- **Token Optimization**: Efficient prompt engineering for consistent results

## API Endpoint

`POST /api/parse-pdf/` - Accepts multipart form data with PDF files and returns structured scenario data ready for the frontend scenario builder. 