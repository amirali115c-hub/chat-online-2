# ClawForge v4.0 - Production-Grade AI Agent System

## Quick Start

### Option 1: Double-Click (Easiest)
```
Double-click START.bat
```

### Option 2: Using Launcher (Recommended)
```bash
python launcher.py
```

### Option 3: Manual
```bash
# Terminal 1 - Backend
python backend/main.py --server

# Terminal 2 - Frontend
cd frontend && npm run dev
```

---

## Launcher Options

| Command | Description |
|---------|-------------|
| `python launcher.py` | Start both services |
| `python launcher.py --status` | Check if running |
| `python launcher.py --stop` | Stop all services |
| `python launcher.py --restart` | Restart services |

---

## Services

| Service | URL | Description |
|---------|-----|-------------|
| Backend | http://127.0.0.1:8000 | FastAPI server |
| Frontend | http://127.0.0.1:7860 | React dashboard |
| API Docs | http://127.0.0.1:8000/docs | Swagger documentation |

---

## Features

- **4 AI Models**: z-ai/glm5, qwen/qwen3.5-397b-a17b, NVIDIABuild-Autogen-60, deepseek-ai/deepseek-v3.2
- **Memory System**: Persistent JSON-based conversation memory
- **Web Search**: Brave Search API integration
- **Git Integration**: Status, commit, push operations
- **Text-to-Speech**: pyttsx3 voice synthesis
- **Task Planner**: Multi-step task planning
- **File Editor**: Search/replace file editing

---

## API Keys

API keys are stored in `backend/api.py`. NEVER commit API keys to version control.

---

## Architecture

```
ClawForge/
├── backend/
│   ├── api.py          # FastAPI server
│   ├── features.py     # All feature modules
│   ├── nvidia_client.py
│   ├── glm_client.py
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── App.jsx    # React dashboard
│   │   └── App.css
│   └── ...
└── launcher.py         # Permanent service launcher
```
