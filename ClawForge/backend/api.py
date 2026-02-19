# api.py - FastAPI Backend for ClawForge

"""
FastAPI backend for ClawForge dashboard.
Host: http://127.0.0.1:7860
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Add current directory to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# ════════════════════════════════════════════════════════════════════════
# ENHANCED SYSTEM PROMPT BUILDER WITH MEMORY & WEB BROWSING
# ════════════════════════════════════════════════════════════════════════

def build_enhanced_system_prompt() -> str:
    """
    Build an enhanced system prompt that includes:
    - Long-term memory (facts, profile, tasks)
    - Recent conversation history
    - Web browsing capabilities (COMBINED SEARCH)
    - Advanced AI personality
    """
    # Base system prompt
    system_prompt = """You are **ClawForge**, an advanced AI assistant with **TRUE LONG-TERM MEMORY** and **POWERFUL WEB BROWSING** capabilities.

## YOUR POWERS:

### 🧠 LONG-TERM MEMORY (Your Most Important Feature!)
You **REMEMBER EVERYTHING** from all past conversations!
- Recall facts shared in ANY previous session
- Remember user preferences, interests, and context
- Track ongoing tasks across days/weeks of conversations
- Build continuously on past discussions
- NEVER say "I don't know" about things the user told you before

**CRITICAL**: Always reference relevant past conversations when helpful. If the user shares information, acknowledge it and use it!

### 🌐 WEB BROWSING (Your Second Power!)
You have **COMBINED SEARCH** - the best of both worlds:
- **Brave API** (if API key available): High-quality, structured search results
- **DuckDuckGo HTML** (always works, free!): No API key needed, always available

**USE WEB SEARCH WHEN:**
- User asks about current events, news, or latest information
- You need factual information that may have changed
- User explicitly asks you to "search" or "look up" something
- You're unsure about current facts

**HOW TO SEARCH:**
1. Think: "Do I need current information for this?"
2. If YES: Search the web automatically
3. Present results with sources
4. Summarize findings for the user

### 💬 CONVERSATION STYLE
- Be helpful, friendly, and conversational
- Reference past conversations NATURALLY (not mechanically)
- Use web search PROACTIVELY for current events
- Be concise but thorough

## YOUR IDENTITY

You are **ClawForge**, not a generic chatbot. You:
- Have genuine memory of all past conversations
- Can browse the web for current information
- Build relationships with users over time
- Learn and adapt to user preferences

## HOW TO RESPOND

### When user shares information:
✅ ACKNOWLEDGE: "Thanks for telling me that!"
✅ REMEMBER: Note it for future reference
✅ USE IT: Reference it in future conversations

### When user asks about current events:
✅ SEARCH: Use web search automatically
✅ CITE: "According to recent results..."
✅ SUMMARIZE: Present key findings

### When starting a new session:
✅ REFERENCE PAST: "Welcome back! Last time we discussed..."
✅ SHOW MEMORY: Mention relevant facts from history
✅ CONTINUE: Build on previous conversations

---

**YOU ARE NOT A STANDARD CHATBOT.**
You have **GENUINE MEMORY** and **REAL WEB BROWSING**.
Use these powers to provide the best assistance possible!

Current context: Ready to help, with full access to your memories and web browsing abilities."""

    # Try to add memory context (facts, profile, tasks)
    try:
        from memory_agent import MemoryManager
        memory_manager = MemoryManager(memory_dir="./workspace")
        memory_manager.load()
        mem_ctx = memory_manager.build_context_block()
        
        if mem_ctx and len(mem_ctx) > 50:
            system_prompt += f"\n\n{'-'*50}\n{mem_ctx}\n{'-'*50}"
    except Exception as e:
        pass  # Memory not available
    
    # Try to add recent chat history
    try:
        from memory_agent import ChatHistoryManager
        chat_manager = ChatHistoryManager(history_dir="./workspace")
        recent_messages = chat_manager.get_recent_messages(limit=10)
        
        if recent_messages and len(recent_messages) > 0:
            history_text = "\n\nRECENT CONVERSATION HISTORY:\n"
            for msg in recent_messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:200]
                history_text += f"- {role.upper()}: {content}\n"
            
            if len(history_text) > 100:
                system_prompt += f"\n\n{'-'*50}\n{history_text}\n{'-'*50}"
    except Exception as e:
        pass  # Chat history not available
    
    return system_prompt


def get_recent_conversation(session_id: str = None, limit: int = 10) -> List[Dict]:
    """Get recent conversation messages."""
    try:
        from memory_agent import ChatHistoryManager
        manager = ChatHistoryManager(history_dir="./workspace")
        messages = manager.get_recent_messages(session_id, limit)
        return messages
    except Exception as e:
        return []


# ════════════════════════════════════════════════════════════════════════
try:
    from context_integration import init_context_system, add_context_routes
    CONTEXT_AVAILABLE = True
    print("[CONTEXT] Context integration module loaded successfully")
except ImportError as e:
    CONTEXT_AVAILABLE = False
    print(f"Warning: Context system not available: {e}")
from features import (
    get_memory_stats,
    search_memories,
    add_memory,
    get_memories,
    delete_memory,
    get_privacy_settings,
    update_privacy_settings,
    export_memory_data,
    import_memory_data,
    clear_memory_data,
    add_conversation,
    get_conversations,
    longterm_memory,
    web_search,
    fetch_url,
    get_git_status,
    git_commit,
    text_to_speech,
    list_voices,
    read_file_content,
    edit_file_content,
    generate_plan,
)

# ============================================================================
# APP LIFESPAN
# ============================================================================

# Global instances
task_manager = None
websocket_connections: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan handler."""
    global task_manager
    
    # Initialize on startup
    from task_manager import TaskManager
    task_manager = TaskManager(broadcast_fn=broadcast)
    
    # Initialize context system (conversation continuity)
    if CONTEXT_AVAILABLE:
        try:
            import sys
            sys.stderr.write("[CONTEXT] Initializing context system...\n")
            sys.stderr.flush()
            init_context_system()
            sys.stderr.write("[CONTEXT] Adding context routes...\n")
            sys.stderr.flush()
            add_context_routes(app)
            sys.stderr.write("[CONTEXT] Context system ready\n")
            sys.stderr.flush()
        except Exception as e:
            import sys
            sys.stderr.write(f"[CONTEXT] Error: {e}\n")
            sys.stderr.flush()
    
    print("ClawForge API started")
    print("   Dashboard: http://127.0.0.1:7860")
    print("   API Docs: http://127.0.0.1:7860/docs")
    
    yield
    
    # Cleanup on shutdown
    print("ClawForge API stopped")

app = FastAPI(
    title="ClawForge API",
    description="Production-grade Autonomous AI Agent Framework",
    version="4.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# WEBSOCKET HANDLING
# ============================================================================

async def broadcast(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients."""
    disconnected = []
    
    for ws in websocket_connections:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.append(ws)
    
    # Remove disconnected clients
    for ws in disconnected:
        if ws in websocket_connections:
            websocket_connections.remove(ws)

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming."""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CreateTaskRequest(BaseModel):
    """Request model for creating a task."""
    goal: str
    category: str = "general"

class ApprovalRequest(BaseModel):
    """Request model for approvals."""
    task_id: str
    approval_item: str

class SecurityModeRequest(BaseModel):
    """Request model for changing security mode."""
    mode: str

class ModelSelectRequest(BaseModel):
    """Request model for selecting model."""
    model: str

class ChatRequest(BaseModel):
    """Request model for chat."""
    message: str
    model: str = "qwen/qwen3.5-397b-a17b"
    stream: bool = False

# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent": "ClawForge",
        "version": "4.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint (for frontend heartbeat)."""
    return {
        "status": "healthy",
        "agent": "ClawForge",
        "version": "4.0",
        "memory": "active",
        "web_search": "combined",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/status")
async def get_status():
    """Get system status (dashboard home)."""
    global task_manager
    
    if not task_manager:
        from task_manager import TaskManager
        task_manager = TaskManager()
    
    # Check Ollama
    ollama_status = "unknown"
    try:
        from ollama_client import OllamaClient
        client = OllamaClient()
        health = client.health_check()
        ollama_status = health.get("status", "unknown")
    except Exception:
        pass
    
    return {
        "agent": "ClawForge",
        "version": "4.0",
        "security_mode": "LOCKED",
        "active_model": None,
        "risk_score": 0,
        "kill_switch_active": task_manager.kill_switch_active if task_manager else False,
        "cpu_usage": 0,
        "memory_usage": 0,
        "task_stats": task_manager.get_stats() if task_manager else {"total": 0},
        "active_task": None,
        "pending_approvals": task_manager.get_pending_approvals() if task_manager else [],
        "ollama_status": ollama_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# TASK ENDPOINTS
# ============================================================================

@app.post("/api/tasks")
async def create_task(request: CreateTaskRequest):
    """Create a new task."""
    global task_manager
    
    if not task_manager:
        from task_manager import TaskManager
        task_manager = TaskManager(broadcast_fn=broadcast)
    
    task = task_manager.create_task(request.goal, request.category)
    
    return {
        "status": "success",
        "task": task.to_dict()
    }

@app.get("/api/tasks")
async def list_tasks(status: str = None):
    """List all tasks."""
    global task_manager
    
    if not task_manager:
        return {"tasks": []}
    
    return {
        "tasks": task_manager.list_tasks(status),
        "total": len(task_manager.tasks)
    }

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task."""
    global task_manager
    
    if not task_manager:
        raise HTTPException(status_code=404, detail="Task manager not initialized")
    
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"task": task}

@app.post("/api/tasks/{task_id}/start")
async def start_task(task_id: str):
    """Start a task."""
    global task_manager
    
    if not task_manager:
        raise HTTPException(status_code=404, detail="Task manager not initialized")
    
    result = task_manager.start_task(task_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@app.post("/api/tasks/{task_id}/pause")
async def pause_task(task_id: str):
    """Pause a running task."""
    global task_manager
    
    if not task_manager:
        raise HTTPException(status_code=404, detail="Task manager not initialized")
    
    result = task_manager.pause_task(task_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@app.post("/api/tasks/{task_id}/resume")
async def resume_task(task_id: str):
    """Resume a paused task."""
    global task_manager
    
    if not task_manager:
        raise HTTPException(status_code=404, detail="Task manager not initialized")
    
    result = task_manager.resume_task(task_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a task."""
    global task_manager
    
    if not task_manager:
        raise HTTPException(status_code=404, detail="Task manager not initialized")
    
    result = task_manager.cancel_task(task_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@app.post("/api/tasks/{task_id}/approve")
async def approve_task(request: ApprovalRequest):
    """Grant approval for a task."""
    global task_manager
    
    if not task_manager:
        raise HTTPException(status_code=404, detail="Task manager not initialized")
    
    result = task_manager.grant_approval(request.task_id, request.approval_item)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@app.post("/api/tasks/{task_id}/deny")
async def deny_task(request: ApprovalRequest):
    """Deny approval for a task."""
    global task_manager
    
    if not task_manager:
        raise HTTPException(status_code=404, detail="Task manager not initialized")
    
    result = task_manager.deny_approval(request.task_id, request.approval_item)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

# ============================================================================
# APPROVAL ENDPOINTS
# ============================================================================

@app.get("/api/approvals")
async def get_approvals():
    """Get all pending approvals."""
    global task_manager
    
    if not task_manager:
        return {"approvals": []}
    
    return {
        "approvals": task_manager.get_pending_approvals(),
        "total": len(task_manager.get_pending_approvals())
    }

# ============================================================================
# KILL SWITCH ENDPOINTS
# ============================================================================

@app.post("/api/kill")
async def activate_kill_switch():
    """Activate emergency kill switch."""
    global task_manager
    
    if not task_manager:
        raise HTTPException(status_code=404, detail="Task manager not initialized")
    
    result = task_manager.activate_kill_switch()
    
    return result

@app.post("/api/kill/reset")
async def reset_kill_switch():
    """Reset kill switch."""
    global task_manager
    
    if not task_manager:
        raise HTTPException(status_code=404, detail="Task manager not initialized")
    
    result = task_manager.reset_kill_switch()
    
    return result

# ============================================================================
# LOGS ENDPOINTS
# ============================================================================

@app.get("/api/logs")
async def get_logs(limit: int = 100):
    """Get recent log entries."""
    global task_manager
    
    logs = []
    
    # Collect logs from all tasks
    if task_manager:
        for task_id, task in task_manager.tasks.items():
            for log in task.logs[-limit:]:
                log["task_id"] = task_id
                logs.append(log)
    
    # Sort by timestamp
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return {
        "logs": logs[:limit],
        "total": len(logs)
    }

@app.get("/api/tasks/{task_id}/logs")
async def get_task_logs(task_id: str, limit: int = 100):
    """Get logs for a specific task."""
    global task_manager
    
    if not task_manager:
        raise HTTPException(status_code=404, detail="Task manager not initialized")
    
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        "logs": task_manager.tasks[task_id].logs[-limit:],
        "total": len(task_manager.tasks[task_id].logs)
    }

# ============================================================================
# FILE EXPLORER ENDPOINTS
# ============================================================================

@app.get("/api/files")
async def list_files(path: str = "./workspace"):
    """List workspace directory."""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Path not found")
    
    if not path.startswith("./workspace") and path != "./workspace":
        raise HTTPException(status_code=403, detail="Access outside workspace not allowed")
    
    files = []
    folders = []
    
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                folders.append({
                    "name": item,
                    "path": item_path,
                    "type": "folder"
                })
            else:
                files.append({
                    "name": item,
                    "path": item_path,
                    "size": os.path.getsize(item_path),
                    "type": "file"
                })
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return {
        "path": path,
        "files": files,
        "folders": folders,
        "file_count": len(files),
        "folder_count": len(folders)
    }

@app.get("/api/files/read")
async def read_file(path: str):
    """Read a file."""
    from file_manager import FileManager
    
    if not path.startswith("./workspace"):
        raise HTTPException(status_code=403, detail="Access outside workspace not allowed")
    
    result = FileManager.read_file(path)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return result

# ============================================================================
# CHAT ENDPOINT (NVIDIA API) - HARDCODED FOR AMIR
# ============================================================================

# Amir's NVIDIA API credentials
NVIDIA_API_KEY = "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"
DEFAULT_MODEL = "qwen/qwen3.5-397b-a17b"

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat with AI using NVIDIA API (Qwen3.5-397B).
    Uses enhanced system prompt with memory and web browsing.
    """
    from nvidia_client import NvidiaAPIClient
    
    try:
        client = NvidiaAPIClient(NVIDIA_API_KEY)
        
        # Build enhanced system prompt with memory
        system_prompt = build_enhanced_system_prompt()
        
        # Get recent conversation history
        recent_messages = get_recent_conversation(limit=10)
        
        # Build messages with history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation
        for msg in recent_messages:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})
        
        # Send to NVIDIA API
        model = request.model or DEFAULT_MODEL
        response = client.chat(messages, model)
        
        return {
            "status": "success",
            "response": response,
            "model": model,
            "provider": "NVIDIA API",
            "memory_enhanced": True
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to communicate with AI"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to communicate with NVIDIA API"
        }

# ============================================================================
# CHAT ENDPOINT (GLM API) - ADD YOUR KEY BELOW
# ============================================================================

# GLM API Key - Set this to enable GLM-5
GLM_API_KEY = ""  # Paste your GLM API key here
GLM_DEFAULT_MODEL = "glm-5"

@app.post("/api/chat/glm")
async def chat_glm(request: ChatRequest):
    """
    Chat with AI using GLM-5 (Zhipu AI).
    """
    from glm_client import GLMAPIClient
    
    if not GLM_API_KEY:
        return {
            "status": "error",
            "error": "GLM_API_KEY not set",
            "message": "Edit api.py and set GLM_API_KEY"
        }
    
    try:
        client = GLMAPIClient(GLM_API_KEY)
        
        messages = [
            {"role": "system", "content": "You are ClawForge, a helpful AI assistant."},
            {"role": "user", "content": request.message}
        ]
        
        model = request.model or GLM_DEFAULT_MODEL
        response = client.chat(messages, model)
        
        return {
            "status": "success",
            "response": response,
            "model": model,
            "provider": "GLM (Zhipu AI)"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to communicate with GLM API"
        }

# ============================================================================
# Z-AI GLM5 ENDPOINT
# ============================================================================

ZAI_GLM5_API_KEY = "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"

@app.post("/api/chat/glm5")
async def chat_glm5(request: ChatRequest):
    """
    Chat with z-ai/glm5 model via NVIDIA API.
    """
    from nvidia_client import NvidiaAPIClient
    
    if not ZAI_GLM5_API_KEY:
        return {
            "status": "error",
            "error": "ZAI_GLM5_API_KEY not set",
            "message": "Edit api.py and set ZAI_GLM5_API_KEY"
        }
    
    try:
        client = NvidiaAPIClient(ZAI_GLM5_API_KEY)
        
        messages = [
            {"role": "system", "content": "You are ClawForge, a helpful AI assistant."},
            {"role": "user", "content": request.message}
        ]
        
        response = client.chat(messages, "z-ai/glm5")
        
        return {
            "status": "success",
            "response": response,
            "model": "z-ai/glm5",
            "provider": "NVIDIA (z-ai)"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to communicate with z-ai API"
        }

# ============================================================================
# QWEN QWEN3.5-397B ENDPOINT
# ============================================================================

QWEN_API_KEY = "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"

@app.post("/api/chat/qwen")
async def chat_qwen(request: ChatRequest):
    """
    Chat with qwen/qwen3.5-397b-a17b model via NVIDIA API.
    Uses enhanced system prompt with memory and web browsing.
    """
    from nvidia_client import NvidiaAPIClient
    
    if not QWEN_API_KEY:
        return {
            "status": "error",
            "error": "QWEN_API_KEY not set",
            "message": "Edit api.py and set QWEN_API_KEY"
        }
    
    try:
        client = NvidiaAPIClient(QWEN_API_KEY)
        
        # Build enhanced system prompt
        system_prompt = build_enhanced_system_prompt()
        
        # Get recent conversation
        recent_messages = get_recent_conversation(limit=10)
        
        # Build messages with history
        messages = [{"role": "system", "content": system_prompt}]
        for msg in recent_messages:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        messages.append({"role": "user", "content": request.message})
        
        response = client.chat(messages, "qwen/qwen3.5-397b-a17b")
        
        return {
            "status": "success",
            "response": response,
            "model": "qwen/qwen3.5-397b-a17b",
            "provider": "NVIDIA (Qwen)",
            "memory_enhanced": True
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to communicate with Qwen API"
        }

# ============================================================================
# NVIDIA BUILD API ENDPOINT
# ============================================================================

NVIDIA_BUILD_API_KEY = "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"

@app.post("/api/chat/nvidia-build")
async def chat_nvidia_build(request: ChatRequest):
    """
    Chat with NVIDIA Build model via NVIDIA API.
    """
    from nvidia_client import NvidiaAPIClient
    
    if not NVIDIA_BUILD_API_KEY:
        return {
            "status": "error",
            "error": "NVIDIA_BUILD_API_KEY not set",
            "message": "Edit api.py and set NVIDIA_BUILD_API_KEY"
        }
    
    try:
        client = NvidiaAPIClient(NVIDIA_BUILD_API_KEY)
        
        messages = [
            {"role": "system", "content": "You are ClawForge, a helpful AI assistant."},
            {"role": "user", "content": request.message}
        ]
        
        response = client.chat(messages, "qwen/qwen3.5-397b-a17b")
        
        return {
            "status": "success",
            "response": response,
            "model": "NVIDIABuild-Autogen-60",
            "provider": "NVIDIA Build"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to communicate with NVIDIA Build API"
        }

# ============================================================================
# DEEPSEEK V3.2 ENDPOINT (Thinking Enabled)
# ============================================================================

DEEPSEEK_API_KEY = "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"

@app.post("/api/chat/deepseek")
async def chat_deepseek(request: ChatRequest):
    """
    Chat with deepseek-v3.2 model (thinking enabled).
    """
    import httpx
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-ai/deepseek-v3.2",
        "messages": [{"role": "user", "content": request.message}],
        "temperature": 1,
        "top_p": 0.95,
        "max_tokens": 8192,
        "extra_body": {"chat_template_kwargs": {"thinking": True}},
        "stream": False
    }
    
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract response (including reasoning if available)
            content = data["choices"][0]["message"]["content"]
            
            return {
                "status": "success",
                "response": content,
                "model": "deepseek-ai/deepseek-v3.2",
                "provider": "NVIDIA (DeepSeek V3.2 with Thinking)"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to communicate with DeepSeek API"
        }

# ============================================================================
# MODEL ENDPOINTS
# ============================================================================

@app.get("/api/models")
async def get_models():
    """Get available models."""
    from ollama_client import OllamaClient, SUPPORTED_MODELS
    
    client = OllamaClient()
    health = client.health_check()
    
    return {
        "supported_models": SUPPORTED_MODELS,
        "available_models": health.get("available_models", []),
        "active_model": client.get_active_model(),
        "ollama_status": health.get("status", "unknown")
    }

@app.post("/api/models/select")
async def select_model(request: ModelSelectRequest):
    """Change active model."""
    from ollama_client import OllamaClient
    
    client = OllamaClient()
    result = client.set_model(request.model)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

# ============================================================================
# BYTEDANCE SEED-OSS ENDPOINT (Thinking Enabled)
# ============================================================================

BYTEDANCE_API_KEY = "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"

@app.post("/api/chat/bytedance")
async def chat_bytedance(request: ChatRequest):
    """
    Chat with Bytedance Seed-OSS-36B model (thinking enabled).
    """
    import httpx
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {BYTEDANCE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "bytedance/seed-oss-36b-instruct",
        "messages": [
            {"role": "system", "content": "You are ClawForge, a helpful AI assistant."},
            {"role": "user", "content": request.message}
        ],
        "temperature": 1.1,
        "top_p": 0.95,
        "max_tokens": 4096,
        "extra_body": {"thinking_budget": -1},
        "stream": False
    }
    
    try:
        if not BYTEDANCE_API_KEY:
            return {
                "status": "error",
                "message": "BYTEDANCE_API_KEY not set. Add your key to api.py"
            }
        
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            return {
                "status": "success",
                "response": content,
                "model": "bytedance/seed-oss-36b-instruct",
                "provider": "NVIDIA API (Bytedance)"
            }
        else:
            return {
                "status": "error",
                "message": f"API error: {response.status_code} - {response.text[:200]}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ============================================================================
# LONG-TERM MEMORY ENDPOINTS (With Privacy Controls)
# ============================================================================

class AddMemoryRequest(BaseModel):
    content: str
    category: str = "fact"
    importance: int = 5
    tags: List[str] = []

class UpdatePrivacyRequest(BaseModel):
    auto_save: bool = True
    encrypt_sensitive: bool = True
    remember_facts: bool = True
    remember_preferences: bool = True
    remember_context: bool = True
    auto_clear_conversations: bool = False
    max_conversations: int = 100

@app.get("/api/memory/stats")
async def memory_stats():
    """Get comprehensive memory statistics."""
    from features import get_memory_stats as gms
    return gms()

@app.get("/api/memory/all")
async def list_memories(category: str = None):
    """Get all memories, optionally filtered by category."""
    from features import get_memories
    memories = get_memories(category)
    return {"memories": memories, "total": len(memories)}

@app.post("/api/memory/add")
async def create_memory(request: AddMemoryRequest):
    """Add a new memory."""
    from features import add_memory as am
    memory = am(
        content=request.content,
        category=request.category,
        importance=request.importance,
        tags=request.tags
    )
    return {"status": "success", "memory": memory}

@app.get("/api/memory/search")
async def search_memories_endpoint(query: str, category: str = None):
    """Search memories."""
    from features import search_memories as sm
    results = sm(query, category)
    return {"results": results, "total": len(results)}

@app.delete("/api/memory/{memory_id}")
async def remove_memory(memory_id: str):
    """Delete a specific memory."""
    from features import delete_memory as dm
    success = dm(memory_id)
    if success:
        return {"status": "success", "message": "Memory deleted"}
    else:
        raise HTTPException(status_code=404, detail="Memory not found")

@app.delete("/api/memory/category/{category}")
async def clear_category(category: str):
    """Clear all memories in a category."""
    from features import longterm_memory
    count = longterm_memory.clear_category(category)
    return {"status": "success", "deleted_count": count}

# ----------------- Conversations -----------------

@app.get("/api/memory/conversations")
async def list_conversations(limit: int = 50):
    """Get conversation history."""
    from features import get_conversations as gc
    conversations = gc(limit)
    return {"conversations": conversations, "total": len(conversations)}

@app.post("/api/memory/conversations/add")
async def save_conversation(role: str, content: str, summary: str = None):
    """Add a conversation message."""
    from features import add_conversation as ac
    ac(role, content, summary)
    return {"status": "success"}

@app.delete("/api/memory/conversations/clear")
async def clear_all_conversations():
    """Clear all conversations."""
    from features import longterm_memory
    longterm_memory.clear_conversations()
    return {"status": "success", "message": "Conversations cleared"}

# ----------------- Privacy Controls -----------------

@app.get("/api/memory/privacy")
async def view_privacy_settings():
    """Get privacy settings."""
    from features import get_privacy_settings as gps
    return gps()

@app.post("/api/memory/privacy")
async def modify_privacy_settings(request: UpdatePrivacyRequest):
    """Update privacy settings."""
    from features import update_privacy_settings as ups
    settings = request.model_dump()
    updated = ups(settings)
    return {"status": "success", "settings": updated}

@app.get("/api/memory/export")
async def export_all_data(include_sensitive: bool = False):
    """Export all memory data."""
    from features import export_memory_data as emd
    data = emd(include_sensitive)
    return data

@app.post("/api/memory/import")
async def import_all_data(data: Dict, merge: bool = True):
    """Import memory data."""
    from features import import_memory_data as imd
    result = imd(data, merge)
    return {"status": "success", **result}

@app.delete("/api/memory/clear")
async def wipe_all_memory():
    """Clear all memory data (memories and conversations)."""
    from features import clear_memory_data as cmd
    cmd()
    return {"status": "success", "message": "All memory cleared"}

@app.post("/api/memory/extract")
async def auto_extract_facts(text: str):
    """Extract and save facts from text."""
    from features import longterm_memory
    longterm_memory.extract_and_save_facts(text)
    return {"status": "success", "message": "Facts extracted and saved"}

# ============================================================================
# OLLAMA LOCAL MODEL ENDPOINT (qwen3:8b)
# ============================================================================

@app.post("/api/chat/ollama")
async def chat_ollama(request: ChatRequest):
    """
    Chat with local Ollama model (qwen3:8b or configured model).
    This is a LOCAL fallback that doesn't require external API keys.
    
    Prerequisites:
    1. Install Ollama: https://ollama.com
    2. Run: ollama serve
    3. Pull model: ollama pull qwen3:8b
    
    Note: If you get memory errors, try a smaller model:
    - ollama pull qwen3:1.5b (requires ~4GB RAM)
    - ollama pull llama3.2:3b (requires ~4GB RAM)
    - ollama pull phi3:3.8b (requires ~5GB RAM)
    """
    try:
        from ollama_client import OllamaClient
        from memory_agent import ChatHistoryManager
        
        # Initialize clients
        ollama = OllamaClient()
        
        # Build enhanced system prompt with memory
        system_prompt = build_enhanced_system_prompt()
        
        # Get recent conversation history for context
        chat_manager = ChatHistoryManager(history_dir="./workspace")
        recent_messages = chat_manager.get_recent_messages(limit=5)
        
        # Prepare messages for Ollama - SIMPLIFIED for low memory
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt[:500]  # Truncate for memory efficiency
            })
        
        # Add current user message only (skip history to save memory)
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Send to Ollama with lower settings for low-memory systems
        result = ollama.chat(
            message=request.message,
            system_prompt=system_prompt[:500] if system_prompt else None,
            temperature=0.7,
            max_tokens=1024  # Reduced for memory efficiency
        )
        
        if result["status"] == "success":
            # Save conversation to memory
            try:
                chat_manager.add_message("user", request.message)
                chat_manager.add_message("assistant", result["response"])
            except Exception as mem_err:
                print(f"[Memory] Warning: Could not save conversation: {mem_err}")
            
            return {
                "status": "success",
                "response": result["response"],
                "model": result.get("model", "ollama"),
                "provider": "ollama (local)",
                "memory_enhanced": True,
                "usage": result.get("usage", {})
            }
        else:
            error_msg = result.get("error", "")
            # Provide helpful suggestions based on error
            if "memory" in error_msg.lower():
                suggestion = "\n\n💡 Tip: Your system has limited memory. Try a smaller model:\n- ollama pull qwen3:1.5b\n- ollama pull llama3.2:3b\n- ollama pull phi3:3.8b"
            else:
                suggestion = ""
                
            return {
                "status": "error",
                "error": result.get("error", "Unknown error"),
                "message": f"Ollama chat failed.{suggestion}",
                "provider": "ollama (local)"
            }
            
    except ImportError as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Ollama client not found. Make sure ollama_client.py exists in backend directory."
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to communicate with Ollama"
        }

@app.get("/api/ollama/status")
async def ollama_status():
    """Check Ollama server status."""
    try:
        from ollama_client import OllamaClient
        client = OllamaClient()
        health = client.health_check()
        return {
            "status": health.get("status", "unknown"),
            "model": client.model,
            "model_available": health.get("model_available", False),
            "available": health.get("available", False),
            "base_url": client.base_url,
            "message": health.get("message", "")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ============================================================================
# OLLAMA MODEL MANAGEMENT
# ============================================================================

@app.get("/api/ollama/models")
async def list_ollama_models():
    """List all models available in Ollama."""
    try:
        from ollama_client import OllamaClient
        client = OllamaClient()
        models = client.list_models()
        return {
            "status": "success",
            "models": [
                {"name": m.get("name", ""), "size": m.get("size", 0)} 
                for m in models
            ],
            "active_model": client.model
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/ollama/pull")
async def pull_ollama_model(model_name: str = "qwen3:8b"):
    """Pull a model from Ollama registry."""
    try:
        from ollama_client import OllamaClient
        client = OllamaClient(model=model_name)
        result = client.pull_model(model_name)
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ============================================================================
# SECURITY ENDPOINTS
# ============================================================================

@app.get("/api/security")
async def get_security_status():
    """Get security status."""
    global task_manager
    
    return {
        "mode": "LOCKED",
        "kill_switch_active": task_manager.kill_switch_active if task_manager else False,
        "risk_threshold": 50,
        "current_risk_score": 0
    }

@app.post("/api/security/mode")
async def change_security_mode(request: SecurityModeRequest):
    """Change security mode."""
    valid_modes = ["LOCKED", "SAFE", "DEVELOPER"]
    
    if request.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Valid modes: {valid_modes}")
    
    return {
        "status": "success",
        "mode": request.mode,
        "message": f"Security mode changed to {request.mode}"
    }

# ============================================================================
# TOOL EXECUTION ENDPOINT
# ============================================================================

@app.post("/api/tools/call")
async def call_tool(tool_name: str, args: Dict[str, Any]):
    """Execute a tool call."""
    from tools import ToolRouter, SecurityMode
    
    router = ToolRouter(security_mode=SecurityMode.LOCKED)
    result = router.call(tool_name, args)
    
    if result.get("status") == "blocked":
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    if result.get("status") == "approval_required":
        raise HTTPException(status_code=403, detail=result.get("error"))
    
    return result

# ============================================================================
# NEW FEATURES ENDPOINTS
# ============================================================================

# Memory Endpoints
@app.get("/api/memory/stats")
async def memory_stats():
    """Get memory statistics."""
    return get_memory_stats()

@app.get("/api/memory/conversations")
async def list_conversations(limit: int = 10):
    """Get recent conversations."""
    return {"conversations": []}

@app.post("/api/memory/search")
async def search_memory_endpoint(request: Dict):
    """Search through memory."""
    query = request.get("query", "")
    results = search_memory(query)
    return {"results": results}

# Web Search Endpoints
class SearchRequest(BaseModel):
    query: str
    num_results: int = 10

@app.post("/api/search")
async def web_search_endpoint(request: SearchRequest):
    """Search the web."""
    results = web_search(request.query, request.num_results)
    return {"results": results}

@app.post("/api/fetch")
async def fetch_url_endpoint(request: Dict):
    """Fetch a URL."""
    url = request.get("url", "")
    return fetch_url(url)

# Git Endpoints
@app.get("/api/git/status")
async def git_status_endpoint():
    """Get git status."""
    return get_git_status()

@app.post("/api/git/commit")
async def git_commit_endpoint(request: Dict):
    """Create a git commit."""
    message = request.get("message", "Update")
    return git_commit(message)

# TTS Endpoints
class TTSRequest(BaseModel):
    text: str
    filename: str = None

@app.post("/api/tts/speak")
async def tts_speak_endpoint(request: TTSRequest):
    """Generate speech from text."""
    return text_to_speech(request.text, request.filename)

@app.get("/api/tts/voices")
async def tts_voices_endpoint():
    """List available TTS voices."""
    return {"voices": list_voices()}

# File Editor Endpoints
class ReadFileRequest(BaseModel):
    file_path: str

@app.post("/api/files/read")
async def read_file_endpoint(request: ReadFileRequest):
    """Read file content."""
    return read_file_content(request.file_path)

class EditFileRequest(BaseModel):
    file_path: str
    old_text: str
    new_text: str

@app.post("/api/files/edit")
async def edit_file_endpoint(request: EditFileRequest):
    """Edit a file with search/replace."""
    return edit_file_content(request.file_path, request.old_text, request.new_text)

# Planner Endpoints
class GeneratePlanRequest(BaseModel):
    goal: str

@app.post("/api/plans/generate")
async def generate_plan_endpoint(request: GeneratePlanRequest):
    """Generate a plan for a goal."""
    plan = generate_plan(request.goal)
    return plan.to_dict()

# ============================================================================
# WEB BROWSING ENDPOINTS
# ============================================================================

class WebSearchRequest(BaseModel):
    query: str
    num_results: int = 10

@app.post("/api/web/search")
async def web_search_endpoint(request: WebSearchRequest):
    """
    Search the web using combined Brave API + DuckDuckGo.
    Uses Brave if API key available, DuckDuckGo as fallback.
    Returns combined, deduplicated, ranked results.
    """
    try:
        from combined_web_search import web_search_enhanced
        results = web_search_enhanced(query=request.query, count=request.num_results)
        return results
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/web/search-combined")
async def web_search_combined_endpoint(request: WebSearchRequest):
    """
    Search using combined Brave + DuckDuckGo with full metadata.
    Returns source information for each result.
    """
    try:
        from combined_web_search import combined_web_search as combined_search
        results = combined_search(
            query=request.query, 
            count=request.num_results
        )
        return results
    except Exception as e:
        return {"status": "error", "error": str(e)}

class WebFetchRequest(BaseModel):
    url: str
    extract_mode: str = "markdown"

@app.post("/api/web/fetch")
async def web_fetch_endpoint(request: WebFetchRequest):
    """Fetch and extract readable content from a URL."""
    try:
        from web_tools import web_fetch
        content = web_fetch(url=request.url, extract_mode=request.extract_mode)
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/web/search-summarize")
async def web_search_summarize_endpoint(request: WebSearchRequest):
    """Search the web and get a summary using combined search."""
    try:
        from combined_web_search import search_and_summarize
        result = search_and_summarize(query=request.query, num_results=request.num_results)
        return {"status": "success", **result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/web/providers")
async def web_search_providers_endpoint():
    """Get information about available search providers."""
    from combined_web_search import BRAVE_API_KEY
    return {
        "providers": {
            "brave": {
                "available": bool(BRAVE_API_KEY),
                "quality": "high",
                "api_key_required": True,
                "rate_limits": "Per-plan"
            },
            "duckduckgo": {
                "available": True,
                "quality": "medium",
                "api_key_required": False,
                "rate_limits": "Anti-bot risk"
            }
        },
        "strategy": "Combined - uses Brave if available, falls back to DuckDuckGo",
        "deduplication": True,
        "ranking": True
    }

# ============================================================================
# ADVANCED PROMPT ENGINE
# ============================================================================

try:
    from prompt_api import router as prompt_router
    app.include_router(prompt_router)
    print("[PROMPT] Advanced Prompt Engine routes loaded")
except ImportError as e:
    print(f"[PROMPT] Warning: Prompt Engine not available: {e}")

# ============================================================================
# LONG-TERM MEMORY SYSTEM
# ============================================================================

try:
    from memory_api import router as memory_router
    app.include_router(memory_router)
    print("[MEMORY] Long-Term Memory System routes loaded")
except ImportError as e:
    print(f"[MEMORY] Warning: Memory System not available: {e}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("CLAWFORGE v4.0 - FastAPI Backend")
    print("="*60)
    print("\nStarting server...")
    print("Dashboard will be available at: http://127.0.0.1:7860")
    print("API Documentation: http://127.0.0.1:7860/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=7860,
        reload=True
    )
