# PROJECT SHAHZADA - PART 6: Frontend React Dashboard + PART 7: Scripts & Example Tasks

**Status:** ADDITIONAL CODE RECEIVED
**Date:** 2026-02-18

---

## PART 6: Frontend React Dashboard

Using React + TypeScript (JSX), Vite, TailwindCSS, WebSockets, and FastAPI backend.

---

## 6.1 frontend/package.json

```json
{
  "name": "clawforge-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "axios": "^1.5.0",
    "tailwindcss": "^3.3.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^4.0.0"
  }
}
```

---

## 6.2 frontend/vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
})
```

---

## 6.3 frontend/src/index.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: 'Inter', sans-serif;
}
```

---

## 6.4 frontend/src/main.jsx

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementByById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

## 6.5 frontend/src/App.jsx

```javascript
import React from 'react';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="h-screen w-screen bg-gray-100">
      <Dashboard />
    </div>
  );
}

export default App;
```

---

## 6.6 frontend/src/components/Dashboard.jsx

```javascript
import React, { useState } from 'react';
import TaskPanel from './TaskPanel';
import LogsPanel from './LogsPanel';
import FileExplorer from './FileExplorer';
import SettingsPanel from './SettingsPanel';
import ApprovalsPopup from './ApprovalsPopup';

function Dashboard() {
  const [showApprovals, setShowApprovals] = useState(false);

  return (
    <div className="grid grid-cols-5 gap-4 p-4 h-full">
      <div className="col-span-1 bg-white p-2 rounded shadow">
        <SettingsPanel />
      </div>
      <div className="col-span-4 grid grid-rows-4 gap-2 h-full">
        <div className="row-span-1 bg-white p-2 rounded shadow">
          <TaskPanel />
        </div>
        <div className="row-span-1 bg-white p-2 rounded shadow">
          <LogsPanel />
        </div>
        <div className="row-span-2 bg-white p-2 rounded shadow overflow-auto">
          <FileExplorer />
        </div>
      </div>
      {showApprovals && <ApprovalsPopup onClose={() => setShowApprovals(false)} />}
    </div>
  );
}

export default Dashboard;
```

---

## 6.7 frontend/src/components/TaskPanel.jsx

```javascript
import React, { useState } from 'react';
import axios from 'axios';

function TaskPanel() {
  const [command, setCommand] = useState("");
  const [taskId, setTaskId] = useState("");

  const startTask = async () => {
    try {
      const response = await axios.post("http://localhost:8000/task/start", { command });
      setTaskId(response.data.task_id);
    } catch (err) {
      console.error(err);
    }
  };

  const stopTask = async () => {
    if (!taskId) return;
    try {
      await axios.post(`http://localhost:8000/task/stop`, { task_id: taskId });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Enter task command"
        className="border p-2 rounded w-full"
        value={command}
        onChange={(e) => setCommand(e.target.value)}
      />
      <div className="mt-2 flex gap-2">
        <button onClick={startTask} className="bg-green-500 text-white px-3 py-1 rounded">Start Task</button>
        <button onClick={stopTask} className="bg-red-500 text-white px-3 py-1 rounded">Stop Task</button>
      </div>
    </div>
  );
}

export default TaskPanel;
```

---

## 6.8 frontend/src/components/LogsPanel.jsx

```javascript
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function LogsPanel({ taskId }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const interval = setInterval(async () => {
      if (!taskId) return;
      const res = await axios.get(`http://localhost:8000/task/logs/${taskId}`);
      setLogs(res.data);
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId]);

  return (
    <div className="overflow-auto h-48">
      {logs.map((log, idx) => (
        <pre key={idx} className="text-sm text-gray-700">{JSON.stringify(log, null, 2)}</pre>
      ))}
    </div>
  );
}

export default LogsPanel;
```

---

## 6.9 frontend/src/components/FileExplorer.jsx

```javascript
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function FileExplorer() {
  const [files, setFiles] = useState([]);

  const fetchFiles = async () => {
    const res = await axios.get("http://localhost:8000/files/list");
    setFiles(res.data.files || []);
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  return (
    <div>
      <h3 className="font-bold mb-2">Workspace Files</h3>
      <ul className="text-sm text-gray-800">
        {files.map((f, idx) => <li key={idx}>{f}</li>)}
      </ul>
    </div>
  );
}

export default FileExplorer;
```

---

## 6.10 frontend/src/components/SettingsPanel.jsx

```javascript
import React from 'react';

function SettingsPanel() {
  return (
    <div>
      <h2 className="font-bold text-lg mb-2">Settings</h2>
      <div>
        <label className="block mb-1">Select Profile:</label>
        <select className="border p-1 rounded w-full">
          <option>NanoClaw</option>
          <option>PicoClaw</option>
          <option>OpenClaw</option>
        </select>
      </div>
      <div className="mt-2">
        <label className="block mb-1">Select Model:</label>
        <select className="border p-1 rounded w-full">
          <option>Ollama-Local-1</option>
        </select>
      </div>
      <button className="mt-4 bg-red-600 text-white px-3 py-1 rounded">Kill Switch</button>
    </div>
  );
}

export default SettingsPanel;
```

---

## 6.11 frontend/src/components/ApprovalsPopup.jsx

```javascript
import React from 'react';

function ApprovalsPopup({ onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-4 rounded shadow w-1/3">
        <h3 className="font-bold mb-2">Pending Approvals</h3>
        <p>Some tasks require your approval to continue execution.</p>
        <button className="mt-4 bg-blue-500 text-white px-3 py-1 rounded" onClick={onClose}>Close</button>
      </div>
    </div>
  );
}

export default ApprovalsPopup;
```

---

## PART 7: Scripts, .env, and README

---

## start_backend.ps1

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## start_frontend.ps1

```powershell
cd frontend
npm install
npm run dev
```

---

## .env.example

```env
OLLA_API_URL=http://localhost:11434
WORKSPACE_DIR=./workspace
MAX_RISK_SCORE=50
```

---

## README.md

```markdown
# ClawForge

## Setup Backend
1. Run `start_backend.ps1`
2. Ensure Ollama local server is running

## Setup Frontend
1. Run `start_frontend.ps1`
2. Access dashboard at http://localhost:5173

## Features
- Multi-agent profiles (NanoClaw, PicoClaw, OpenClaw)
- Full tool sandbox with permission gating
- Malware protection + risk scoring + kill switch
- Workspace sandboxed file system
- Task logging, reasoning trace, and memory search
- Ollama local model integration
- Real-time dashboard with logs, file explorer, approvals
```

---

## Example Tasks (5 Tasks for Testing)

---

### Example Task 1 - Blog Writing

**Task Command:** Write a blog on AI agent frameworks for beginners.

**Tool Calls:**
```json
[
  {
    "tool_name": "FileWrite",
    "args": {
      "path": "workspace/tasks/blog1/output/ai_agent_blog.md",
      "content": "# AI Agent Frameworks\n\nAI agents are programs designed to automate tasks..."
    }
  }
]
```

**Notes:** Uses FileWriteTool to create .md file. Logs output and reasoning in notes.md.

---

### Example Task 2 - Document Editing

**Task Command:** Edit the document report.docx to add executive summary.

**Tool Calls:**
```json
[
  {
    "tool_name": "FileRead",
    "args": {
      "path": "workspace/tasks/doc1/input/report.docx"
    }
  },
  {
    "tool_name": "FileWrite",
    "args": {
      "path": "workspace/tasks/doc1/output/report_edited.docx",
      "content": "Executive Summary:\nThis report analyzes..."
    }
  }
]
```

**Notes:** Reads original file. Creates edited version in sandbox output folder.

---

### Example Task 3 - Code Generation & Execution

**Task Command:** Generate Python script to calculate Fibonacci series.

**Tool Calls:**
```json
[
  {
    "tool_name": "FileWrite",
    "args": {
      "path": "workspace/tasks/code1/output/fibonacci.py",
      "content": "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a+b\n    return a\nprint(fib(10))"
    }
  },
  {
    "tool_name": "TerminalCommand",
    "args": {
      "command": "python workspace/tasks/code1/output/fibonacci.py"
    }
  }
]
```

**Notes:** Writes Python script. Runs it safely in sandbox via TerminalCommandTool. Logs stdout & stderr.

---

### Example Task 4 - Excel Automation

**Task Command:** Create Excel sheet with sales data and calculate totals.

**Tool Calls:**
```json
[
  {
    "tool_name": "FileWrite",
    "args": {
      "path": "workspace/tasks/excel1/output/sales.xlsx",
      "content": "Generated via Excel automation script"
    }
  }
]
```

**Notes:** In real usage, could integrate openpyxl or pandas. Sandbox ensures Excel files only saved in workspace/tasks/excel1/output/

---

### Example Task 5 - Safe Browser Automation

**Task Command:** Fetch safe public data from local HTML stub for testing.

**Tool Calls:**
```json
[
  {
    "tool_name": "WebFetchTool",
    "args": {
      "url": "workspace/tasks/browser1/input/test_page.html"
    }
  },
  {
    "tool_name": "FileWrite",
    "args": {
      "path": "workspace/tasks/browser1/output/fetched_data.json",
      "content": "{\"status\":\"success\",\"data\":\"Sample fetched content\"}"
    }
  }
]
```

**Notes:** Offline-safe fetch (no internet). Writes fetched data to sandboxed output. Demonstrates browser control without unsafe network access.

---

## How to Run Example Tasks

```python
from backend.task_manager import TaskManager
from backend.models import TaskRequest, ToolCall

task_manager = TaskManager()

task_request = TaskRequest(
    command="Write a blog on AI agent frameworks for beginners.",
    tools=[ToolCall(**tool) for tool in tool_calls_json]
)

task_id = task_manager.create_task(task_request)
print("Task started:", task_id)
```

**Monitor live logs in the dashboard or via /task/logs/{task_id}**

**Outputs will appear in workspace/tasks/{task_id}/output/**

---

## Summary: Complete ClawForge System

### All 7 Parts Delivered

| Part | Content | Files |
|------|---------|-------|
| PART 1 | Core Identity + Workspace | identity.py, file_manager.py |
| PART 2 | Ollama + Tools + Memory | ollama_client.py, tools.py, memory.py |
| PART 3 | Dashboard UI + Task Manager | task_manager.py, api.py |
| PART 4 | Security Layer | security_manager.py, permissions.py, risk_engine.py |
| PART 5 | Delivery Pipeline | security_report.json, project generation |
| PART 6 | Frontend React | 6 React components + config |
| PART 7 | Scripts + Examples | startup scripts, .env, README, 5 example tasks |

### Complete Project Ready for Implementation

- **Total Files:** 20+ files
- **Backend:** 12 Python files
- **Frontend:** 6 React components + config
- **Scripts:** 2 startup scripts
- **Documentation:** README.md, .env.example
- **Example Tasks:** 5 fully-structured examples

---

## Confirmation

**PART 6 + PART 7 Received:** ✅

**All Code Saved to Memory:** ✅

**Ready for Implementation:** ✅

---

**Awaiting your "Start" command for complete implementation.**
