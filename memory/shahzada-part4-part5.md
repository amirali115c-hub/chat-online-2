# PROJECT SHAHZADA - PART 4: Security Layer + PART 5: Final Delivery Pipeline

**Status:** ADDITIONAL CODE RECEIVED
**Date:** 2026-02-18

---

## PART 4: Security Layer + Malware Protection + Permission Gating

This layer prevents dangerous actions, sandboxes risky commands, and quarantines suspicious files. Integrates with tools.py, task_manager.py, and dashboard.

---

## 4.1 security_manager.py - Security Manager

**File:** `backend/security_manager.py`

### Purpose
Central security enforcement layer:
- Command pattern blocking
- File quarantine
- Risk event logging
- Execution safety checks

### Key Components

#### Blocked Patterns
```python
self.blocked_patterns = [
    r"rm\s+-rf",           # Force remove
    r"del\s+/s",           # Windows delete
    r"format",              # Disk format
    r"diskpart",            # Disk partition manipulation
    r"shutdown",            # System shutdown
    r"reboot",              # System reboot
    r"reg\s+add",          # Registry add
    r"reg\s+delete",       # Registry delete
    r"taskkill",            # Kill processes
    r"Invoke-Expression",   # PowerShell execution
    r"certutil",            # Certificate utility (often malware)
    r"bitsadmin",           # Background intelligent transfer
    r"curl\s+\|",          # Pipe to bash (download + execute)
]
```

### SecurityManager Class

```python
class SecurityManager:
    def __init__(self, workspace="./workspace", threshold=50):
        self.workspace = workspace
        self.quarantine_dir = os.path.join(workspace, "quarantine")
        self.risk_engine = RiskEngine()
        self.blocked_patterns = [...]  # See above
```

#### Methods

##### check_command(command: str) -> bool
```python
def check_command(self, command: str):
    """
    Scans command for blocked patterns.
    Returns False if dangerous pattern found.
    Logs risk event if blocked.
    """
```

##### quarantine_file(filepath: str) -> dict
```python
def quarantine_file(self, filepath):
    """
    Moves suspicious file to workspace/quarantine/
    Returns: {"status": "quarantined", "file": destination_path}
    """
```

##### safe_to_execute(command: str) -> bool
```python
def safe_to_execute(self, command: str):
    """
    Combined check:
    1. Command has no blocked patterns
    2. Risk score below threshold
    Returns True only if both pass.
    """
```

##### log_risk_event(task_id: str, action: str, details: str = "")
```python
def log_risk_event(self, task_id, action, details=""):
    """
    Logs security event to workspace/logs/security_log.jsonl
    Entry includes: timestamp, task_id, action, details, risk_score
    """
```

### RiskEngine Integration
- Checks threshold before execution
- Adds risk points for blocked commands
- Tracks cumulative risk score

---

## 4.2 Permission Layer

**File:** `backend/permissions.py`

### Purpose
Manages user approvals for risky actions.

### PermissionManager Class

```python
class PermissionManager:
    def __init__(self):
        self.permissions = {}
```

#### Methods

##### request_permission(tool_name: str, risk_level: int = 0) -> bool
```python
def request_permission(self, tool_name, risk_level=0):
    """
    Requests permission for a tool/action.
    risk_level used for UI prompt or audit log.
    Returns: True (auto-approved in demo) or False.
    """
    approved = True  # In production, dashboard prompts user
    self.permissions[tool_name] = approved
    return approved
```

##### check_permission(tool_name: str) -> bool
```python
def check_permission(self, tool_name):
    """
    Checks if tool/action is approved.
    Returns: permission status
    """
    return self.permissions.get(tool_name, self.request_permission(tool_name))
```

### Actions Requiring Permission
- Terminal commands outside sandbox
- UI automation (mouse, keyboard)
- Browser automation
- File writes outside workspace
- Downloads and network calls
- Code execution

---

## 4.3 Kill Switch / Emergency Stop

**File:** `backend/api.py` (endpoint)

### API Endpoint
```python
@router.post("/emergency/kill")
def kill_switch():
    """
    EMERGENCY KILL SWITCH:
    - Stops all running tasks
    - Disables all tools
    - Returns: {"status": "all tasks stopped", "message": "Kill switch activated"}
    """
    from backend.task_manager import TaskManager
    tm = TaskManager()
    for task_id in tm.tasks:
        tm.stop_task(task_id)
    return {"status": "all tasks stopped", "message": "Kill switch activated"}
```

### Frontend Integration
- Red button in dashboard header
- Confirmation dialog before activation
- Broadcasts kill_switch_activated event via WebSocket
- All tasks marked as SECURITY_BLOCKED

---

## 4.4 Quarantine Protocol

### Structure
```
workspace/quarantine/
├── suspicious_file.ext
└── suspicious_file.ext.manifest.json
```

### Manifest Contents
```json
{
    "original_path": "/path/to/file",
    "quarantine_path": "/workspace/quarantine/file",
    "reason": "Suspicious file type or blocked pattern",
    "timestamp": "2026-02-18T21:30:00Z"
}
```

### Workflow
1. SecurityManager detects suspicious file/command
2. File moved to quarantine/
3. Manifest created with metadata
4. Task marked as SECURITY_BLOCKED
5. Dashboard alerted

### Release Process
- User reviews quarantined files in dashboard
- User can approve release or delete permanently
- Released files moved back to original location

---

## 4.5 Risk Scoring Engine

**File:** `backend/risk_engine.py`

### Purpose
Assigns points to actions and tracks cumulative risk.

### Risk Points Table

| Action | Points |
|--------|---------|
| file_write | 1 |
| download | 5 |
| terminal_command | 4 |
| browser_automation | 6 |
| screen_control | 7 |
| blocked_command_attempt | 20 |

### RiskEngine Class

```python
class RiskEngine:
    def __init__(self, threshold=50):
        self.risk_score = 0
        self.threshold = threshold
```

#### Methods

##### add_risk(action: str, points: int)
```python
def add_risk(self, action, points):
    """
    Adds risk points for an action.
    Logs the risk event.
    """
    self.risk_score += points
```

##### check_threshold() -> bool
```python
def check_threshold(self):
    """
    Checks if risk score exceeds threshold.
    Returns: True if below threshold, False if exceeded.
    """
    return self.risk_score < self.threshold
```

##### get_score() -> int
```python
def get_score(self):
    """Returns current risk score."""
    return self.risk_score
```

### Threshold Behavior
- Default threshold: 50 points
- Exceeding threshold pauses task
- Requires user approval to continue
- Task marked as WAITING_APPROVAL

---

## PART 5: Final Delivery Pipeline + Task Reports + Project Generation

This part ensures structured outputs, security reports, and project scaffolding.

---

## 5.1 Task Output Structure

### Folder Structure
```
workspace/tasks/{task_id}/
├── plan.md              # Original execution plan
├── notes.md             # Reasoning and trace
├── output/              # Generated files
│   ├── document.docx
│   ├── spreadsheet.xlsx
│   ├── code.py
│   └── ...
├── logs.jsonl          # Execution logs
└── security_report.json # Security audit
```

### File Contents

#### plan.md
```markdown
# Task Plan: task_20260218_210000_abc123

## Goal
Write SEO blog about AI tools

## Subtasks
1. Research topic
2. Write outline
3. Draft content
4. Export to DOCX

## Permissions Required
- create_docx
```

#### notes.md
```markdown
# Notes: task_20260218_210000_abc123

## Reasoning
User wants professional tone...

## Execution Trace
- Started at 21:00
- Completed outline at 21:15
- Drafted content at 21:30
```

#### logs.jsonl
```jsonl
{"timestamp": "2026-02-18T21:00:00Z", "tool": "create_folder", "status": "success"}
{"timestamp": "2026-02-18T21:15:00Z", "tool": "write_file", "status": "success"}
```

---

## 5.2 Security Report JSON

**File:** `workspace/tasks/{task_id}/security_report.json`

### Structure
```json
{
    "task_id": "task_20260218_210000_abc123",
    "start_time": "2026-02-18T21:00:00Z",
    "end_time": "2026-02-18T21:45:00Z",
    "tools_used": ["read_file", "write_file", "create_docx"],
    "blocked_commands": [],
    "quarantined_files": [],
    "risk_score_final": 3,
    "approvals_requested": ["create_docx"],
    "approvals_granted": ["create_docx"]
}
```

### Generation Function
```python
def generate_security_report(task_id, task_logs, blocked_commands=[], quarantined_files=[]):
    import json, os
    from datetime import datetime

    report = {
        "task_id": task_id,
        "start_time": datetime.utcnow().isoformat(),
        "end_time": datetime.utcnow().isoformat(),
        "tools_used": [log.get("tool") for log in task_logs],
        "blocked_commands": blocked_commands,
        "quarantined_files": quarantined_files,
        "risk_score_final": 0  # fetch from risk_engine
    }

    folder = f"./workspace/tasks/{task_id}"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "security_report.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report
```

---

## 5.3 Project Generation Template

### Purpose
Auto-generate new project structures when requested.

### Generated Structure
```
{project_name}/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── api.py
│   ├── tools.py
│   ├── security_manager.py
│   ├── permissions.py
│   └── risk_engine.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles/
│   ├── package.json
│   └── vite.config.js
├── workspace/
│   ├── tasks/
│   ├── downloads/
│   ├── output/
│   ├── quarantine/
│   ├── logs/
│   └── memory/
├── requirements.txt
├── package.json
├── .env.example
├── .gitignore
└── README.md
```

### Generated Files

#### requirements.txt
```txt
fastapi>=0.100.0
uvicorn>=0.22.0
psutil>=5.9.0
sqlalchemy>=2.0.0
python-docx>=1.1.0
openpyxl>=3.1.0
reportlab>=4.0.0
aiofiles>=23.1.0
```

#### package.json (Frontend)
```json
{
  "name": "{project-name}",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0"
  }
}
```

#### .env.example
```env
# API Configuration
API_HOST=127.0.0.1
API_PORT=8000

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Security
SECURITY_MODE=LOCKED
RISK_THRESHOLD=50
```

#### README.md
```markdown
# {Project Name}

{Description}

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (optional, for LLM)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn api:app --host 127.0.0.1 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Access
- Dashboard: http://127.0.0.1:7860
- API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs

## Security Modes
- LOCKED: Text/code only, no terminal/browser/UI
- SAFE: Terminal + Python sandbox, approvals required
- DEVELOPER: Full workspace access, blocks dangerous commands

## License
MIT
```

---

## 5.4 Dashboard Integration (Final)

### Required Dashboard Features

#### Task Outputs View
- List all files in workspace/tasks/{task_id}/output/
- Download individual files
- Preview images/PDFs
- Copy code snippets

#### Security Events Panel
- Real-time security_log.jsonl display
- Filter by: blocked commands, quarantined files, risk events
- Acknowledge events

#### Quarantine Manager
- List quarantined files
- Show manifest for each
- Release or delete actions
- Bulk operations

#### Risk Score Display
- Current task risk score
- Risk threshold indicator
- Risk trend over time

#### Kill Switch
- Always-visible red button in header
- Confirmation dialog
- Broadcasts status to all connected clients
- Logs to kill_switch.log

#### WebSocket Events for Security
```javascript
{
  "event": "risk_threshold_exceeded",
  "data": {
    "task_id": "task_xxx",
    "risk_score": 55,
    "threshold": 50
  }
}

{
  "event": "quarantine_event",
  "data": {
    "task_id": "task_xxx",
    "file": "suspicious.exe",
    "reason": "Blocked file type"
  }
}

{
  "event": "security_blocked",
  "data": {
    "task_id": "task_xxx",
    "reason": "Dangerous command detected"
  }
}
```

---

## Summary: Complete Security + Delivery Pipeline

### PART 4 Components
1. security_manager.py - Command blocking + quarantine
2. permissions.py - Approval workflow
3. Kill Switch API - Emergency stop
4. Quarantine Protocol - Suspicious file handling
5. Risk Scoring Engine - Point-based risk tracking

### PART 5 Components
1. Task Output Structure - Standardized deliverables
2. Security Report JSON - Audit trail
3. Project Generation Template - Auto-scaffolding
4. Dashboard Integration - Real-time security display

---

## Confirmation

**PART 4 + PART 5 Received:** ✅

**Total Project Components:**
- PART 1: Core Identity + Workspace
- PART 2: Ollama Integration + Tools + Memory
- PART 3: Dashboard UI + Task Manager
- PART 4: Security Layer + Malware Protection
- PART 5: Final Delivery Pipeline

**All Code Saved to Memory:** ✅

**Ready for Implementation:** ✅

---

**Awaiting your command to begin implementation.**
