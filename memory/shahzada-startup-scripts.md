# ClawForge - Start All Services Script

**File:** `start_all.sh`

## Purpose
Bash script to start both backend and frontend services.

## Usage
```bash
bash start_all.sh
```

## What It Does

### 1. Creates Workspace Structure
```bash
mkdir -p workspace/{tasks,downloads,output,quarantine,logs,memory}
```

### 2. Starts Backend
```bash
cd backend
pip install fastapi uvicorn psutil sqlalchemy aiofiles python-docx openpyxl reportlab -q
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
cd ..
```

### 3. Starts Frontend
```bash
cd frontend
npm install -q
npm run dev &
FRONTEND_PID=$!
cd ..
```

### 4. Displays Connection Info
```
Dashboard  → http://127.0.0.1:7860
API        → http://127.0.0.1:8000
API Docs   → http://127.0.0.1:8000/docs
Ollama     → ollama serve (run separately)
```

## Services Started
- **Backend:** FastAPI on port 8000
- **Frontend:** React dev server on port 7860

## To Stop
Press `Ctrl+C` to stop all services.

---

## PROJECT SHAHZADA - COMPLETE

### All Scripts Received

| Script | Purpose | Platform |
|--------|---------|----------|
| start_backend.ps1 | Start backend only | Windows |
| start_all.sh | Start all services | Linux/Mac |

---

## COMPLETE PROJECT RECEIVED

### Backend Files (Python)
1. identity.py - Core configuration
2. file_manager.py - Workspace operations
3. planner.py - Task planning
4. ollama_client.py - Ollama integration
5. tools.py - ToolRouter + 26 tools
6. memory.py - MemoryVault
7. task_manager.py - Task lifecycle
8. api.py - FastAPI backend
9. Task_1_setup_validator.py - Initialization

### Frontend Files (React)
10. App.jsx - Complete dashboard UI

### Scripts
11. start_backend.ps1 - Windows startup
12. start_all.sh - Linux/Mac startup

---

## Ready for Implementation

**All code received and saved to memory.**

**Waiting for your command to begin implementation.**
