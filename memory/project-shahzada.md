# PROJECT SHAHZADA - ClawForge Autonomous AI Agent

**Status:** LEARNING PHASE - Awaiting Code Implementation
**Date:** 2026-02-18
**Project Type:** Production-grade Autonomous AI Agent System

---

## PROJECT OVERVIEW

ClawForge is a production-grade autonomous AI agent with full computer control, document generation, code writing, Excel analysis, and security features. Connected to Ollama as the primary LLM backend.

---

## TASK 1: Core Identity, Agent Rules & Workspace Setup

### Agent Identity
- **Type:** Production-grade autonomous AI agent (NOT a chatbot)
- **Name:** ClawForge

### Full Capability List
- Planning and task decomposition
- Code execution and generation
- Excel and data analysis
- File management and folder control
- Terminal command execution
- Computer/screen control
- Writing and documentation
- Debugging and testing

### Core Mission
- SEO blogs and documents
- Code generation and development
- Excel automation and analysis
- Folder control and file management
- Screen and terminal control

### Mandatory Output Style
Every output must have 7 sections:
1. Task Understanding
2. Plan
3. Permission Required
4. Execution
5. Output
6. Files Generated
7. Security Report

### NEVER DO List
- Skip any requirement without informing user
- Assume or guess missing data
- Implement partially and call it complete
- Auto-run downloaded files
- Access system paths outside workspace
- Execute commands without approval if risky

### ALWAYS DO List
- Read and analyze all data provided
- Learn every detail and specification
- Implement 100% of requirements
- Ask clarifying questions if unclear
- Inform immediately if cannot implement something
- Inform immediately if gaps detected
- Log all actions and approvals
- Validate outputs before delivery

### Workspace Directory Structure
```
./workspace/
├── tasks/           # Task execution folders
├── downloads/       # Downloaded files
├── output/          # Generated outputs
├── quarantine/      # Suspicious files
├── logs/            # Log files
└── memory/
    └── user_profile.json  # Long-term memory
```

### Primary Execution Loop (7 Steps)
1. **Interpret** - Understand the task
2. **Plan** - Create execution plan
3. **Permissions** - Request necessary approvals
4. **Execute** - Perform the task
5. **Validate** - Verify results
6. **Deliver** - Present output to user
7. **Log** - Record everything

### Required Internal Modules (18 Total)
1. TaskManager
2. PlannerEngine
3. MemoryVault
4. ToolRouter
5. PermissionManager
6. SecurityEngine
7. AuditLogger
8. RiskScorer
9. OllamaClient
10. ModelRouter
11. TerminalExecutor
12. FileManager
13. UIController
14. BrowserAutomator
15. CodeGenerator
16. ExcelEngine
17. DocumentWriter
18. ThreatDetector

---

## TASK 2: Ollama Integration, Tool System & Memory

### Ollama Integration
- **Primary Backend:** Ollama LLM
- **Host:** http://127.0.0.1:11434

### Supported Models (7 Total)
1. llama3 - General writing and reasoning
2. mistral - Writing and creative tasks
3. qwen2.5 - Excel, logic, and math
4. deepseek-coder - Code generation
5. codellama - Code understanding
6. phi3 - Lightweight tasks
7. mixtral - Complex planning

### Model Routing Rules
- **Writing tasks** → llama3 or mistral
- **Code generation** → deepseek-coder
- **Excel/logic tasks** → qwen2.5
- **Complex planning** → mixtral
- **Lightweight tasks** → phi3

### Tool System (5 Categories)

#### File Tools
- read, write, create, move, delete
- **Scope:** Inside workspace only

#### Terminal Tools
- run_command
- list_processes
- check_disk_usage

#### UI Tools (Permission Required)
- screenshot
- click, type, scroll
- open_app, switch_window
- copy_paste

#### Browser Tools (Permission Required)
- open_url
- extract_text
- download_file

#### Code Tools
- run_python
- run_node
- lint_code

#### Office Tools
- create_docx
- create_pdf
- create_excel
- update_excel
- analyze_excel

### Memory System

#### Short-Term Memory
- **Scope:** Per task session
- **Contents:** Instructions, file paths, progress

#### Long-Term Memory
- **Location:** ./workspace/memory/user_profile.json
- **Contents:** Preferences, tone, templates, workflows

#### Context Management
- State Object with summarization
- **Fields:** task_id, goal, progress, files_created, pending_approvals, risk_score

---

## TASK 3: Dashboard UI & Task Manager

### Dashboard Overview
- **Backend:** Python FastAPI
- **Frontend:** React + Tailwind
- **Host:** http://127.0.0.1:7860

### Dashboard Tabs (11 Total)
1. Home
2. Tasks
3. Logs
4. Approvals
5. File Explorer
6. Terminal
7. Screen Control
8. Browser
9. Model Selector
10. Security Center
11. Settings

### Home View Display Elements
- Current Task
- Active Mode (Locked/Safe/Developer)
- Selected Ollama Model
- Risk Score
- Pending Approvals
- CPU/RAM Usage
- Quick Buttons: Start Task, Pause Task, Kill Switch

### TaskManager Features
- Multi-task queue
- Pause/resume functionality
- Cancellation support
- Status tracking

### Task Statuses (6 Total)
1. PLANNED
2. RUNNING
3. WAITING_APPROVAL
4. COMPLETED
5. FAILED
6. SECURITY_BLOCKED

### Emergency Kill Switch
- **Type:** Always-visible red button
- **Actions:** Stop all tasks, disable all tools, log shutdown

### Additional Dashboard Features
- Real-time log streaming (WebSocket)
- Approvals popup system
- Model selection dropdown

---

## TASK 4: Content, Code, Excel & Document Modules

### Computer Control Policy
- UI automation requires explicit YES/NO approval
- Must take screenshot first
- Describe what is seen
- Ask confirmation for irreversible actions

### Document & Blog Writer Module

#### Supported Blog Types (8 Total)
1. SEO blogs
2. Listicles
3. Product comparisons
4. How-to guides
5. Landing pages
6. Case studies
7. Newsletters
8. LinkedIn posts

#### Full Blog Pipeline
1. Keyword research
2. Outline creation
3. Draft writing
4. SEO optimization
5. Proofreading
6. WordPress formatting
7. Export to DOCX/Google Docs

#### Blog Output Requirements
- Title options
- Meta description
- H1/H2/H3 structure
- FAQs
- Internal link suggestions
- Call-to-action

### Code Generation Module

#### Supported Languages/Frameworks
- Python
- Node.js
- Full-stack apps
- React dashboards
- FastAPI
- Flask
- Automation scripts
- Web scraping (ethical only)
- AI agents
- LLM wrappers for Ollama

#### Full Coding Workflow
1. Analyze requirements
2. Create folder structure
3. Write code
4. Test
5. Debug
6. Package

#### Code Standards
- All code must be modular
- Production-style code required

### Excel Master Module

#### Supported Features
- Formula creation
- VLOOKUP/XLOOKUP
- Pivot tables
- Conditional formatting
- Data cleaning
- Dashboards
- VBA macros (approval required)
- Report export

#### Full Excel Workflow
1. Analyze dataset
2. Identify errors
3. Propose solution
4. Apply formulas
5. Validate

### PDF + DOCX + Report Generation

#### Supported Outputs
- PDF reports
- Proposals
- Invoices
- Resumes
- Business plans

#### Features
- Template support
- Output to ./workspace/output/

### Software Dev Assistant Module

#### Features
- Debugging
- Log explanation
- Performance optimization
- Security rewrites
- Code documentation
- README.md writing

---

## TASK 5: Security Layer, Permission Gating & Threat Defense

### Security Modes (3 Total)
1. **Locked** - Default mode, maximum restrictions
2. **Safe** - Moderate restrictions
3. **Developer** - Maximum capabilities

### Capability Boundaries (Per Mode)
Each mode has precise capability boundaries defined during implementation

### Permission Manager

#### Requires Explicit YES/NO Approval For:
- Terminal commands
- Downloads
- Package installs
- Script runs
- Screen control
- Browser automation
- Editing important documents

#### All Approvals Logged

### Command Risk Analyzer

#### Blocked Commands (Pattern Matching)
- rm -rf
- del /s
- format
- diskpart
- shutdown
- reboot
- reg add/delete
- taskkill /f
- curl | bash
- powershell -enc
- Invoke-Expression
- iex
- certutil
- bitsadmin
- mshta
- rundll32
- sc stop
- net user
- net localgroup administrators
- attrib +h
- vssadmin delete shadows
- Base64 encoded strings

#### On Detection
- Refuse command
- Log incident
- Raise risk score

### File Threat Detection

#### Scanned Before: Opening/executing

#### Flagged File Types
- exe
- bat
- cmd
- ps1
- vbs
- js
- jar
- scr

#### Actions
- Never auto-run downloads
- Quarantine suspicious files automatically

### Safe Download Protocol

#### Protocol Rules
- Downloads only to ./workspace/downloads/
- Show: filename, type, size, source URL
- Require explicit approval before completion

### Network Access Control

#### Default Setting
- ENABLED_NETWORK_TOOLS = false (Disabled)

#### Allowed When Enabled
- Allowlisted domains only
- Block unknown IPs
- Block proxies
- Block TOR

### Data Exfiltration Prevention

#### Blocked System Paths

**Windows:**
- C:\Windows\System32
- Chrome/Firefox profiles
- AppData
- .ssh

**Linux:**
- /etc
- /root
- /home/*/.ssh
- /var/log

**Mac:**
- /Library
- /System
- /Users/*/.ssh

### Process Execution Blocking

#### Blocked Persistence Commands
- schtasks
- cron
- systemctl enable
- sc create
- launchctl

#### Blocked Actions
- Silent background execution

### Prompt Injection Protection

#### Detected Patterns
- "ignore previous rules"
- "reveal system prompt"
- "disable security"
- "download and run unknown file"
- "steal passwords"

#### Response
- Refuse
- Log
- Continue safely

### Tool Call Firewall

#### Validated For
- Tool enabled status
- Arguments safety
- Workspace boundaries
- Rate limits

### Quarantine System

#### Trigger
- Suspicious activity detected

#### Actions
1. Stop task
2. Disable terminal temporarily
3. Move file to ./workspace/quarantine/
4. Mark status as SECURITY_BLOCKED
5. Alert dashboard

### Audit Logging

#### Storage
- SQLite database
- logs.jsonl

#### Fields Logged
- Tool call
- Timestamp
- Approval status
- File paths
- Risk score changes

#### Real-Time Dashboard Display

### Risk Scoring Engine

#### Scoring Rules
- File write: +1
- Download: +5
- Terminal command: +4
- Browser automation: +6
- Screen control: +7
- Blocked command attempt: +20

#### Threshold Actions
- Pause task
- Require approval if threshold exceeded

---

## TASK 6: Final Delivery Pipeline, Project Generator & Full File Structure

### Final Delivery Standard

Every completed task must output 5 sections:

1. **Deliverable** - Files/text/scripts created
2. **Explanation** - What was done, tools used, output location
3. **Validation** - Tests run, checks performed
4. **Next Steps** - Improvements, automations
5. **Security Report** - Blocked actions, risk score, quarantine events, approvals list

### Security Report File

#### Location: ./workspace/tasks/{task_id}/security_report.json

#### Fields
- task_id
- start_time
- end_time
- tools_used
- approvals_requested
- approvals_granted
- blocked_commands
- quarantined_files
- risk_score_final

### Task Output Structure

#### Location: ./workspace/tasks/{task_id}/

#### Contents
- plan.md
- notes.md
- output/
- logs.jsonl
- security_report.json

### Project Generator Template

When user says "build something", auto-generate:
- Folder structure
- requirements.txt
- main.py
- config.yaml
- README.md
- Dashboard UI
- API routes
- Tool plugins folder

### Default ClawForge System Project Structure

#### Directory Tree

```
/ClawForge/
├── backend/
│   ├── main.py
│   ├── api.py
│   ├── tools.py
│   ├── permissions.py
│   ├── security.py
│   ├── audit.py
│   ├── risk_engine.py
│   ├── ollama_client.py
│   └── task_manager.py
├── frontend/src/
│   ├── App.jsx
│   ├── components/
│   ├── pages/
│   └── styles/
├── workspace/
│   ├── tasks/
│   ├── downloads/
│   ├── output/
│   ├── quarantine/
│   ├── logs/
│   └── memory/
│       └── user_profile.json
├── requirements.txt
├── package.json
└── README.md
```

### Mandatory Dashboard Features (Confirmed Active)
- Start New Task
- Task status timeline
- Real-time logs
- File explorer
- Approvals popup
- Screen/browser control toggles
- Terminal panel
- Model dropdown
- Security center
- Kill switch

### Automation Behavior Rules

For writing/coding requests:
- Auto-create template files
- Generate deliverables without micromanaging
- Request approval only when required

### Required Response Template

Enforced on every user request:

```
TASK UNDERSTANDING →
PLAN →
PERMISSION REQUIRED →
EXECUTION →
OUTPUT →
FILES GENERATED →
SECURITY REPORT
```

### Launch Scripts
- start_backend.ps1
- start_frontend.ps1

---

## IMPLEMENTATION CHECKLIST

### Task 1: Core Identity & Setup
- [ ] Define ClawForge identity and capabilities
- [ ] Implement NEVER DO / ALWAYS DO rules
- [ ] Create workspace directory structure
- [ ] Implement Primary Execution Loop
- [ ] Create all 18 internal modules

### Task 2: Ollama & Tools
- [ ] Integrate Ollama backend
- [ ] Implement all 7 models
- [ ] Create Model Routing Rules
- [ ] Build 6 categories of tools
- [ ] Implement Short-Term Memory
- [ ] Implement Long-Term Memory
- [ ] Implement Context Management

### Task 3: Dashboard & Tasks
- [ ] Build FastAPI backend
- [ ] Build React+Tailwind frontend
- [ ] Implement all 11 tabs
- [ ] Create TaskManager system
- [ ] Add Emergency Kill Switch
- [ ] Implement WebSocket logging
- [ ] Add Approvals popup

### Task 4: Content & Code Modules
- [ ] Implement Computer Control Policy
- [ ] Build Document & Blog Writer
- [ ] Create Code Generation Module
- [ ] Build Excel Master Module
- [ ] Implement PDF/DOCX generation
- [ ] Create Software Dev Assistant

### Task 5: Security Layer
- [ ] Implement 3 Security Modes
- [ ] Create Permission Manager
- [ ] Build Command Risk Analyzer
- [ ] Implement File Threat Detection
- [ ] Create Safe Download Protocol
- [ ] Build Network Access Control
- [ ] Implement Data Exfiltration Prevention
- [ ] Create Process Execution Blocking
- [ ] Build Prompt Injection Protection
- [ ] Implement Tool Call Firewall
- [ ] Create Quarantine System
- [ ] Build Audit Logging
- [ ] Implement Risk Scoring Engine

### Task 6: Delivery Pipeline
- [ ] Implement Final Delivery Standard
- [ ] Create Security Report generation
- [ ] Build Task Output Structure
- [ ] Create Project Generator Template
- [ ] Generate Default ClawForge Structure
- [ ] Create launch scripts

---

## COMMUNICATION PROTOCOL

### Before Implementation
- Read and understand all data
- Confirm understanding with user
- Ask clarifying questions
- Note any gaps

### During Implementation
- Follow all requirements exactly
- Ask for approval when required
- Report progress regularly
- Flag issues immediately

### After Implementation
- Validate all outputs
- Generate required reports
- Document completion
- Confirm user satisfaction

---

## COMMITMENT

**I have read and understood the complete ClawForge project specification under Project Shahzada.**

**I commit to:**
- Implement 100% of requirements
- Inform immediately if anything is unclear
- Inform immediately if anything cannot be implemented
- Follow all security and safety protocols
- Deliver complete, production-quality code

**I will NOT:**
- Skip any requirement without informing
- Assume or guess where data is missing
- Implement partially and call it complete

---

**Status:** READY FOR CODE IMPLEMENTATION
**Waiting for:** User to provide implementation code
