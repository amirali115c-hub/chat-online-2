"""
Leo Voice Assistant - Superior Version WITH VOICE
A powerful, privacy-focused voice-controlled PC assistant
Built with Windows-native features + voice input
"""

import subprocess
import webbrowser
import os
import sys
import json
import threading
import time
import queue
from datetime import datetime
from pathlib import Path

# GUI
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# ============== CONFIGURATION ==============
APP_NAME = "Leo Voice Assistant"
VERSION = "2.0.0"
WORKSPACE = r"C:\Users\HP\.openclaw\workspace"
WAKE_WORD = "hey leo"

# App paths
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
    'camera': 'microsoft.windows.camera:',
    'explorer': 'explorer.exe',
    'taskmgr': 'taskmgr.exe',
    'control': 'control.exe',
    'settings': 'ms-settings:',
    'store': 'ms-windows-store:',
}

# Website URLs
WEBSITES = {
    'youtube': 'https://youtube.com',
    'gmail': 'https://gmail.com',
    'google': 'https://google.com',
    'facebook': 'https://facebook.com',
    'twitter': 'https://twitter.com',
    'x': 'https://twitter.com',
    'linkedin': 'https://linkedin.com',
    'reddit': 'https://reddit.com',
    'amazon': 'https://amazon.com',
    'netflix': 'https://netflix.com',
    'whatsapp': 'https://web.whatsapp.com',
    'github': 'https://github.com',
    'stackoverflow': 'https://stackoverflow.com',
    'indeed': 'https://indeed.com',
    'upwork': 'https://upwork.com',
    'fiverr': 'https://fiverr.com',
}

# ============== VOICE ENGINE ==============
class VoiceEngine:
    """Windows native text-to-speech engine"""
    
    def __init__(self):
        self.enabled = True
        self.speaking = False
        
    def speak(self, text):
        """Speak text using Windows SAPI"""
        if not self.enabled:
            return
            
        def _speak():
            self.speaking = True
            try:
                text = text.replace('"', "'").replace('\n', ' ').replace('\r', '')
                cmd = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Rate = 0; $synth.Speak("{text}")'
                subprocess.Popen(
                    ['powershell', '-WindowStyle', 'Hidden', '-Command', cmd],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                time.sleep(0.5)
            except:
                pass
            finally:
                self.speaking = False
        
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()

# ============== VOICE LISTENER ==============
class VoiceListener:
    """Listen for voice commands using Windows Speech Recognition"""
    
    def __init__(self, callback):
        self.callback = callback
        self.listening = False
        self.listening_for_command = False
        self.running = True
        self.voice_thread = None
        
    def start(self):
        """Start listening for wake word"""
        if self.listening:
            return
        self.listening = True
        self.running = True
        self.voice_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.voice_thread.start()
        
    def stop(self):
        """Stop listening"""
        self.listening = False
        self.running = False
        
    def _listen_loop(self):
        """Main listening loop using Windows built-in speech recognition"""
        while self.running and self.listening:
            try:
                # Use PowerShell to listen for speech
                # This uses Windows 10/11 built-in speech recognition
                script = '''
Add-Type -AssemblyName System.Speech
$recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
$recognizer.Initialize([System.Globalization.CultureInfo]::"en-US")
$recognizer.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
$recognizer.SetInputToDefaultAudioDevice()
try {
    $result = $recognizer.Recognize([System.TimeSpan]::FromSeconds(5))
    if ($result) {
        Write-Output $result.Text
    }
} catch {
    Write-Output ""
}
'''
                result = subprocess.run(
                    ['powershell', '-Command', script],
                    capture_output=True,
                    text=True,
                    timeout=8
                )
                
                text = result.stdout.strip().lower()
                
                if text:
                    print(f" Heard: {text}")
                    self.callback(text)
                    
            except subprocess.TimeoutExpired:
                pass
            except Exception as e:
                print(f"Listen error: {e}")
                time.sleep(0.5)

# ============== COMMAND PARSER ==============
class CommandParser:
    """Advanced command parser with pattern matching"""
    
    def __init__(self):
        pass
        
    def parse(self, text):
        """Parse command text"""
        text = text.lower().strip()
        
        # Check for wake word
        if WAKE_WORD in text:
            return 'wake', text.replace(WAKE_WORD, '').strip()
        
        # Open apps
        if 'open' in text or 'launch' in text or 'start' in text:
            for app in APP_PATHS.keys():
                if app in text:
                    return 'open_app', app
        
        # Websites
        for site in WEBSITES.keys():
            if site in text:
                return 'open_website', site
        
        # Jobs
        if 'job' in text:
            return 'find_jobs', ''
        
        # Email
        if 'email' in text or 'gmail' in text:
            return 'check_email', ''
        
        # Search
        if 'search' in text or 'find' in text:
            query = text.replace('search', '').replace('find', '').strip()
            return 'web_search', query
        
        # Time
        if 'time' in text:
            return 'get_time', ''
        
        # Date/Day
        if 'date' in text or 'day' in text:
            return 'get_date', ''
        
        # Shutdown
        if 'shutdown' in text or 'shut down' in text:
            return 'shutdown', ''
        
        # Restart
        if 'restart' in text or 'reboot' in text:
            return 'restart', ''
        
        # Lock
        if 'lock' in text:
            return 'lock', ''
        
        # Sleep
        if 'sleep' in text or 'hibernate' in text:
            return 'sleep', ''
        
        # Explorer
        if 'explorer' in text or 'files' in text:
            return 'open_explorer', ''
        
        # Settings
        if 'settings' in text:
            return 'open_settings', ''
        
        # Control Panel
        if 'control panel' in text:
            return 'open_control', ''
        
        return 'unknown', text

# ============== COMMAND EXECUTOR ==============
class CommandExecutor:
    """Execute parsed commands"""
    
    def __init__(self, voice_engine):
        self.voice = voice_engine
        self.pending_confirmation = None
        
    def execute(self, action, param=""):
        """Execute command"""
        
        if action == 'open_app':
            return self._open_app(param)
        elif action == 'open_website':
            return self._open_website(param)
        elif action == 'find_jobs':
            return self._find_jobs()
        elif action == 'check_email':
            return self._check_email()
        elif action == 'web_search':
            return self._web_search(param)
        elif action == 'get_time':
            return self._get_time()
        elif action == 'get_date':
            return self._get_date()
        elif action == 'shutdown':
            return self._shutdown()
        elif action == 'restart':
            return self._restart()
        elif action == 'lock':
            return self._lock()
        elif action == 'sleep':
            return self._sleep()
        elif action == 'open_explorer':
            return self._open_explorer()
        elif action == 'open_settings':
            return self._open_settings()
        elif action == 'open_control':
            return self._open_control()
        else:
            return f"I didn't understand that. Say help for commands."
    
    def _open_app(self, app_name):
        app_name = app_name.lower().strip()
        for key, path in APP_PATHS.items():
            if key in app_name or app_name in key:
                try:
                    subprocess.Popen(path)
                    return f"Opening {key}"
                except:
                    pass
        return f"Could not find {app_name}"
    
    def _open_website(self, site):
        site = site.lower().strip()
        if site in WEBSITES:
            webbrowser.open(WEBSITES[site])
            return f"Opening {site}"
        webbrowser.open(f'https://{site}')
        return f"Opening {site}"
    
    def _find_jobs(self):
        webbrowser.open('https://www.linkedin.com/jobs')
        return "Opening LinkedIn Jobs"
    
    def _check_email(self):
        webbrowser.open('https://gmail.com')
        return "Opening Gmail"
    
    def _web_search(self, query):
        if not query:
            return "What should I search for?"
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching for {query}"
    
    def _get_time(self):
        now = datetime.now()
        return f"The time is {now.strftime('%I:%M %p')}"
    
    def _get_date(self):
        now = datetime.now()
        return f"Today is {now.strftime('%B %d, %Y')}"
    
    def _shutdown(self):
        if self.pending_confirmation != 'shutdown':
            self.pending_confirmation = 'shutdown'
            return "Say confirm to shutdown in 60 seconds"
        subprocess.run(['shutdown', '/s', '/t', '60'])
        self.pending_confirmation = None
        return "Shutting down in 60 seconds"
    
    def _restart(self):
        if self.pending_confirmation != 'restart':
            self.pending_confirmation = 'restart'
            return "Say confirm to restart in 60 seconds"
        subprocess.run(['shutdown', '/r', '/t', '60'])
        self.pending_confirmation = None
        return "Restarting in 60 seconds"
    
    def _lock(self):
        subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
        return "Locking PC"
    
    def _sleep(self):
        subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0', '1', '0'])
        return "Going to sleep"
    
    def _open_explorer(self):
        subprocess.Popen('explorer.exe')
        return "Opening File Explorer"
    
    def _open_settings(self):
        subprocess.Popen('ms-settings:')
        return "Opening Settings"
    
    def _open_control(self):
        subprocess.Popen('control.exe')
        return "Opening Control Panel"

# ============== MAIN APPLICATION ==============
class LeoAssistant:
    """Main application class"""
    
    def __init__(self):
        self.voice = VoiceEngine()
        self.parser = CommandParser()
        self.executor = CommandExecutor(self.voice)
        self.listener = None
        self.voice_enabled = False
        
        self.setup_gui()
        self.log("Leo Assistant started!")
        
    def setup_gui(self):
        """Setup the GUI"""
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} 🦁 v{VERSION}")
        self.root.geometry("500x650")
        self.root.minsize(400, 500)
        self.root.configure(bg='#1e1e2e')
        
        # Header
        header = tk.Frame(self.root, bg='#7c3aed', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(header, text=f"{APP_NAME} 🦁", 
                        font=('Arial', 18, 'bold'),
                        bg='#7c3aed', fg='white')
        title.pack(pady=15)
        
        # Status with voice indicator
        self.status_frame = tk.Frame(self.root, bg='#1e1e2e')
        self.status_frame.pack(pady=5)
        
        self.status_label = tk.Label(self.status_frame, text="Ready",
                                    font=('Arial', 10),
                                    bg='#1e1e2e', fg='#4ade80')
        self.status_label.pack(side='left')
        
        self.voice_status = tk.Label(self.status_frame, text="🎤 Voice: OFF",
                                    font=('Arial', 9),
                                    bg='#1e1e2e', fg='#666')
        self.voice_status.pack(side='left', padx=10)
        
        # Notebook (Tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Tab 1: Commands
        self.tab_commands = tk.Frame(notebook, bg='#1e1e2e')
        notebook.add(self.tab_commands, text="💬 Commands")
        self.setup_commands_tab()
        
        # Tab 2: Log
        self.tab_log = tk.Frame(notebook, bg='#1e1e2e')
        notebook.add(self.tab_log, text="📝 Log")
        self.setup_log_tab()
        
        # Input area
        input_frame = tk.Frame(self.root, bg='#1e1e2e')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        self.input_entry = tk.Entry(input_frame, font=('Arial', 12),
                                   bg='#2d2d2d', fg='white', insertbackground='white')
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.input_entry.bind('<Return>', lambda e: self.process_input())
        
        send_btn = tk.Button(input_frame, text="Send", 
                           command=self.process_input,
                           bg='#7c3aed', fg='white',
                           font=('Arial', 10, 'bold'),
                           padx=15, pady=5)
        send_btn.pack(side='right')
        
        # Voice button
        self.voice_btn = tk.Button(input_frame, text="🎤",
                            command=self.toggle_voice,
                            bg='#2d2d2d', fg='white',
                            font=('Arial', 12),
                            padx=10, pady=5)
        self.voice_btn.pack(side='right', padx=(5, 0))
        
        # Version
        ver = tk.Label(self.root, text=f"v{VERSION} | Say '{WAKE_WORD}' to activate",
                      font=('Arial', 8), bg='#1e1e2e', fg='#666')
        ver.pack(pady=(0, 5))
    
    def setup_commands_tab(self):
        """Setup commands tab"""
        frame = tk.Frame(self.tab_commands, bg='#1e1e2e')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        commands = [
            ("Wake Word", f"Say '{WAKE_WORD}' to activate"),
            ("🌐 Websites", "open youtube / open gmail / open linkedin"),
            ("🔍 Search", "search google for jobs / search for weather"),
            ("💼 Jobs", "find jobs / check indeed / open upwork"),
            ("💻 Apps", "open chrome / open brave / open spotify / open vscode"),
            ("📁 Files", "open explorer / create folder"),
            ("🔊 Volume", "volume up / volume down / mute"),
            ("⏰ Time", "what time is it / what day is it / date"),
            ("🔒 Power", "shutdown / restart / lock / sleep"),
            ("⚙️ System", "open settings / open control panel"),
        ]
        
        for category, cmd in commands:
            tk.Label(frame, text=category, font=('Arial', 11, 'bold'),
                    bg='#1e1e2e', fg='#7c3aed').pack(anchor='w', pady=(10, 2))
            tk.Label(frame, text=cmd, font=('Arial', 9),
                    bg='#1e1e2e', fg='#888').pack(anchor='w', pady=(0, 5))
    
    def setup_log_tab(self):
        """Setup log tab"""
        self.log_area = scrolledtext.ScrolledText(self.tab_log, 
                                                 bg='#2d2d2d', fg='white',
                                                 font=('Consolas', 9))
        self.log_area.pack(fill='both', expand=True, padx=10, pady=10)
    
    def log(self, message):
        """Add to log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
    
    def toggle_voice(self):
        """Toggle voice input"""
        if not self.voice_enabled:
            # Try to start voice listening
            try:
                self.listener = VoiceListener(self.on_voice_command)
                self.listener.start()
                self.voice_enabled = True
                self.voice_status.config(text="🎤 Voice: ON", fg='#4ade80')
                self.voice_btn.config(bg='#4ade80', fg='black')
                self.log("Voice listening started - say 'hey leo' to activate")
                self.voice.speak("Voice activated. Say hey leo to give commands.")
            except Exception as e:
                self.log(f"Voice error: {e}")
                self.voice.speak("Voice not available. Please type commands.")
        else:
            # Stop voice
            if self.listener:
                self.listener.stop()
            self.voice_enabled = False
            self.voice_status.config(text="🎤 Voice: OFF", fg='#666')
            self.voice_btn.config(bg='#2d2d2d', fg='white')
            self.log("Voice listening stopped")
    
    def on_voice_command(self, text):
        """Handle voice command"""
        self.root.after(0, lambda: self._process_voice(text))
    
    def _process_voice(self, text):
        """Process voice input"""
        self.log(f"Voice: {text}")
        
        # Check for wake word
        action, param = self.parser.parse(text)
        
        if action == 'wake':
            if param:
                # Process command after wake word
                action, param = self.parser.parse(param)
                result = self.executor.execute(action, param)
                self.log(f"Leo: {result}")
                self.voice.speak(result)
            else:
                # Just wake word - ready for command
                self.log("Listening for command...")
                self.voice.speak("I'm listening")
        else:
            # Process directly
            result = self.executor.execute(action, param)
            self.log(f"Leo: {result}")
            self.voice.speak(result)
    
    def process_input(self):
        """Process text input"""
        text = self.input_entry.get().strip()
        if not text:
            return
            
        self.input_entry.delete(0, tk.END)
        
        # Check for confirmation
        if self.executor.pending_confirmation and 'confirm' in text.lower():
            action = self.executor.pending_confirmation
            self.executor.pending_confirmation = None
            result = self.executor.execute(action, "")
            self.log(f"Confirmed: {result}")
            self.voice.speak(result)
            return
        
        # Parse and execute
        self.log(f"You: {text}")
        action, param = self.parser.parse(text)
        result = self.executor.execute(action, param)
        self.log(f"Leo: {result}")
        self.voice.speak(result)
    
    def run(self):
        """Run the app"""
        self.voice.speak("Leo assistant ready. Click the microphone to enable voice.")
        self.root.mainloop()

# ============== ENTRY POINT ==============
if __name__ == "__main__":
    app = LeoAssistant()
    app.run()
