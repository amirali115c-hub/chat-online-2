# ClawForge - AI-Powered Content & Workflow Platform

A comprehensive AI agent platform with copywriting, SEO, job hunting, and productivity tools.

## FREE Setup (No Paid APIs)

This implementation uses FREE local tools:
- **Ollama** (https://ollama.com) - Local AI models
- **Python 3.10+** - Core programming
- **DuckDuckGo** - Web search
- **SQLite** - Local database
- **N8N** - Workflow automation (self-hosted)
- **Selenium** - Browser automation
- **Gradio** - Dashboard UI
- **FastAPI** - API endpoints

## Quick Start

```bash
# Clone or download
cd ClawForge-Implementation

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download Ollama models
ollama pull llama3
ollama pull mistral
ollama pull codellama

# Start the platform
python main.py
```

## Project Structure

```
ClawForge-Implementation/
├── blog/                    # Blog posts
├── core/                   # Core AI modules
│   ├── agent.py           # Personal AI Agent
│   ├── memory.py          # MemoryManager
│   ├── web_tools.py       # WebTools
│   ├── code_executor.py   # CodeExecutor
│   ├── file_manager.py    # FileManager
│   ├── reasoning.py        # ReasoningEnhancer
│   ├── fact_checker.py    # FactChecker
│   ├── safety.py          # SafetyLayer
│   ├── meta_awareness.py  # MetaAwareness
│   └── tool_dispatcher.py  # ToolDispatcher
├── engines/                # Specialized engines
│   ├── lyra.py           # Lyra v2.0 Prompt Optimizer
│   ├── copywriting.py     # CopywritingEngine
│   ├── blog_engine.py     # BlogEngine
│   └── seo_engine.py      # SEOEngine
├── job_tools/             # Job hunting tools
│   ├── job_aggregator.py
│   ├── application_tracker.py
│   ├── resume_parser.py
│   ├── cover_letter.py
│   └── linkedin_automation.py
├── clawforge_essentials/   # ClawForge modules
│   ├── content_seo.py
│   ├── technical_audit.py
│   ├── marketing.py
│   ├── sales_crm.py
│   └── support.py
├── productivity/          # Productivity tools
│   ├── email.py
│   ├── calendar.py
│   ├── tasks.py
│   └── file_sync.py
├── connectivity/          # Connectivity
│   ├── slack.py
│   ├── discord.py
│   ├── telegram.py
│   └── webhooks.py
├── ui/                    # User interface
│   └── dashboard.py       # Gradio dashboard
├── api/                   # FastAPI endpoints
│   └── main.py
├── config/
│   └── config.yaml        # Configuration
├── tests/                 # Tests
├── requirements.txt       # Dependencies
├── config.yaml           # Main config
└── main.py              # Entry point
```

## Features

### Core AI (Personal Agent)
- [x] MemoryManager - SQLite persistent memory
- [x] WebTools - DuckDuckGo search, page fetch
- [x] CodeExecutor - Python/shell execution
- [x] FileManager - Read/write files
- [x] ReasoningEnhancer - Chain-of-thought, multi-perspective
- [x] FactChecker - Confidence scoring
- [x] SafetyLayer - Content moderation
- [x] MetaAwareness - Self-awareness, bias detection
- [x] ToolDispatcher - Unified tool routing

### Engines
- [x] **Lyra v2.0** - 5-D prompt optimization
- [x] **CopywritingEngine** - 12 frameworks (AIDA, PAS, BAB, etc.)
- [x] **BlogEngine** - HCU-compliant SEO content
- [x] **SEOEngine** - Full-stack SEO, schema, keywords

### Job Tools
- [x] Job aggregator
- [x] Application tracker
- [x] Resume parser
- [x] Cover letter generator
- [x] LinkedIn automation

### ClawForge Essentials
- [x] Content & SEO
- [x] Technical audit
- [x] Marketing automation
- [x] Sales CRM
- [x] Customer support

## Configuration

Edit `config.yaml` to customize:

```yaml
# FREE Configuration
ai:
  provider: "ollama"  # Free local AI
  models:
    - "llama3"
    - "mistral"
    - "codellama"

web:
  search: "duckduckgo"  # Free search

database:
  type: "sqlite"  # Free local database

automation:
  n8n_url: "http://localhost:5678"  # Self-hosted N8N
  browser: "selenium"  # Free browser automation

ui:
  dashboard: "gradio"  # Free UI framework
  port: 7860
```

## Usage

### Command Line

```bash
# Start the platform
python main.py --mode cli

# Start dashboard
python main.py --mode dashboard

# Run specific tool
python main.py --tool copywriting --product "Rolex" --audience "collectors"
```

### Dashboard

Access the web dashboard at `http://localhost:7860`

### API

Access API at `http://localhost:8000/docs`

## Dependencies

```
# requirements.txt
ollama>=0.1.0
duckduckgo-search>=7.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0
gradio>=4.0.0
fastapi>=0.109.0
uvicorn>=0.27.0
selenium>=4.15.0
n8n-nodes-python>=1.0.0
rich>=13.7.0
python-dotenv>=1.0.0
```

## License

MIT License

---

**Built with FREE local tools. No paid APIs required.**
