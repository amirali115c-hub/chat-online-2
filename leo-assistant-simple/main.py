"""
Leo Assistant - Windows Native Version
Uses Windows built-in speech (SAPI) and automation
No pip packages needed!
"""

import subprocess
import webbrowser
import os
import time
from datetime import datetime

# GUI
import tkinter as tk
from tkinter import scrolledtext

# ============== CONFIGURATION ==============
WAKE_WORD = "hey computer"

# ============== SPEAK FUNCTION (Windows SAPI) ==============
def speak(text):
    """Use Windows built-in speech"""
    try:
        # Use PowerShell to speak
        cmd = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("{text}")'
        subprocess.Popen(['powershell', '-Command', cmd], 
                       creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        print(f"Speak error: {e}")

# ============== LISTEN FUNCTION ==============
def listen_for_wake():
    """Simple listen using Windows audio"""
    # For now, return True (always listening)
    return True

# ============== COMMAND PARSER ==============
def parse_command(text):
    """Parse command using simple pattern matching"""
    text = text.lower().strip()
    
    # Open Apps
    if 'open' in text or 'launch' in text:
        if 'chrome' in text:
            return 'open_app', {'app': 'chrome'}
        if 'brave' in text:
            return 'open_app', {'app': 'brave'}
        if 'spotify' in text:
            return 'open_app', {'app': 'spotify'}
        if 'notepad' in text:
            return 'open_app', {'app': 'notepad'}
        if 'calculator' in text:
            return 'open_app', {'app': 'calculator'}
        if 'vscode' in text or 'vs code' in text:
            return 'open_app', {'app': 'vscode'}
        if 'terminal' in text or 'cmd' in text:
            return 'open_app', {'app': 'terminal'}
    
    # Websites
    if 'youtube' in text:
        return 'open_url', {'url': 'https://youtube.com'}
    if 'gmail' in text:
        return 'open_url', {'url': 'https://gmail.com'}
    if 'linkedin' in text:
        return 'open_url', {'url': 'https://linkedin.com'}
    if 'facebook' in text:
        return 'open_url', {'url': 'https://facebook.com'}
    
    # Jobs
    if 'job' in text:
        return 'open_url', {'url': 'https://www.linkedin.com/jobs'}
    
    # Search
    if 'search' in text:
        query = text.replace('search', '').replace('google', '').strip()
        return 'search', {'query': query}
    
    # Time/Date
    if 'time' in text:
        return 'get_time', {}
    if 'date' in text or 'day' in text:
        return 'get_date', {}
    
    # System
    if 'shutdown' in text:
        return 'shutdown', {}
    if 'restart' in text:
        return 'restart', {}
    if 'lock' in text:
        return 'lock', {}
    
    # Files
    if 'explorer' in text or 'file' in text and 'open' in text:
        return 'explorer', {}
    
    if 'control panel' in text or 'settings' in text:
        return 'control_panel', {}
    
    return 'unknown', {}

# ============== EXECUTE COMMAND ==============
def execute_command(cmd_type, params):
    """Execute the command"""
    
    if cmd_type == 'open_app':
        app = params.get('app', '')
        app_map = {
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'brave': r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
            'spotify': r'C:\Users\HP\AppData\Roaming\Spotify\Spotify.exe',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'vscode': 'code',
            'terminal': 'cmd.exe',
        }
        
        if app in app_map:
            path = app_map[app]
            try:
                subprocess.Popen(path)
                return f"Opening {app}"
            except:
                return f"Could not open {app}"
        
        # Try direct
        try:
            subprocess.Popen(app)
            return f"Opening {app}"
        except:
            return f"App not found: {app}"
    
    if cmd_type == 'open_url':
        url = params.get('url', '')
        webbrowser.open(url)
        return "Done"
    
    if cmd_type == 'search':
        query = params.get('query', '')
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching for {query}"
    
    if cmd_type == 'get_time':
        now = datetime.now()
        return f"The time is {now.strftime('%I:%M %p')}"
    
    if cmd_type == 'get_date':
        now = datetime.now()
        return f"Today is {now.strftime('%B %d, %Y')}"
    
    if cmd_type == 'shutdown':
        return "Say confirm to shutdown"
    
    if cmd_type == 'restart':
        return "Say confirm to restart"
    
    if cmd_type == 'lock':
        subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
        return "Locking computer"
    
    if cmd_type == 'explorer':
        subprocess.Popen('explorer.exe')
        return "Opening File Explorer"
    
    if cmd_type == 'control_panel':
        subprocess.Popen('control.exe')
        return "Opening Control Panel"
    
    return "Command not recognized"

# ============== GUI APPLICATION ==============
class LeoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Leo Assistant")
        self.root.geometry("400x450")
        self.root.configure(bg='#1e1e2e')
        
        self.setup_gui()
        self.running = True
        
    def setup_gui(self):
        # Header
        tk.Label(self.root, text="Leo Assistant 🦁", 
                font=('Arial', 16, 'bold'),
                bg='#7c3aed', fg='white', pady=10).pack(fill='x')
        
        # Status
        self.status = tk.Label(self.root, text="Ready",
                             font=('Arial', 11), bg='#1e1e2e', fg='#00ff00')
        self.status.pack(pady=5)
        
        # Commands list
        tk.Label(self.root, text="Commands:", font=('Arial', 11, 'bold'),
                bg='#1e1e2e', fg='white').pack(pady=5)
        
        commands = """Open Chrome / Open Brave / Open Spotify
Open YouTube / Open Gmail / Open LinkedIn  
Search Google for query
Find Jobs / Check Email
Whats the time / What day is it
Shutdown / Restart / Lock
Open File Explorer / Open Notepad
Open Calculator / Open VS Code"""
        
        self.cmd_text = tk.Label(self.root, text=commands, font=('Arial', 9),
                                bg='#1e1e2e', fg='#aaaaaa', justify='left')
        self.cmd_text.pack(pady=10)
        
        # Log area
        self.log = scrolledtext.ScrolledText(self.root, height=10,
                                           bg='#2d2d2d', fg='#ffffff')
        self.log.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Buttons
        btn_frame = tk.Frame(self.root, bg='#1e1e2e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🎤 Listen", bg='#4ade80', font=('Arial', 10),
                command=self.manual_listen).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Exit", bg='#f87171', font=('Arial', 10),
                command=self.exit).pack(side='left', padx=5)
        
        # Manual input
        tk.Label(self.root, text="Or type command:", bg='#1e1e2e', fg='white').pack()
        
        self.input_entry = tk.Entry(self.root, font=('Arial', 10))
        self.input_entry.pack(padx=10, pady=5, fill='x')
        self.input_entry.bind('<Return>', self.on_enter)
        
    def log_msg(self, msg):
        self.log.insert(tk.END, f"{msg}\n")
        self.log.see(tk.END)
        
    def manual_listen(self):
        # For now, just log - voice needs microphone
        self.log_msg("Voice input not available yet")
        speak("Voice input coming soon")
        
    def on_enter(self, event):
        text = self.input_entry.get().strip()
        if text:
            self.input_entry.delete(0, tk.END)
            self.process_command(text)
        
    def process_command(self, text):
        self.log_msg(f"You: {text}")
        cmd_type, params = parse_command(text)
        result = execute_command(cmd_type, params)
        self.log_msg(f"Leo: {result}")
        speak(result)
        
    def exit(self):
        self.running = False
        self.root.quit()
        
    def run(self):
        speak("Leo assistant ready")
        self.root.mainloop()

# ============== RUN ==============
if __name__ == "__main__":
    app = LeoApp()
    app.run()
