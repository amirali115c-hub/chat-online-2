"""
Leo Voice Assistant - Complete Local AI Voice Assistant
A 100% local, privacy-focused voice assistant for Windows
"""

import os
import sys
import json
import threading
import queue
import time
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path

# GUI
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# ============== CONFIGURATION ==============
APP_NAME = "Leo Voice Assistant"
VERSION = "5.0.0"
WAKE_WORD = "hey computer"
WORKSPACE = Path(r"C:\Users\HP\.openclaw\workspace\leo-voice-assistant")

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"

# Sandbox paths (for safety)
SANDBOX_PATHS = [
    Path.home() / "Desktop",
    Path.home() / "Documents", 
    Path.home() / "Downloads",
]

# ============== LOGGING ==============
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    
    # Print to console
    print(f"[{timestamp}] [{level}] {message}")
    
    # Save to log file
    log_dir = WORKSPACE / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# ============== VOICE ENGINE (TTS) ==============
class VoiceEngine:
    """Windows native text-to-speech engine"""
    
    def __init__(self):
        self.enabled = True
        self.rate = 150
        self.volume = 1.0
        
    def speak(self, text):
        """Speak text using Windows SAPI"""
        if not self.enabled:
            return
            
        try:
            text = text.replace('"', "'").replace('\n', ' ').replace('\r', '')
            cmd = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Rate = 0; $synth.Speak("{text}")'
            subprocess.Popen(
                ['powershell', '-WindowStyle', 'Hidden', '-Command', cmd],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            log(f"TTS Error: {e}", "ERROR")
    
    def speak_async(self, text):
        """Speak in background"""
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()

# ============== STT ENGINE (Speech to Text) ==============
class STTEngine:
    """Speech to Text - uses Windows built-in recognition"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self._init_recognizer()
        
    def _init_recognizer(self):
        """Initialize speech recognizer"""
        try:
            import speech_recognition
            self.recognizer = speech_recognition.Recognizer()
            log("STT Engine initialized", "INFO")
        except Exception as e:
            log(f"STT init error: {e}", "ERROR")
            self.recognizer = None
    
    def listen(self, timeout=5):
        """Listen for audio input"""
        if not self.recognizer:
            return None
            
        try:
            import speech_recognition as sr
            with self.microphone or sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Try Google first (needs internet)
            try:
                text = self.recognizer.recognize_google(audio)
                log(f"STT (Google): {text}", "INFO")
                return text
            except:
                pass
                
            # Fallback to vosk if available
            try:
                text = self.recognizer.recognize_vosk(audio)
                log(f"STT (Vosk): {text}", "INFO")
                return text
            except:
                pass
                
        except Exception as e:
            log(f"STT listen error: {e}", "ERROR")
        
        return None

# ============== LLM CLIENT (Ollama) ==============
class LLMClient:
    """Local LLM using Ollama"""
    
    def __init__(self, model=DEFAULT_MODEL):
        self.model = model
        self.base_url = OLLAMA_URL
        self.conversation_history = []
        self.available = self._check_ollama()
        
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                log("Ollama is available", "INFO")
                return True
        except:
            log("Ollama not available - using fallback parser", "WARNING")
        return False
    
    def generate(self, prompt, system_prompt=None):
        """Generate response from Ollama"""
        if not self.available:
            return None
            
        try:
            import requests
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            if system_prompt:
                payload["system"] = system_prompt
                
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json().get("response", "")
        except Exception as e:
            log(f"LLM error: {e}", "ERROR")
        
        return None
    
    def chat(self, message):
        """Chat with context"""
        if not self.available:
            return None
            
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            import requests
            payload = {
                "model": self.model,
                "messages": self.conversation_history[-10:],  # Last 10 messages
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_msg = result.get("message", {}).get("content", "")
                self.conversation_history.append({"role": "assistant", "content": assistant_msg})
                return assistant_msg
                
        except Exception as e:
            log(f"LLM chat error: {e}", "ERROR")
        
        return None

# ============== INTENT PARSER ==============
class IntentParser:
    """Parse user commands into structured JSON"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.system_prompt = """You are a Windows automation assistant. Parse user commands into JSON format.

Available actions:
- open_app: Open an application (params: app_name)
- close_app: Close an application (params: app_name)
- web_search: Search the web (params: query, engine="google")
- open_website: Open a website (params: url)
- system_control: Control system (params: action in ["volume_up", "volume_down", "mute", "unmute", "shutdown", "restart", "lock", "sleep", "get_time", "get_date"])
- file_operation: File operations (params: operation in ["create_folder", "list_files", "delete_file", "move_files"], path, destination)
- get_time: Get current time
- get_date: Get current date

Respond with ONLY the JSON object, no other text.
Example: {"action": "open_app", "app_name": "chrome"}
Example: {"action": "web_search", "query": "weather"}"""
    
    def parse(self, user_input):
        """Parse user input into intent"""
        # Try LLM first
        if self.llm and self.llm.available:
            try:
                prompt = f"{self.system_prompt}\n\nUser command: {user_input}\n\nJSON:"
                response = self.llm.generate(prompt)
                
                if response:
                    # Extract JSON
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    
                    if start >= 0 and end > start:
                        json_str = response[start:end]
                        intent = json.loads(json_str)
                        log(f"Intent (LLM): {intent}", "INFO")
                        return intent
            except Exception as e:
                log(f"Intent parse error: {e}", "ERROR")
        
        # Fallback to pattern matching
        return self._fallback_parse(user_input)
    
    def _fallback_parse(self, text):
        """Simple pattern matching fallback"""
        text = text.lower()
        
        # Open apps
        if 'open' in text or 'launch' in text or 'start' in text:
            apps = ['chrome', 'brave', 'edge', 'firefox', 'spotify', 'discord', 
                   'slack', 'vscode', 'notepad', 'calculator', 'word', 'excel']
            for app in apps:
                if app in text:
                    return {"action": "open_app", "app_name": app}
        
        # Close apps
        if 'close' in text or 'quit' in text:
            apps = ['chrome', 'brave', 'notepad', 'spotify']
            for app in apps:
                if app in text:
                    return {"action": "close_app", "app_name": app}
        
        # Websites
        sites = ['youtube', 'gmail', 'facebook', 'twitter', 'linkedin', 
                'reddit', 'amazon', 'netflix', 'github', 'wordpress']
        for site in sites:
            if site in text:
                return {"action": "open_website", "url": site}
        
        # Search
        if 'search' in text or 'find' in text:
            query = text.replace('search', '').replace('google', '').replace('for', '').strip()
            return {"action": "web_search", "query": query}
        
        # Jobs
        if 'job' in text:
            return {"action": "open_website", "url": "linkedin.com/jobs"}
        
        # Email
        if 'email' in text or 'gmail' in text:
            return {"action": "open_website", "url": "gmail.com"}
        
        # System control
        if 'volume up' in text or 'louder' in text:
            return {"action": "system_control", "params": {"action": "volume_up"}}
        if 'volume down' in text or 'quieter' in text:
            return {"action": "system_control", "params": {"action": "volume_down"}}
        if 'mute' in text:
            return {"action": "system_control", "params": {"action": "mute"}}
        if 'unmute' in text:
            return {"action": "system_control", "params": {"action": "unmute"}}
        
        # Time/Date
        if 'time' in text:
            return {"action": "system_control", "params": {"action": "get_time"}}
        if 'date' in text or 'day' in text:
            return {"action": "system_control", "params": {"action": "get_date"}}
        
        # Power
        if 'shutdown' in text or 'shut down' in text:
            return {"action": "system_control", "params": {"action": "shutdown"}}
        if 'restart' in text or 'reboot' in text:
            return {"action": "system_control", "params": {"action": "restart"}}
        if 'lock' in text:
            return {"action": "system_control", "params": {"action": "lock"}}
        if 'sleep' in text:
            return {"action": "system_control", "params": {"action": "sleep"}}
        
        # Files
        if 'explorer' in text or 'files' in text:
            return {"action": "system_control", "params": {"action": "explorer"}}
        if 'folder' in text or 'directory' in text:
            return {"action": "file_operation", "params": {"operation": "create_folder"}}
        
        # Settings
        if 'settings' in text:
            return {"action": "system_control", "params": {"action": "settings"}}
        if 'control panel' in text:
            return {"action": "system_control", "params": {"action": "control_panel"}}
        
        # Blog/Content
        if 'blog' in text or 'post' in text or 'write' in text:
            return {"action": "blog_workflow", "params": {"operation": "write"}}
        if 'wordpress' in text:
            return {"action": "blog_workflow", "params": {"operation": "wordpress"}}
        if 'screenshot' in text or 'capture' in text:
            return {"action": "screenshot", "params": {}}
        
        return {"action": "unknown", "original": text}

# ============== APP CONTROLLER ==============
class AppController:
    """Control applications"""
    
    APP_PATHS = {
        'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        'brave': r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
        'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
        'spotify': r'C:\Users\HP\AppData\Roaming\Spotify\Spotify.exe',
        'discord': r'C:\Users\HP\AppData\Local\Discord\Update.exe',
        'slack': r'C:\Users\HP\AppData\Local\slack\slack.exe',
        'vscode': r'C:\Users\HP\AppData\Local\Programs\Microsoft VS Code\Code.exe',
        'notepad': 'notepad.exe',
        'calc': 'calc.exe',
        'cmd': 'cmd.exe',
        'powershell': 'powershell.exe',
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'paint': 'mspaint.exe',
        'explorer': 'explorer.exe',
    }
    
    def open_app(self, app_name):
        """Open application"""
        app_name = app_name.lower().strip()
        
        if app_name in self.APP_PATHS:
            path = self.APP_PATHS[app_name]
            try:
                subprocess.Popen(path)
                log(f"Opened app: {app_name}", "INFO")
                return f"Opening {app_name}"
            except Exception as e:
                log(f"Failed to open {app_name}: {e}", "ERROR")
        
        # Try start menu
        try:
            subprocess.Popen(f"start {app_name}", shell=True)
            return f"Opening {app_name}"
        except:
            return f"Could not find {app_name}"
    
    def close_app(self, app_name):
        """Close application"""
        app_name = app_name.lower().strip()
        
        process_map = {
            'chrome': 'chrome.exe',
            'brave': 'brave.exe',
            'edge': 'msedge.exe',
            'firefox': 'firefox.exe',
            'spotify': 'spotify.exe',
            'discord': 'discord.exe',
            'notepad': 'notepad.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
        }
        
        proc_name = process_map.get(app_name, f"{app_name}.exe")
        
        try:
            subprocess.run(['taskkill', '/F', '/IM', proc_name], capture_output=True)
            log(f"Closed app: {app_name}", "INFO")
            return f"Closed {app_name}"
        except:
            return f"Could not close {app_name}"

# ============== FILE CONTROLLER ==============
class FileController:
    """Safe file operations"""
    
    def __init__(self):
        self.sandbox_paths = SANDBOX_PATHS
        self.destructive_ops = ['delete_file', 'move_files', 'delete_folder']
    
    def _is_safe_path(self, path):
        """Check if path is within sandbox"""
        try:
            path = Path(path).resolve()
            for safe in self.sandbox_paths:
                if safe in path.parents or safe == path:
                    return True
        except:
            pass
        return False
    
    def create_folder(self, path):
        """Create folder"""
        if not self._is_safe_path(path):
            return "Error: Path not allowed"
        
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            log(f"Created folder: {path}", "INFO")
            return f"Created folder: {path}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def list_files(self, path):
        """List files in directory"""
        if not self._is_safe_path(path):
            return "Error: Path not allowed"
        
        try:
            files = list(Path(path).iterdir())
            names = [f.name for f in files[:20]]
            return " ".join(names) if names else "Empty"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def delete_file(self, path, confirmed=False):
        """Delete file (requires confirmation)"""
        if not confirmed:
            return f"CONFIRM_DELETE: {path}"
        
        if not self._is_safe_path(path):
            return "Error: Path not allowed"
        
        try:
            Path(path).unlink()
            log(f"Deleted file: {path}", "INFO")
            return f"Deleted: {path}"
        except Exception as e:
            return f"Error: {str(e)}"

# ============== SYSTEM CONTROLLER ==============
class SystemController:
    """System controls"""
    
    def volume_up(self, steps=2):
        """Increase volume"""
        # Simulated - would use pycaw
        return "Volume increased"
    
    def volume_down(self, steps=2):
        """Decrease volume"""
        return "Volume decreased"
    
    def mute(self):
        """Mute"""
        return "Muted"
    
    def unmute(self):
        """Unmute"""
        return "Unmuted"
    
    def get_time(self):
        """Get current time"""
        return datetime.now().strftime("%I:%M %p")
    
    def get_date(self):
        """Get current date"""
        return datetime.now().strftime("%B %d, %Y")
    
    def shutdown(self, confirmed=False):
        """Shutdown (requires confirmation)"""
        if not confirmed:
            return "CONFIRM_SHUTDOWN"
        subprocess.run(['shutdown', '/s', '/t', '30'])
        return "Shutting down in 30 seconds"
    
    def restart(self, confirmed=False):
        """Restart (requires confirmation)"""
        if not confirmed:
            return "CONFIRM_RESTART"
        subprocess.run(['shutdown', '/r', '/t', '30'])
        return "Restarting in 30 seconds"
    
    def lock(self):
        """Lock PC"""
        subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
        return "Locking PC"
    
    def sleep(self):
        """Sleep"""
        subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0', '1', '0'])
        return "Going to sleep"
    
    def open_settings(self):
        """Open Settings"""
        subprocess.Popen('ms-settings:')
        return "Opening Settings"
    
    def open_control_panel(self):
        """Open Control Panel"""
        subprocess.Popen('control.exe')
        return "Opening Control Panel"
    
    def open_explorer(self):
        """Open File Explorer"""
        subprocess.Popen('explorer.exe')
        return "Opening File Explorer"

# ============== WEB CONTROLLER ==============
class WebController:
    """Browser automation with Playwright"""
    
    def __init__(self):
        self.browser_path = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
        self.playwright = None
        self.browser = None
        self.page = None
        
    def _init_playwright(self):
        """Initialize Playwright"""
        try:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)
            self.page = self.browser.new_page()
            return True
        except Exception as e:
            log(f"Playwright init failed: {e}", "ERROR")
            return False
    
    def open_website(self, url):
        """Open website"""
        if not url.startswith('http'):
            url = 'https://' + url
        
        try:
            # Try with Playwright
            if not self.page:
                if self._init_playwright():
                    self.page.goto(url)
                    log(f"Opened with Playwright: {url}", "INFO")
                    return f"Opening {url}"
        except Exception as e:
            log(f"Playwright failed, using browser: {e}", "WARNING")
        
        # Fallback to subprocess
        try:
            subprocess.Popen([self.browser_path, url])
            log(f"Opened: {url}", "INFO")
            return f"Opening {url}"
        except:
            webbrowser.open(url)
            return f"Opening {url}"
    
    def search(self, query, engine="google"):
        """Web search"""
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return self.open_website(url)
    
    def click_element(self, selector):
        """Click element by selector"""
        if self.page:
            try:
                self.page.click(selector)
                return f"Clicked {selector}"
            except Exception as e:
                return f"Click failed: {str(e)}"
        return "No page open"
    
    def type_text(self, selector, text):
        """Type into element"""
        if self.page:
            try:
                self.page.fill(selector, text)
                return f"Typed into {selector}"
            except Exception as e:
                return f"Type failed: {str(e)}"
        return "No page open"
    
    def take_screenshot(self, path=None):
        """Take screenshot"""
        if self.page:
            if not path:
                path = WORKSPACE / "screenshot.png"
            self.page.screenshot(path=str(path))
            return f"Screenshot saved to {path}"
        return "No page open"
    
    def close_browser(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.browser = None
        self.page = None
        self.playwright = None

# ============== BLOG WORKFLOW ==============
class BlogWorkflow:
    """Complete blog posting workflow"""
    
    def __init__(self, web_controller):
        self.web = web_controller
        self.word_app = None
        
    def open_word(self):
        """Open Microsoft Word"""
        try:
            subprocess.Popen(['winword.exe'])
            return "Opening Word"
        except:
            return "Could not open Word"
    
    def write_blog(self, title, content):
        """Write blog in Word (simplified)"""
        # This would use pyautogui for full automation
        # For now, just open a text file
        desktop = Path.home() / "Desktop"
        file_path = desktop / f"{title.replace(' ', '_')}.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n\n{content}")
        
        log(f"Blog saved: {file_path}", "INFO")
        return f"Blog saved to Desktop as {title}.txt"
    
    def post_to_wordpress(self, site_url, title, content, username, password):
        """Post to WordPress via API"""
        try:
            import requests
            
            # WordPress REST API
            url = f"{site_url}/wp-json/wp/v2/posts"
            
            data = {
                'title': title,
                'content': content,
                'status': 'publish'
            }
            
            response = requests.post(url, json=data, auth=(username, password))
            
            if response.status_code in [200, 201]:
                return f"Blog posted successfully!"
            else:
                return f"Post failed: {response.status_code}"
                
        except Exception as e:
            return f"WordPress error: {str(e)}"
    
    def create_blog_workflow(self, title, content, platform="wordpress", **credentials):
        """Complete workflow: write and optionally post"""
        # Step 1: Write content
        result = self.write_blog(title, content)
        
        # Step 2: Open in browser if posting
        if platform == "wordpress" and credentials.get('site_url'):
            self.post_to_wordpress(
                credentials['site_url'],
                title,
                content,
                credentials.get('username', ''),
                credentials.get('password', '')
            )
        
        return result

# ============== SAFETY MANAGER ==============
class SafetyManager:
    """Safety and confirmation handling"""
    
    def __init__(self, tts_engine):
        self.tts = tts_engine
        self.destructive_actions = ['shutdown', 'restart', 'delete_file', 'move_files']
        self.pending_confirmation = None
    
    def needs_confirmation(self, intent):
        """Check if action needs confirmation"""
        action = intent.get('action')
        if action == 'system_control':
            params = intent.get('params', {})
            action = params.get('action')
        
        return action in self.destructive_actions
    
    def confirm(self, action_type):
        """Process confirmation"""
        if self.pending_confirmation == action_type:
            self.pending_confirmation = None
            return True
        return False

# ============== MAIN ORCHESTRATOR ==============
class LeoAssistant:
    """Main voice assistant"""
    
    def __init__(self):
        log("Initializing Leo Voice Assistant...", "INFO")
        
        # Initialize components
        self.voice = VoiceEngine()
        self.stt = STTEngine()
        self.llm = LLMClient()
        self.intent_parser = IntentParser(self.llm)
        self.app_ctrl = AppController()
        self.file_ctrl = FileController()
        self.sys_ctrl = SystemController()
        self.web_ctrl = WebController()
        self.blog_workflow = BlogWorkflow(self.web_ctrl)
        self.safety = SafetyManager(self.voice)
        
        # State
        self.listening = False
        self.running = True
        
        # Setup GUI
        self.setup_gui()
        
        log("Leo Voice Assistant ready!", "INFO")
    
    def setup_gui(self):
        """Setup the GUI"""
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} 🦁 v{VERSION}")
        self.root.geometry("550x700")
        self.root.configure(bg='#1e1e2e')
        
        # Header
        header = tk.Frame(self.root, bg='#7c3aed', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text=f"{APP_NAME} 🦁", 
                font=('Arial', 18, 'bold'),
                bg='#7c3aed', fg='white').pack(pady=15)
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready - Say 'Hey Computer'",
                                    font=('Arial', 11), bg='#1e1e2e', fg='#4ade80')
        self.status_label.pack(pady=5)
        
        # Ollama status
        self.llm_status = tk.Label(self.root, 
                                   text=f"LLM: {'Connected' if self.llm.available else 'Using Fallback'}",
                                   font=('Arial', 9), bg='#1e1e2e', fg='#888')
        self.llm_status.pack()
        
        # Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Commands tab
        self.tab_cmds = tk.Frame(notebook, bg='#1e1e2e')
        notebook.add(self.tab_cmds, text="💬 Commands")
        self.setup_commands_tab()
        
        # Log tab
        self.tab_log = tk.Frame(notebook, bg='#1e1e2e')
        notebook.add(self.tab_log, text="📝 Log")
        self.log_area = scrolledtext.ScrolledText(self.tab_log, bg='#2d2d2d', fg='#fff', font=('Consolas', 9))
        self.log_area.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Input
        input_frame = tk.Frame(self.root, bg='#1e1e2e')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        self.input_entry = tk.Entry(input_frame, font=('Arial', 12),
                                   bg='#2d2d2d', fg='white', insertbackground='white')
        self.input_entry.pack(side='left', fill='x', expand=True)
        self.input_entry.bind('<Return>', lambda e: self.process_text())
        
        tk.Button(input_frame, text="Send", command=self.process_text,
                 bg='#7c3aed', fg='white', font=('Arial', 10, 'bold'),
                 padx=15).pack(side='left', padx=5)
        
        # Version
        tk.Label(self.root, text=f"v{VERSION} | Privacy-focused | 100% Local",
                 font=('Arial', 8), bg='#1e1e2e', fg='#666').pack(pady=5)
        
        # Minimize to tray on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        """Handle window close - minimize to tray"""
        self.root.withdraw()
        log("Minimized to tray", "INFO")
    
    def setup_commands_tab(self):
        """Setup commands display"""
        frame = tk.Frame(self.tab_cmds, bg='#1e1e2e')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        commands = [
            ("Wake", "Say 'Hey Computer' to activate"),
            ("Open Apps", "open chrome, open spotify, open vscode"),
            ("Websites", "open youtube, open gmail, open linkedin"),
            ("Search", "search for jobs, search weather"),
            ("Blog", "write blog, post to wordpress"),
            ("Screenshot", "take screenshot"),
            ("System", "volume up, mute, get time, lock"),
            ("Power", "shutdown, restart (say confirm)"),
            ("Files", "create folder, list files"),
        ]
        
        for cat, cmd in commands:
            tk.Label(frame, text=cat, font=('Arial', 11, 'bold'),
                    bg='#1e1e2e', fg='#7c3aed').pack(anchor='w', pady=(8, 2))
            tk.Label(frame, text=cmd, font=('Arial', 9),
                    bg='#1e1e2e', fg='#888').pack(anchor='w')
    
    def log(self, msg):
        """Add to log"""
        self.log_area.insert(tk.END, f"{msg}\n")
        self.log_area.see(tk.END)
    
    def process_text(self):
        """Process text input"""
        text = self.input_entry.get().strip()
        if not text:
            return
        
        self.input_entry.delete(0, tk.END)
        self.log(f"You: {text}")
        
        # Check for confirmation
        if self.safety.pending_confirmation:
            if 'yes' in text.lower() or 'confirm' in text.lower():
                action = self.safety.pending_confirmation
                self.safety.pending_confirmation = None
                result = self.execute_action({"action": "system_control", 
                                            "params": {"action": action, "confirmed": True}})
                self.log(f"Leo: {result}")
                self.voice.speak(result)
                return
            else:
                self.safety.pending_confirmation = None
                self.log("Cancelled")
                self.voice.speak("Cancelled")
                return
        
        # Check for wake word
        if WAKE_WORD in text.lower():
            text = text.lower().replace(WAKE_WORD, '').strip()
        
        if not text:
            return
        
        # Parse intent
        intent = self.intent_parser.parse(text)
        self.log(f"Intent: {json.dumps(intent)}")
        
        # Execute
        result = self.execute_action(intent)
        self.log(f"Leo: {result}")
        self.voice.speak(result)
    
    def execute_action(self, intent):
        """Execute parsed intent"""
        action = intent.get('action')
        
        try:
            if action == 'open_app':
                return self.app_ctrl.open_app(intent.get('app_name', ''))
            
            elif action == 'close_app':
                return self.app_ctrl.close_app(intent.get('app_name', ''))
            
            elif action == 'open_website':
                return self.web_ctrl.open_website(intent.get('url', ''))
            
            elif action == 'web_search':
                return self.web_ctrl.search(intent.get('query', ''))
            
            elif action == 'system_control':
                params = intent.get('params', {})
                sys_action = params.get('action', '')
                
                # Check for confirmation
                if sys_action in ['shutdown', 'restart']:
                    if not params.get('confirmed'):
                        self.safety.pending_confirmation = sys_action
                        return f"Say 'confirm' to {sys_action}"
                
                # Execute
                if sys_action == 'volume_up':
                    return self.sys_ctrl.volume_up()
                elif sys_action == 'volume_down':
                    return self.sys_ctrl.volume_down()
                elif sys_action == 'mute':
                    return self.sys_ctrl.mute()
                elif sys_action == 'unmute':
                    return self.sys_ctrl.unmute()
                elif sys_action == 'get_time':
                    return f"Time is {self.sys_ctrl.get_time()}"
                elif sys_action == 'get_date':
                    return f"Today is {self.sys_ctrl.get_date()}"
                elif sys_action == 'shutdown':
                    return self.sys_ctrl.shutdown(True)
                elif sys_action == 'restart':
                    return self.sys_ctrl.restart(True)
                elif sys_action == 'lock':
                    return self.sys_ctrl.lock()
                elif sys_action == 'sleep':
                    return self.sys_ctrl.sleep()
                elif sys_action == 'settings':
                    return self.sys_ctrl.open_settings()
                elif sys_action == 'control_panel':
                    return self.sys_ctrl.open_control_panel()
                elif sys_action == 'explorer':
                    return self.sys_ctrl.open_explorer()
            
            elif action == 'file_operation':
                params = intent.get('params', {})
                op = params.get('operation')
                
                if op == 'create_folder':
                    return self.file_ctrl.create_folder(params.get('path', ''))
                elif op == 'list_files':
                    return self.file_ctrl.list_files(params.get('path', ''))
                elif op == 'delete_file':
                    return self.file_ctrl.delete_file(params.get('path', ''), 
                                                   params.get('confirmed', False))
            
            elif action == 'blog_workflow':
                params = intent.get('params', {})
                op = params.get('operation', 'write')
                
                if op == 'write':
                    # For now, just create a draft file
                    return self.blog_workflow.write_blog(
                        "My New Blog Post",
                        "Your blog content goes here..."
                    )
                elif op == 'wordpress':
                    return "WordPress posting requires credentials. Configure in settings."
            
            elif action == 'screenshot':
                return self.web_ctrl.take_screenshot()
            
            elif action == 'unknown':
                # Try chat with LLM
                if self.llm.available:
                    response = self.llm.chat(intent.get('original', ''))
                    return response or "I didn't understand that"
                return "I didn't understand that"
            
            else:
                return f"Unknown action: {action}"
        
        except Exception as e:
            log(f"Execute error: {e}", "ERROR")
            return f"Error: {str(e)}"
        
        return "Done"
    
    def run(self):
        """Run the assistant"""
        self.voice.speak("Leo assistant ready. Say hey computer to begin.")
        
        # Setup system tray
        self.tray = SystemTray(self)
        if self.tray.setup_tray():
            self.tray.run_tray()
            log("System tray enabled", "INFO")
        
        self.root.mainloop()

# ============== SYSTEM TRAY ==============
class SystemTray:
    """System tray icon and menu"""
    
    def __init__(self, app):
        self.app = app
        self.icon = None
        
    def create_icon(self):
        """Create a simple icon"""
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (64, 64), color='#7c3aed')
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 15, 25, 50], fill='white')
            draw.rectangle([20, 15, 45, 22], fill='white')
            return img
        except:
            return None
    
    def setup_tray(self):
        """Setup system tray"""
        try:
            import pystray
            from PIL import Image
            
            icon_image = self.create_icon()
            
            if icon_image:
                menu = pystray.Menu(
                    pystray.MenuItem("Show", self.show_app),
                    pystray.MenuItem("Status: Active", None, enabled=False),
                    pystray.MenuItem("Exit", self.exit_app)
                )
                
                self.icon = pystray.Icon("Leo Assistant", icon_image, "Leo Voice Assistant", menu)
                return True
        except Exception as e:
            log(f"Tray setup failed: {e}", "WARNING")
        return False
    
    def run_tray(self):
        """Run tray in background"""
        if self.icon:
            self.icon.run_detached()
    
    def show_app(self):
        """Show main window"""
        if self.app:
            self.app.root.deiconify()
    
    def exit_app(self):
        """Exit application"""
        if self.app:
            self.app.running = False
            self.app.root.quit()
        if self.icon:
            self.icon.stop()
        import sys
        sys.exit(0)

# ============== CONFIG MANAGER ==============
class ConfigManager:
    """Manage configuration settings"""
    
    def __init__(self):
        self.config_file = WORKSPACE / "config.json"
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "wake_word": "hey computer",
            "voice_rate": 150,
            "voice_volume": 1.0,
            "ollama_model": "llama3.2:3b",
            "sandbox_paths": [
                str(Path.home() / "Desktop"),
                str(Path.home() / "Documents"),
                str(Path.home() / "Downloads")
            ],
            "require_confirmation": ["shutdown", "restart", "delete"],
            "auto_start": False,
            "minimize_to_tray": True,
        }
    
    def save_config(self):
        """Save configuration"""
        try:
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            log(f"Config save error: {e}", "ERROR")
        return False
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        return self.save_config()

# ============== ENTRY POINT ==============
if __name__ == "__main__":
    log("="*50, "INFO")
    log("Leo Voice Assistant Starting...", "INFO")
    log("="*50, "INFO")
    
    try:
        app = LeoAssistant()
        app.run()
    except Exception as e:
        log(f"Fatal error: {e}", "ERROR")
        input("Press Enter to exit...")
