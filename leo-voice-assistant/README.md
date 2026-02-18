# Leo Voice Assistant 🦁

A lightweight, privacy-focused voice-controlled assistant. **No AI required!**

## Features

- 🎤 **Voice Control** - Control your PC with voice commands
- 🔒 **Privacy First** - Everything runs locally
- ⚡ **No AI Needed** - Uses pattern matching (no Ollama)
- 🖥️ **System Control** - Open/close apps, shutdown, lock
- 🌐 **Web Search** - Search Google, open websites
- 🗣️ **Voice Feedback** - Speaks back to you

## Requirements

- Windows 10/11
- Python 3.8+
- Microphone
- Internet (for speech recognition - can use offline Vosk model)

## Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**If PyAudio fails:**
```bash
# Option 1: Use pipwin
pip install pipwin
pipwin install pyaudio

# Option 2: Download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

### Step 2: Test Microphone

Make sure your microphone is working in Windows settings.

### Step 3: Run the App

```bash
python main.py
```

Or double-click `run.bat`

## Voice Commands

### Wake Word
- Say **"Hey Computer"** to activate

### After Wake Word, Say:

**Open Apps:**
- "Open Chrome" / "Open Brave" / "Open Edge"
- "Open Spotify" / "Open Discord" / "Open Slack"
- "Open Notepad" / "Open Calculator"
- "Open VS Code" / "Open Terminal"

**Close Apps:**
- "Close Chrome" / "Close Spotify" / "Close Notepad"

**Web:**
- "Search Google for jobs in Pakistan"
- "Open YouTube" / "Open Gmail" / "Open LinkedIn"
- "Go to [any website]"

**System:**
- "Volume Up" / "Volume Down" / "Mute"
- "What's the time?" / "What day is it?"
- "Shutdown" (then say "confirm" to confirm)
- "Restart" (then say "confirm" to confirm)
- "Lock" / "Sleep"

**Work:**
- "Find Jobs" - Opens LinkedIn Jobs
- "Check Email" - Opens Gmail
- "Open File Explorer"
- "Open Control Panel"

## App Mappings

The assistant knows these apps:

| Command | Opens |
|---------|-------|
| Chrome | Google Chrome |
| Brave | Brave Browser |
| Edge | Microsoft Edge |
| Spotify | Spotify |
| Discord | Discord |
| Slack | Slack |
| VS Code | Visual Studio Code |
| Notepad | Notepad |
| Calculator | Calculator |
| Terminal | Command Prompt |
| PowerShell | PowerShell |

## Troubleshooting

### Microphone not detected
- Check Windows: Settings > Privacy > Microphone
- Make sure microphone is enabled

### "Cannot recognize audio"
- Check internet connection (Google speech recognition needs internet)
- Or install Vosk model for offline recognition

### PyAudio installation error
- Install Visual C++ Redistributable
- Or use: `pipwin install pyaudio`

## Privacy

✅ **What's local:**
- Command parsing (pattern matching)
- Text-to-speech (pyttsx3)
- App launching

⚠️ **Needs internet for:**
- Speech-to-text (Google API) - can use offline Vosk model

No data is sent to servers - everything runs on your PC!

---

Made by Leo 🦁
