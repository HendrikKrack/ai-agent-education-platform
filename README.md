# 🎓 AI Agent Education Platform

An innovative educational platform that transforms business case studies into immersive AI-powered simulations. Upload PDF case studies, let AI extract key figures and scenarios, then engage students in **linear simulation experiences** with dynamic **ChatOrchestrator** system and intelligent **AI persona interactions**.

![AI Agent Education Platform](https://img.shields.io/badge/AI-Education-blue?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-TypeScript-000000?style=for-the-badge&logo=nextdotjs)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=for-the-badge&logo=openai)

## 🌟 Features

### 📄 **PDF-to-Simulation Pipeline**
- **Intelligent PDF Processing**: Upload Harvard Business Review cases or any business case study PDF
- **AI Content Analysis**: LlamaParse + OpenAI GPT-4 extract scenarios, key figures, and learning objectives
- **Automatic Persona Generation**: AI creates realistic business personas with personality traits and backgrounds
- **Scene Creation**: Generate sequential learning scenes with clear objectives and visual imagery

### 🎭 **ChatOrchestrator System**
- **Linear Simulation Flow**: Structured multi-scene progression with clear learning objectives
- **AI Persona Interactions**: Dynamic conversations with AI characters based on personality traits
- **Smart Command System**: Built-in commands (`begin`, `help`, `@mentions`) for natural interaction
- **Adaptive Difficulty**: Intelligent hint system and scene progression based on student performance

### 🎮 **Immersive Learning Experiences**
- **Multi-Scene Progression**: Students advance through carefully designed business scenarios
- **Goal-Oriented Learning**: Each scene has specific objectives and success criteria
- **Real-Time Feedback**: AI assesses understanding and provides contextual hints
- **Progress Tracking**: Comprehensive analytics on learning outcomes and engagement

### 🏪 **Community Marketplace**
- **Scenario Sharing**: Publish successful simulations for the educational community
- **Content Discovery**: Browse scenarios by industry, difficulty, and user ratings
- **Remix & Customize**: Clone and adapt existing scenarios for specific needs
- **Quality Assurance**: Community ratings and reviews ensure high-quality content

### 🎨 **Modern UI/UX**
- **Next.js 14 with TypeScript**: Server-side rendering for optimal performance
- **Tailwind CSS + shadcn/ui**: Professional, accessible component library
- **Responsive Design**: Seamless experience across desktop, tablet, and mobile
- **Real-Time Chat Interface**: Immersive conversation experience with AI personas

## 🏗️ Architecture

```mermaid
graph TB
    A[Next.js Frontend] --> B[FastAPI Backend]
    B --> C[PostgreSQL Database]
    B --> D[OpenAI GPT-4]
    B --> E[LlamaParse API]
    B --> F[ChatOrchestrator]
    
    subgraph "Frontend (Next.js + TypeScript)"
        G[PDF Upload Interface]
        H[Scenario Builder]
        I[Chat-Box Experience]
        J[Marketplace]
    end
    
    subgraph "Backend (FastAPI + Python)"
        K[PDF Processing API]
        L[Linear Simulation API]
        M[ChatOrchestrator Engine]
        N[Publishing System]
    end
    
    subgraph "AI Processing Layer"
        O[PDF Analysis]
        P[Persona Generation]
        Q[Scene Creation]
        R[Image Generation]
    end
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v18 or higher)
- **Python** (3.11 or higher)
- **PostgreSQL** (v14 or higher)
- **OpenAI API Key** (for ChatOrchestrator and content generation)
- **LlamaParse API Key** (for PDF processing)

### 1. Clone the Repository
```bash
git clone https://github.com/HendrikKrack/ai-agent-education-platform.git
cd ai-agent-education-platform
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install PyPDF2  # Additional dependency for PDF processing

# Set up environment variables
copy env_template.txt .env
# Edit .env with your API keys:
# OPENAI_API_KEY=your_openai_api_key
# LLAMAPARSE_API_KEY=your_llamaparse_api_key
# DATABASE_URL=postgresql://username:password@localhost:5432/ai_education

# Create database tables
python recreate_db.py

# Start the backend server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at **http://localhost:8000**

### 3. Frontend Setup
```bash
# Navigate to frontend directory (in a new terminal)
cd frontend/ai-agent-platform

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at **http://localhost:3000**

## 🔧 Environment Configuration

### Backend (.env)
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ai_education

# AI Service API Keys
OPENAI_API_KEY=your_openai_api_key_here
LLAMAPARSE_API_KEY=your_llamaparse_api_key_here

# Application Settings
SECRET_KEY=your_secret_key_here
ENVIRONMENT=development
DEBUG=true

# Optional: Image Generation
DALLE_API_KEY=your_dalle_api_key_here
```

### Database Setup
1. Create a PostgreSQL database named `ai_education`
2. Update the `DATABASE_URL` in your `.env` file
3. Run `python recreate_db.py` to create tables
4. The system will automatically create default scenarios

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Key Endpoints
```
# PDF Processing & Scenario Creation
POST /api/parse-pdf/                    # Upload and process PDF case study
GET  /scenarios/                        # List all scenarios
GET  /scenarios/{id}                    # Get scenario with personas and scenes

# Linear Simulation System
POST /api/simulation/start              # Initialize ChatOrchestrator simulation
POST /api/simulation/linear-chat        # Chat with AI personas in simulation

# Legacy Business Simulation
POST /api/simulate/                     # Phase-based business simulation

# Community Marketplace
POST /api/publishing/publish-scenario   # Publish scenario to marketplace
GET  /api/publishing/marketplace        # Browse published scenarios

# System Health
GET  /health/                           # System health check
```

## 🎓 Usage Guide

### For Educators

1. **Upload Business Case Study**
   - Upload PDF case studies (Harvard Business Review, custom cases)
   - AI automatically extracts scenarios, key figures, and learning objectives
   - Review and customize generated personas and scenes

2. **Launch Linear Simulation**
   - Students progress through structured scenes with clear objectives
   - ChatOrchestrator manages multi-persona interactions
   - Monitor student progress and learning outcomes

3. **Publish to Community**
   - Share successful scenarios with other educators
   - Set difficulty levels, categories, and learning objectives
   - Receive community feedback and ratings

### For Students

1. **Start Simulation Experience**
   - Review scenario overview and learning objectives
   - Understand your role in the business challenge
   - Meet AI personas and their backgrounds

2. **Engage with ChatOrchestrator**
   - Type `begin` to start the simulation
   - Use `@mentions` to interact with specific personas
   - Type `help` for available commands and guidance

3. **Progress Through Scenes**
   - Complete objectives in each scene to advance
   - Receive real-time feedback and hints
   - Build understanding through natural conversation

### Example Simulation Flow
```
Student: begin
ChatOrchestrator: Welcome to KasKazi Network Strategic Challenge...

Student: @wanjohi What are your main concerns about seasonal contracts?
Wanjohi: As the founder, I'm deeply concerned about our revenue gaps...

Student: What alternatives have you considered?
ChatOrchestrator: [Multiple personas respond with different perspectives]

Student: help
ChatOrchestrator: Available commands: @mention, progress, hint...
```

## 🛠️ Technology Stack

### Frontend
- **Next.js 14** with TypeScript and App Router
- **Tailwind CSS** for utility-first styling
- **shadcn/ui** for modern, accessible components
- **React Hook Form** for form management
- **Zustand** for state management

### Backend
- **FastAPI** with async Python for high performance
- **SQLAlchemy** ORM with PostgreSQL
- **Pydantic** for data validation and serialization
- **Uvicorn** ASGI server with hot reloading

### AI Services
- **OpenAI GPT-4** for ChatOrchestrator and content generation
- **LlamaParse** for advanced PDF processing and content extraction
- **AI Image Generation** for scene visualization
- **Custom ChatOrchestrator** for linear simulation management

### Database
- **PostgreSQL** with JSONB support for flexible data storage
- **Alembic** for database migrations
- **Connection pooling** for optimal performance

## 📁 Project Structure

```
ai-agent-education-platform/
├── backend/
│   ├── main.py                       # FastAPI application entry point
│   ├── database/
│   │   ├── models.py                 # SQLAlchemy models (scenarios, personas, scenes)
│   │   ├── schemas.py                # Pydantic schemas for API validation
│   │   └── migrations/               # Database migration files
│   ├── api/
│   │   ├── parse_pdf.py             # PDF processing endpoints
│   │   ├── simulation.py            # Linear simulation endpoints
│   │   ├── chat_orchestrator.py     # ChatOrchestrator logic
│   │   └── publishing.py            # Marketplace publishing
│   ├── services/
│   │   └── simulation_engine.py     # Core simulation business logic
│   └── docs/                        # Comprehensive API documentation
├── frontend/ai-agent-platform/
│   ├── app/
│   │   ├── chat-box/                # Linear simulation interface
│   │   ├── scenario-builder/        # PDF upload and scenario creation
│   │   ├── marketplace/             # Community scenario discovery
│   │   └── dashboard/               # User progress and analytics
│   ├── components/
│   │   ├── ui/                      # shadcn/ui components
│   │   ├── PersonaCard.tsx          # AI persona display components
│   │   └── SceneCard.tsx            # Scene progression UI
│   └── lib/                         # Utility functions and API clients
├── CHAT_ORCHESTRATOR_INTEGRATION.md # Integration documentation
├── QUICK_START.md                   # Quick setup guide
└── README.md                        # This file
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- **Python**: Follow PEP 8 with Black formatting and type hints
- **TypeScript**: Use Prettier with ESLint and strict TypeScript
- **Commits**: Use conventional commits format
- **Testing**: Write tests for new features and maintain 80%+ coverage

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **OpenAI GPT-4** for powering intelligent ChatOrchestrator interactions
- **LlamaParse** for advanced PDF processing and content extraction
- **shadcn/ui** for beautiful, accessible React components
- **FastAPI** for high-performance async Python web framework
- **Next.js** for modern React development with server-side rendering

## 📞 Support

- **Quick Start Guide**: [QUICK_START.md](QUICK_START.md)
- **Integration Documentation**: [CHAT_ORCHESTRATOR_INTEGRATION.md](CHAT_ORCHESTRATOR_INTEGRATION.md)
- **API Reference**: [backend/docs/API_Reference.md](backend/docs/API_Reference.md)
- **Architecture Documentation**: [backend/docs/architecture/](backend/docs/architecture/)
- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

## 🗺️ Roadmap

### Phase 1: Core Platform (✅ Complete)
- [x] **PDF-to-Simulation Pipeline** with AI processing
- [x] **ChatOrchestrator Integration** with linear simulation flow
- [x] **Multi-Scene Progression** with goal tracking
- [x] **Community Marketplace** with publishing system

### Phase 2: Enhanced Learning (🚧 In Progress)
- [ ] **Advanced Analytics Dashboard** for educators
- [ ] **Learning Outcome Assessment** with AI evaluation
- [ ] **Multi-User Simulations** for collaborative learning
- [ ] **Voice Interaction** with AI personas

### Phase 3: Enterprise Features (🔮 Planned)
- [ ] **LMS Integration** (Canvas, Blackboard, Moodle)
- [ ] **SSO Authentication** for institutional use
- [ ] **White-Label Solutions** for educational institutions
- [ ] **Mobile Native Apps** (iOS/Android)

### Phase 4: Advanced AI (🔮 Future)
- [ ] **Custom Model Training** for domain-specific scenarios
- [ ] **VR/AR Integration** for immersive experiences
- [ ] **Multi-Language Support** with i18n
- [ ] **Real-Time Collaboration** with WebRTC

---

<div align="center">

**[⭐ Star this repository](../../stargazers) • [🐛 Report Bug](../../issues) • [✨ Request Feature](../../issues)**

**Transform business education with AI-powered simulations**

Made with ❤️ for educators and students worldwide

</div> 