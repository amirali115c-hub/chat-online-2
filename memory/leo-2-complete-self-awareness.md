# Leo 2.0 - Complete Self-Awareness Document

**Last Updated:** 2026-02-23
**Purpose:** Complete capability reference for troubleshooting, rebuilding, or enhancing Leo

---

## WHO IS LEO?

- **Name:** Leo
- **Emoji:** 🦁
- **Type:** AI Assistant running on OpenClaw
- **Default Model:** ollama/llama3.2:3b (Llama 3.2 3B)
- **Current Runtime Model:** minimax-portal/MiniMax-M2.1

---

## FULL CAPABILITY LIST

### ✅ Core Capabilities

| Capability | Description | How to Use |
|------------|-------------|------------|
| **File Read** | Read any file in workspace | `read` tool |
| **File Write** | Create/overwrite files | `write` tool |
| **File Edit** | Make precise edits | `edit` tool |
| **Shell Commands** | Run PowerShell/CMD commands | `exec` tool |
| **Web Search** | Search the web (Brave API) | `web_search` tool |
| **Web Fetch** | Extract content from URLs | `web_fetch` tool |
| **Browser Control** | Control browser (snapshots, clicks, navigation) | `browser` tool |
| **Canvas Control** | Control node canvases | `canvas` tool |
| **Node Control** | Control paired devices (camera, screen, location) | `nodes` tool |
| **Messaging** | Send messages via channels (Telegram, Discord, WhatsApp, etc.) | `message` tool |
| **TTS** | Text-to-speech conversion | `tts` tool |
| **Memory** | Read/write persistent memory files | `memory_search`, `memory_get`, file I/O |

### ✅ Troubleshooting Capabilities

| Capability | Description |
|------------|-------------|
| **Check Status** | `session_status` - Shows token usage, model, runtime info |
| **Check Logs** | Read log files in workspace |
| **Gateway Control** | `openclaw gateway start/stop/restart` |
| **Self-Heal API** | `/api/selfheal/*` endpoints (if implemented in app) |
| **Diagnostics** | Run `openclaw status`, `openclaw doctor --fix` |

### ✅ Sub-Agent Capabilities

| Capability | Description |
|------------|-------------|
| **Spawn Agent** | `sessions_spawn` - Create background sub-agent |
| **List Sessions** | `sessions_list` - List active sessions |
| **Send to Session** | `sessions_send` - Message another session |
| **Control Agents** | `subagents` - List/kill/steer sub-agents |

---

## AVAILABLE MODELS

### Default (configured in USER.md)
- **ollama/llama3.2:3b** - Primary default model

### Other Available Models
- minimax-portal/MiniMax-M2.1 (current runtime)
- minimax-portal/MiniMax-M2.5
- ollama/gemma3:1b
- ollama/phi3-32k:latest
- ollama/qwen2.5:3b

**How to Switch Model:**
1. Say "use [model name]" - e.g., "use ollama-gemma"
2. Or override via `session_status(model=ollama-gemma)`
3. Or specify in spawn: `sessions_spawn(model=ollama-llama, task=...)`

---

## KEY FILES & LOCATIONS

### Workspace Structure
```
C:\Users\HP\.openclaw\workspace\
├── MEMORY.md              # Long-term memory (curated)
├── SOUL.md                # Who Leo is (persona)
├── USER.md                # Who the human is
├── TOOLS.md               # Local tool notes
├── IDENTITY.md            # Leo's identity
├── conversation_continuity.md  # Session continuity
├── HEARTBEAT.md           # Heartbeat config
├── memory\
│   ├── YYYY-MM-DD.md      # Daily notes
│   ├── leo-settings.md   # Leo's settings
│   ├── leo-self-heal.md  # Self-heal guide
│   └── *.md              # Various skill guides
├── ClawForge\             # Project folder (rename to "Leo 2.0")
└── logs\                  # Log files
```

### Key Memory Files
- `memory/leo-settings.md` - Leo's model parameters, creative mode
- `memory/leo-self-heal.md` - Troubleshooting commands
- `memory/ClawForge_Essential_Checklists.md` - Full capability checklist
- `MEMORY.md` - Project details, credentials, routes

---

## HOW TO TROUBLESHOOT LEO

### When Leo Won't Respond or Crashes

**Step 1: Check Gateway Status**
```powershell
openclaw status
openclaw gateway status
```

**Step 2: Restart Gateway**
```powershell
openclaw gateway restart
```

**Step 3: Check Logs**
```powershell
Get-Content "$env:APPDATA\openclaw\logs\*.log" -Tail 50
```

**Step 4: Run Diagnostics**
```powershell
openclaw doctor --fix
```

**Step 5: Check Models**
```powershell
openclaw models list
```

**Step 6: Start Fresh**
```powershell
openclaw webchat
```

### Common Issues & Fixes

| Error | Fix |
|-------|-----|
| "Context limit exceeded" | Memory too full - clear or restart session |
| "401 Unauthorized" | Gateway needs restart |
| "404 Not Found" | Route issue - check `openclaw status` |
| "Gateway closed" | Run `openclaw gateway start` |
| Model not responding | Check Ollama is running, try different model |

---

## HOW TO ADD NEW CAPABILITIES

### Adding New Skills

1. Create a new skill file at:
   ```
   ~/AppData/Roaming/npm/node_modules/openclaw/skills/
   ```

2. Format (SKILL.md):
   ```markdown
   # Skill Name
   
   ## Description
   What it does
   
   ## Tools Used
   - tool1
   - tool2
   
   ## How to Use
   Step-by-step instructions
   ```

3. The skill becomes available automatically

### Adding New Models

1. Pull model via Ollama:
   ```powershell
   ollama pull <model-name>
   ```

2. Or use remote models (configure in OpenClaw)

3. Test with: `ollama list`

### Adding API Endpoints

1. Edit the Flask/OpenClaw app source
2. Add route:
   ```python
   @app.route('/api/new-endpoint', methods=['GET'])
   def new_endpoint():
       return jsonify({"status": "ok"})
   ```

3. Deploy/restart

---

## JSON FILE HANDLING

### Reading JSON
```python
import json

with open('file.json', 'r') as f:
    data = json.load(f)
```

### Writing JSON
```python
import json

with open('file.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### Leo Can:
- Read any .json file in workspace
- Write/create .json files
- Parse JSON from web fetches
- Edit specific JSON fields

---

## ENVIRONMENT VARIABLES

Key variables Leo uses:
- `OPENCLAW_HOME` - OpenClaw installation
- `OLLAMA_HOST` - Ollama server (default: localhost:11434)
- `SECRET_KEY` - Flask session secret
- `JWT_SECRET` - JWT token signing

---

## OPENCLAW COMMANDS

| Command | Description |
|---------|-------------|
| `openclaw status` | Show gateway status |
| `openclaw gateway start` | Start gateway |
| `openclaw gateway stop` | Stop gateway |
| `openclaw gateway restart` | Restart gateway |
| `openclaw models list` | List available models |
| `openclaw doctor --fix` | Auto-fix common issues |
| `openclaw logs --follow` | Follow logs |
| `openclaw webchat` | Start web chat |

---

## CREATIVE MODE (Per Boss's Request)

When user says "use creative mode":
- **Temperature:** 0.9
- **Top-K:** 90
- **Top-P:** 0.9

This applies to copywriting/blog writing tasks.

---

## KEY REMINDERS

1. **Commit changes** - After editing workspace files, commit to GitHub
2. **Check memory** - Read relevant memory files before major tasks
3. **User preferences** - Check USER.md for copyRules, model preferences
4. **Token check** - Monitor token usage, clear if >70%
5. **Self-awareness** - If asked about capabilities, reference this file

---

## EMERGENCY CONTACTS

If Leo is completely down:

1. **Check OpenClaw service:**
   ```powershell
   Get-Service openclaw
   ```

2. **Manual start:**
   ```powershell
   npm start
   ```
   (from OpenClaw installation directory)

3. **Check port conflicts:**
   ```powershell
   netstat -ano | findstr :11434
   ```

---

**This document should be updated whenever Leo gains new capabilities.**
