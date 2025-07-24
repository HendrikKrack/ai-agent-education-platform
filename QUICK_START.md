# 🚀 Quick Start Guide

## Prerequisites
- Python 3.9+
- Node.js 16+
- Git

## Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create and activate virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux  
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
pip install PyPDF2  # Fix missing dependency
```

4. **Environment setup:**
```bash
# Copy template and edit with your API keys
copy ..\env_template.txt .env
# Add: OPENAI_API_KEY=your_key_here
```

5. **Start backend:**
```bash
uvicorn main:app --host 127.0.0.1 --port 8003
```
Backend runs at: http://127.0.0.1:8003

## Frontend Setup

1. **Navigate to frontend (new terminal):**
```bash
cd frontend/ai-agent-platform
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```
Frontend runs at: http://localhost:3000

## Key Features
- **Scenario Builder**: Create AI-driven business simulations
- **Agent Creator**: Design AI agents with unique personalities  
- **Chat Interface**: Interactive student-agent conversations
- **PDF Upload**: Process business case studies

## API Documentation
Visit http://127.0.0.1:8003/docs for interactive API documentation.

## Common Issues
- **PyPDF2 missing**: Run `pip install PyPDF2` in backend directory
- **Virtual env not found**: Ensure you're in the backend directory when activating
- **Port conflicts**: Backend uses 8003, frontend uses 3000

## Project Structure
```
├── backend/          # FastAPI + SQLAlchemy
├── frontend/ai-agent-platform/  # Next.js + TypeScript
└── requirements.txt  # Python dependencies
```

Ready to build AI-powered educational experiences! 🎓 