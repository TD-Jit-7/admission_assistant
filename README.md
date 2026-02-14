# 🎓 AI University Admission Assistant

An intelligent conversational AI system that helps Bangladeshi students navigate the university admission process through personalized guidance and recommendations.

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://admission-assistant-two.vercel.app/)
[![Video Demo](https://img.shields.io/badge/Video-Demo-red)](https://drive.google.com/file/d/1SphshV8SAkfcdu86iGF1qTvP0npHoJr5/view?usp=sharing)

##  Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Setup Instructions](#setup-instructions)
- [Deployment](#deployment)
- [Demo](#demo)
- [Project Structure](#project-structure)


##  Overview

This project implements a web-based AI agent that assists Bangladeshi students with university admission guidance. The system uses conversational AI to:
- Understand student queries in natural language
- Extract and store student information automatically
- Provide personalized university recommendations
- Filter universities based on GPA, department, and preferences

**Live Application:** [https://admission-assistant-two.vercel.app/](https://admission-assistant-two.vercel.app/)

**Demo Video:** [Watch on Google Drive](https://drive.google.com/file/d/1SphshV8SAkfcdu86iGF1qTvP0npHoJr5/view?usp=sharing)

##  Features

### Core Functionality
- 💬 **Natural Language Chat Interface** - Intuitive conversation flow
- 🎯 **Personalized Recommendations** - Based on GPA, academic group, and preferences
- 💾 **Automatic Data Extraction** - Extracts student info from conversation using regex
- 📊 **SQLite Database** - Stores up to 20 student profiles
- 🔍 **University Filtering** - By department, type (public/private), and admission status
- ⚡ **Fast Responses** - Sub-2-second response time using Groq AI

### Technical Features
- Responsive React frontend
- RESTful API backend
- Real-time chat updates
- Error handling and validation
- CORS-enabled for cross-origin requests

##  Technology Stack

### Frontend
- **Framework:** React.js 18
- **Styling:** CSS3 with custom components
- **HTTP Client:** Axios
- **Deployment:** Vercel

### Backend
- **Framework:** FastAPI (Python)
- **AI Model:** Groq Llama 3.3 70B
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Server:** Uvicorn
- **Deployment:** Render.com

### Development Tools
- Git & GitHub for version control
- VS Code for development
- Python 3.11
- Node.js 18+

##  System Architecture
```
┌─────────────┐         ┌─────────────┐          ┌─────────────┐
│   React     │────────▶│   FastAPI   │────────▶│   Groq AI   │
│  Frontend   │◀────────│   Backend   │◀────────│   (LLM)     │
└─────────────┘         └─────────────┘          └─────────────┘
                              │
                              ▼
                        ┌─────────────┐
                        │   SQLite    │
                        │  Database   │
                        └─────────────┘
```

### Request Flow
1. User sends message through React chat interface
2. Frontend makes POST request to `/chat` endpoint
3. Backend extracts student information using regex patterns
4. Data is saved to SQLite database
5. Backend constructs prompt with university data and student context
6. Groq AI generates personalized response
7. Response is sent back to frontend and displayed

##  Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- Groq API Key (free at [console.groq.com](https://console.groq.com))

### Backend Setup
```bash
# Clone repository
git clone https://github.com/TD-Jit-7/admission_assistant.git
cd admission_assistant/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_key_here" > .env

# Run backend
uvicorn main:app --reload
```

Backend will run at: `http://localhost:8000`

### Frontend Setup
```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Update API URL in src/App.js (line 38)
# Change to: http://localhost:8000

# Run frontend
npm start
```

Frontend will run at: `http://localhost:3000`

##  Deployment

### Backend (Render.com)
1. Create new Web Service
2. Connect GitHub repository
3. Set root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variable: `GROQ_API_KEY`

### Frontend (Vercel)
1. Import GitHub repository
2. Framework preset: Create React App
3. Root directory: `frontend`
4. Deploy

Update `frontend/src/App.js` with production backend URL before deploying.

##  Demo

**Live Application:** [https://admission-assistant-two.vercel.app/](YOUR_VERCEL_URL)

**Video Demonstration:** [Watch on Google Drive](YOUR_VIDEO_LINK)

The demo video includes:
- System overview and architecture
- Live chat demonstration
- Student data extraction and storage
- Personalized recommendation flow
- Challenges faced and solutions implemented

##  Project Structure
```
admission-assistant/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # SQLAlchemy models
│   ├── universities.json       # University dataset (15 universities)
│   ├── requirements.txt        # Python dependencies
│   ├── runtime.txt            # Python version specification
│   └── students.db            # SQLite database (auto-generated)
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main React component
│   │   ├── App.css            # Styling
│   │   └── index.js           # React entry point
│   ├── public/
│   └── package.json           # Node dependencies
├── .gitignore
└── README.md
```



##  Acknowledgments

- Groq for providing free AI API access
- Anthropic's Claude for development assistance
- Render and Vercel for free hosting platforms

---


