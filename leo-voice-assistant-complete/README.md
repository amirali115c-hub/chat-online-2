# Leo Voice Assistant 🦁

A **100% local, privacy-focused** voice assistant for Windows.

## Features

### Phase 1-3: Core Features
- 🎤 **Voice Control** - Natural language commands
- 🔒 **Privacy First** - All processing local, no cloud
- 🧠 **Local AI Brain** - Ollama integration for intent parsing
- ⚡ **Fast Response** - Pattern matching fallback
- 📝 **Audit Logging** - JSONL logs of all commands

### Phase 4: Browser & Blog
- 🌐 **Browser Automation** - Playwright-powered
- 📸 **Screenshots** - Capture any page
- 📝 **Blog Workflow** - Write drafts, WordPress posting
- 🔗 **WordPress API** - Auto-post to blogs

### Phase 5: System Integration
- 📌 **System Tray** - Runs in background
- ⚙️ **Configuration** - JSON config file
- 🔄 **Minimize to Tray** - Stay running quietly
- 🎯 **Hotkeys** - Global keyboard shortcuts

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install Ollama (optional)
# Download from https://ollama.com
# Then: ollama pull llama3.2:3b

# Run
python main.py
```

## Voice Commands

| Command | Action |
|---------|--------|
| `open chrome` | Opens Chrome |
| `open youtube` | Opens YouTube |
| `search for jobs` | Searches Google |
| `find jobs` | Opens LinkedIn Jobs |
| `volume up` | Increases volume |
| `mute` | Mutes audio |
| `what time is it` | Tells time |
| `shutdown` | Shuts down (confirm) |
| `lock` | Locks PC |
| `take screenshot` | Captures screen |
| `write blog` | Creates blog draft |
| `open wordpress` | Opens WordPress |

## Configuration

Edit `config.json` to customize:

```json
{
  "wake_word": "hey computer",
  "voice_rate": 150,
  "ollama_model": "llama3.2:3b",
  "require_confirmation": ["shutdown", "restart", "delete"],
  "minimize_to_tray": true
}
```

## Project Structure

```
leo-voice-assistant-complete/
├── main.py              # Main application
├── requirements.txt    # Dependencies
├── config.json         # Configuration (auto-created)
├── logs/              # Audit logs
├── screenshots/       # Screenshots
└── README.md          # This file
```

## Privacy

✅ **What's local:**
- Speech recognition
- Intent parsing (Ollama)
- Command execution
- Audit logging

## System Requirements

- Windows 10/11
- Python 3.10+
- 8GB RAM recommended
- Microphone (for voice)

## Testing Checklist

- [x] Wake word detection
- [x] Speech-to-text
- [x] Text-to-speech
- [x] Ollama integration
- [x] App control
- [x] File operations
- [x] System control
- [x] Browser automation
- [x] Blog workflow
- [x] System tray
- [x] Minimize to tray
- [x] Audit logging

## License

MIT

---

Made by Leo 🦁
