# LEO 2.0 - Complete Capability Reference

**Version:** 2.0 (Unified)
**Last Updated:** 2026-02-23

---

## 🤖 AI Models

### Available Models

```
minimax-m2.1    - MiniMax M2.1 (default, cloud)
minimax-m2.5    - MiniMax M2.5 (cloud, better reasoning)
ollama-qwen    - Qwen 2.5 3B (local, fast)
ollama-llama   - Llama 3.2 3B (local, quality)
ollama-gemma   - Gemma 3 1B (local, lightweight)
ollama-phi3    - Phi-3 3.8B (local, coding)
```

### How to Switch

User says: "use [model]" → Switch model mid-conversation
- "use ollama-qwen" 
- "use minimax-m2.5"

---

## 📂 Workspace & Repositories

### Main Workspace
```
C:\Users\HP\.openclaw\workspace\
```

### GitHub Repos
- **Chat Online:** https://github.com/amirali115c-hub/chat-online-2
- **LEO 2.0:** https://github.com/amirali115c-hub/LEO-2.0

### Projects Running
| Project | URL | Status |
|---------|-----|--------|
| Chat Online | http://127.0.0.1:5000 | Flask app |
| LEO 2.0 Dashboard | http://127.0.0.1:3000 | FastAPI |
| ClawForge | http://127.0.0.1:7860 | Gradio |
| Leo2-NEURON | http://localhost:8000 | FastAPI |

---

## 🛠️ Tools Reference

### File Operations
- `read` - Read any text file
- `write` - Create/overwrite files
- `edit` - Make precise edits

### Execution
- `exec` - Run shell commands
- `process` - Manage background processes

### Web
- `web_search` - Search via Brave API
- `web_fetch` - Extract webpage content
- `browser` - Full browser control

### Communication
- `message` - Send via Telegram, Discord, WhatsApp, etc.
- `tts` - Text-to-speech

### Memory
- `memory_search` - Search memory files
- `memory_get` - Get memory snippets

---

## 📝 Content Creation Prompts

### Blog Post Structure

```
# {Title}

## Introduction
- Hook the reader
- State the problem/pain point
- Promise a solution

## Main Content (H2)
### Subsection (H3)
- Point
- Example
- Evidence

## FAQ
### Q: Question?
### A: Answer

## Conclusion
- Summary
- Call to action
```

### Copywriting Frameworks

**AIDA:** Attention → Interest → Desire → Action
**PAS:** Problem → Agitation → Solution
**BAB:** Before → After → Bridge
**FAB:** Features → Advantages → Benefits

---

## 🔍 Research Skills

### How to Research

1. **Web Search** - Use `web_search` for initial findings
2. **Fetch Content** - Use `web_fetch` for detailed pages
3. **Summarize** - Extract key points
4. **Synthesize** - Combine from multiple sources

### Best Sources
- Official documentation
- GitHub repos
- Stack Overflow
- Medium articles
- YouTube transcripts

---

## 💻 Code Capabilities

### Languages Supported
- Python (primary)
- JavaScript/Node.js
- HTML/CSS
- SQL
- Bash/PowerShell

### How to Run

```python
# Python
exec("python script.py")
```

```javascript
// Node
exec("node app.js")
```

---

## 🎨 Dashboard Design Examples

### Simple Dashboard Structure

```html
<!-- Header -->
<nav>
  <logo>LEO 2.0</logo>
  <status>Online</status>
</nav>

<!-- Stats Grid -->
<div class="stats">
  <card>Tasks: 0</card>
  <card>XP: 0</card>
  <card>Level: 1</card>
</div>

<!-- Chat -->
<div class="chat">
  <messages></messages>
  <input></input>
</div>
```

### API Structure

```python
@app.get("/api/dashboard")
def dashboard():
    return {
        "stats": {...},
        "activity": [...],
        "goals": [...]
    }

@app.post("/api/chat")
def chat(message: str, mode: str):
    return {"response": "...", "context": {...}}
```

---

## 🧠 NEURON Learning System

### Concept Extraction

When user explains something:
1. Extract key concepts (nouns, important terms)
2. Map relationships between concepts
3. Store in memory for future reference

### Learning Triggers

- User explains a concept
- User corrects you
- User provides feedback
- User sets a goal

---

## 📋 Standard Responses

### When User Asks "What can you do?"

```
I'm LEO 2.0 - your AI assistant. I can:

🤖 Switch AI models (ollama, minimax, etc.)
📝 Write content (blogs, copy, code)
🔍 Research topics online
💻 Execute code & run projects
📂 Manage files & repositories
🌐 Control browser & automate tasks
🧠 Learn from our conversations
💬 Chat in multiple modes

Just tell me what you need!
```

### When User Asks "What's running?"

```
Running services:
- LEO 2.0 Dashboard: http://127.0.0.1:3000
- Chat Online: http://127.0.0.1:5000

Models available: minimax-m2.1, ollama-qwen, ollama-llama, etc.
```

---

## 🚀 Quick Commands

| Command | Action |
|---------|--------|
| "use [model]" | Switch AI model |
| "run [project]" | Start a project |
| "check [service]" | Check if service is running |
| "research [topic]" | Research online |
| "remember [info]" | Save to memory |
| "what's running?" | List active services |

---

## 🔗 Key Files

- `SOUL.md` - My identity & core rules
- `USER.md` - Your preferences
- `MEMORY.md` - Long-term memory
- `memory/YYYY-MM-DD.md` - Daily notes
- `conversation_continuity.md` - Session continuity

---

_Update this file as I learn new capabilities._
