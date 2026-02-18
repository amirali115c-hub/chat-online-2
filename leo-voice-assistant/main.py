"""
Leo Voice Assistant - Lightweight Version
No AI/ML required - Works offline with pattern matching
"""

import threading
import queue
import subprocess
import os
import webbrowser
import time
from datetime import datetime
import json

# GUI
import tkinter as tk
from tkinter import scrolledtext

# Voice
import speech_recognition as sr
import pyttsx3

# ============== CONFIGURATION ==============
WAKE_WORD = "hey computer"
APP_FOLDER = r"C:\Users\HP\.openclaw\workspace\leo-voice-assistant"

# ============== VOICE ENGINE ==============
class VoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 1.0)
        
    def speak(self, text):
        """Speak text using local TTS"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

# ============== SPEECH RECOGNITION ==============
class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        print("Calibrating microphone...")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Calibration complete!")
        except Exception as e:
            print(f"Microphone error: {e}")
    
    def listen(self, timeout=8):
        """Listen for voice input"""
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=12)
            
            # Try Google first (needs internet), fall back to vosk
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except:
                try:
                    text = self.recognizer.recognize_vosk(audio)
                    return text
                except:
                    return None
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"Recognition error: {e}")
            return None

# ============== COMMAND PARSER (No AI) ==============
class CommandParser:
    """Simple pattern-based command parser - no AI needed"""
    
    def __init__(self):
        self.commands = {
            # Open Apps
            r'open\s+(.+)': self.parse_open_app,
            r'launch\s+(.+)': self.parse_open_app,
            r'start\s+(.+)': self.parse_open_app,
            
            # Close Apps
            r'close\s+(.+)': self.parse_close_app,
            r'quit\s+(.+)': self.parse_close_app,
            r'exit\s+(.+)': self.parse_close_app,
            
            # Web Search
            r'search\s+(.+?)\s+for\s+(.+)': self.parse_web_search,
            r'google\s+(.+)': self.parse_web_search,
            r'look\s+up\s+(.+)': self.parse_web_search,
            
            # Open Website
            r'open\s+(youtube|gmail|facebook|twitter|linkedin|reddit|amazon|netflix)': self.parse_website,
            r'go\s+to\s+(.+)': self.parse_website,
            
            # System Control
            r'volume\s+up': lambda p: ('system_control', {'action': 'volume_up'}),
            r'volume\s+down': lambda p: ('system_control', {'action': 'volume_down'}),
            r'mute': lambda p: ('system_control', {'action': 'mute'}),
            r'unmute': lambda p: ('system_control', {'action': 'unmute'}),
            
            # Time/Date
            r'time': lambda p: ('system_control', {'action': 'get_time'}),
            r'date': lambda p: ('system_control', {'action': 'get_date'}),
            r'what\s+(day|date)': lambda p: ('system_control', {'action': 'get_date'}),
            
            # System
            r'shutdown': lambda p: ('system_control', {'action': 'shutdown'}),
            r'restart': lambda p: ('system_control', {'action': 'restart'}),
            r'sleep': lambda p: ('system_control', {'action': 'sleep'}),
            r'lock': lambda p: ('system_control', {'action': 'lock'}),
            
            # Files
            r'open\s+folder': self.parse_open_folder,
            r'open\s+file': self.parse_open_file,
            r'create\s+folder': self.parse_create_folder,
            
            # Copywriting/Work
            r'find\s+jobs': lambda p: ('open_url', {'url': 'https://www.linkedin.com/jobs'}),
            r'check\s+email': lambda p: ('open_url', {'url': 'https://gmail.com'}),
            r'open\s+(my\s+)?(resume|cv)': lambda p: ('open_file', {'path': f'{APP_FOLDER}/../resume.pdf'}),
            
            # Control Panel
            r'open\s+(control\s+panel|settings)': lambda p: ('system_control', {'action': 'control_panel'}),
            r'open\s+file\s+explorer': lambda p: ('system_control', {'action': 'file_explorer'}),
            
            # Calculator/Notepad
            r'open\s+calculator': lambda p: ('open_app', {'app': 'calc'}),
            r'open\s+notepad': lambda p: ('open_app', {'app': 'notepad'}),
            r'open\s+terminal': lambda p: ('open_app', {'app': 'cmd'}),
            r'open\s+powershell': lambda p: ('open_app', {'app': 'powershell'}),
        }
    
    def parse(self, text):
        """Parse command using pattern matching"""
        import re
        
        text = text.lower().strip()
        
        for pattern, handler in self.commands.items():
            match = re.search(pattern, text)
            if match:
                try:
                    return handler(match.groups())
                except:
                    pass
        
        return ('unknown', {})
    
    def parse_open_app(self, groups):
        app = groups[0] if groups else ""
        return ('open_app', {'app': app})
    
    def parse_close_app(self, groups):
        app = groups[0] if groups else ""
        return ('close_app', {'app': app})
    
    def parse_web_search(self, groups):
        if len(groups) >= 2:
            query = groups[1]
        else:
            query = groups[0] if groups else ""
        return ('web_search', {'query': query})
    
    def parse_website(self, groups):
        site = groups[0] if groups else ""
        return ('open_website', {'site': site})
    
    def parse_open_folder(self, groups):
        return ('system_control', {'action': 'file_explorer'})
    
    def parse_open_file(self, groups):
        return ('system_control', {'action': 'open_file'})
    
    def parse_create_folder(self, groups):
        return ('file_operation', {'operation': 'create_folder'})

# ============== COMMAND EXECUTOR ==============
class CommandExecutor:
    def __init__(self, voice_engine):
        self.voice = voice_engine
        
        # App mappings
        self.app_map = {
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'brave': r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
            'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
            'spotify': r'C:\Users\HP\AppData\Roaming\Spotify\Spotify.exe',
            'discord': r'C:\Users\HP\AppData\Local\Discord\Update.exe',
            'slack': r'C:\Users\HP\AppData\Local\slack\slack.exe',
            'vscode': 'code',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'cmd': 'cmd.exe',
            'terminal': 'cmd.exe',
            'powershell': 'powershell.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'paint': 'mspaint.exe',
            'camera': 'microsoft.windows.camera:',
        }
        
        # Website URLs
        self.sites = {
            'youtube': 'https://youtube.com',
            'gmail': 'https://gmail.com',
            'facebook': 'https://facebook.com',
            'twitter': 'https://twitter.com',
            'linkedin': 'https://linkedin.com',
            'reddit': 'https://reddit.com',
            'amazon': 'https://amazon.com',
            'netflix': 'https://netflix.com',
            'whatsapp': 'https://web.whatsapp.com',
        }
    
    def execute(self, command_type, params):
        """Execute the parsed command"""
        
        handlers = {
            'open_app': self.open_app,
            'close_app': self.close_app,
            'web_search': self.web_search,
            'open_website': self.open_website,
            'system_control': self.system_control,
            'open_url': self.open_url,
            'open_file': self.open_file,
            'file_operation': self.file_operation,
        }
        
        handler = handlers.get(command_type, self.unknown_command)
        return handler(params)
    
    def open_app(self, params):
        app_name = params.get('app', '').lower().strip()
        
        # Check mapped apps
        if app_name in self.app_map:
            path = self.app_map[app_name]
            try:
                subprocess.Popen(path)
                return f"Opening {app_name}"
            except:
                pass
        
        # Try direct open
        try:
            subprocess.Popen(app_name)
            return f"Opening {app_name}"
        except:
            return f"Sorry, I couldn't find {app_name}"
    
    def close_app(self, params):
        app_name = params.get('app', '').lower().strip()
        
        # Common process names
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
        
        proc_name = process_map.get(app_name, f'{app_name}.exe')
        
        try:
            subprocess.run(['taskkill', '/F', '/IM', proc_name], 
                         capture_output=True)
            return f"Closing {app_name}"
        except:
            return f"Couldn't close {app_name}"
    
    def web_search(self, params):
        query = params.get('query', '')
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching for {query}"
    
    def open_website(self, params):
        site = params.get('site', '').lower()
        
        if site in self.sites:
            url = self.sites[site]
            webbrowser.open(url)
            return f"Opening {site}"
        
        # Try as URL
        url = site if site.startswith('http') else f'https://{site}'
        webbrowser.open(url)
        return f"Opening {site}"
    
    def open_url(self, params):
        url = params.get('url', '')
        webbrowser.open(url)
        return "Done"
    
    def open_file(self, params):
        path = params.get('path', '')
        if path and os.path.exists(path):
            os.startfile(path)
            return "Opening file"
        return "File not found"
    
    def system_control(self, params):
        action = params.get('action', '')
        
        if action == 'get_time':
            now = datetime.now()
            return f"The time is {now.strftime('%I:%M %p')}"
        
        elif action == 'get_date':
            now = datetime.now()
            return f"Today is {now.strftime('%B %d, %Y')}"
        
        elif action == 'volume_up':
            # Use nircmd or pycaw if available
            return "Turning up volume"
        
        elif action == 'volume_down':
            return "Turning down volume"
        
        elif action == 'mute':
            return "Muting"
        
        elif action == 'control_panel':
            subprocess.Popen('control.exe')
            return "Opening Control Panel"
        
        elif action == 'file_explorer':
            subprocess.Popen('explorer.exe')
            return "Opening File Explorer"
        
        elif action == 'shutdown':
            return "Say 'confirm shutdown' to confirm"
        
        elif action == 'restart':
            return "Say 'confirm restart' to confirm"
        
        elif action == 'sleep':
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0', '1', '0'])
            return "Going to sleep"
        
        elif action == 'lock':
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
            return "Locking computer"
        
        return "Unknown action"
    
    def file_operation(self, params):
        operation = params.get('operation', '')
        
        if operation == 'create_folder':
            return "What should I name the folder?"
        
        return "File operation not implemented"
    
    def unknown_command(self, params):
        return "I didn't understand that"

# ============== MAIN APPLICATION ==============
class LeoAssistant:
    def __init__(self):
        self.voice_engine = VoiceEngine()
        self.speech_recognizer = SpeechRecognizer()
        self.command_parser = CommandParser()
        self.command_executor = CommandExecutor(self.voice_engine)
        
        self.is_listening = False
        self.running = True
        self.awaiting_confirmation = False
        
        # GUI
        self.root = tk.Tk()
        self.root.title("Leo Voice Assistant")
        self.root.geometry("450x550")
        self.root.configure(bg='#1e1e2e')
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI"""
        
        # Header
        header = tk.Label(self.root, text="Leo Voice Assistant 🦁", 
                        font=('Arial', 18, 'bold'),
                        bg='#7c3aed', fg='white', pady=12)
        header.pack(fill='x')
        
        # Status
        self.status_label = tk.Label(self.root, text="Status: Ready - Say 'Hey Computer'",
                                    font=('Arial', 11), bg='#1e1e2e', fg='#00ff00')
        self.status_label.pack(pady=8)
        
        # Log
        self.log_area = scrolledtext.ScrolledText(self.root, height=22,
                                                   bg='#2d2d2d', fg='#ffffff',
                                                   font=('Consolas', 9))
        self.log_area.pack(padx=10, pady=5, fill='both', expand=True)
        
        # Buttons
        btn_frame = tk.Frame(self.root, bg='#1e1e2e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🎤 Start", font=('Arial', 10),
                 bg='#4ade80', fg='black', padx=15, pady=5,
                 command=self.start_listening).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="⏹ Stop", font=('Arial', 10),
                 bg='#f87171', fg='black', padx=15, pady=5,
                 command=self.stop_listening).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Exit", font=('Arial', 10),
                 bg='#94a3b8', fg='black', padx=15, pady=5,
                 command=self.exit_app).pack(side='left', padx=5)
        
        # Command Help
        help_text = """Commands: Open Chrome/Brave/Spotify | Search Google for... | 
Open YouTube/Gmail | Volume Up/Down | What's the Time? |
Shutdown | Open Notepad | Find Jobs | Check Email"""
        tk.Label(self.root, text=help_text, font=('Arial', 8), 
                bg='#1e1e2e', fg='#888888', wraplength=400).pack(pady=2)
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
    
    def start_listening(self):
        """Start voice listening"""
        self.is_listening = True
        self.status_label.config(text="Status: Listening for 'Hey Computer'...", fg='#00ff00')
        self.log("Started listening...")
        
        thread = threading.Thread(target=self.voice_loop)
        thread.daemon = True
        thread.start()
    
    def stop_listening(self):
        """Stop voice listening"""
        self.is_listening = False
        self.status_label.config(text="Status: Stopped", fg='#ff0000')
        self.log("Stopped listening")
    
    def voice_loop(self):
        """Main voice loop"""
        while self.is_listening:
            try:
                # Wait for wake word
                self.log("Waiting for wake word...")
                wake_text = self.speech_recognizer.listen(timeout=5)
                
                if wake_text and WAKE_WORD in wake_text.lower():
                    self.log("Wake word detected!")
                    self.voice_engine.speak("Yes?")
                    
                    # Listen for command
                    command_text = self.speech_recognizer.listen(timeout=10)
                    
                    if command_text:
                        self.log(f"You said: {command_text}")
                        self.process_command(command_text)
                    else:
                        self.log("Didn't hear anything")
                        
            except Exception as e:
                print(f"Voice loop error: {e}")
                time.sleep(1)
    
    def process_command(self, text):
        """Process voice command"""
        self.status_label.config(text="Status: Processing...", fg='#ffff00')
        
        # Check for confirmation
        if self.awaiting_confirmation:
            if 'confirm' in text.lower():
                if self.pending_action == 'shutdown':
                    os.system('shutdown /s /t 60')
                    self.voice_engine.speak("Shutting down in 60 seconds")
                    self.log("Shutdown initiated")
                elif self.pending_action == 'restart':
                    os.system('shutdown /r /t 60')
                    self.voice_engine.speak("Restarting in 60 seconds")
                    self.log("Restart initiated")
                self.awaiting_confirmation = False
                self.pending_action = None
            else:
                self.voice_engine.speak("Cancelled")
                self.awaiting_confirmation = False
            return
        
        # Check for shutdown/restart confirmation
        if 'shutdown' in text.lower():
            self.voice_engine.speak("Say confirm to shutdown")
            self.awaiting_confirmation = True
            self.pending_action = 'shutdown'
            return
        
        if 'restart' in text.lower():
            self.voice_engine.speak("Say confirm to restart")
            self.awaiting_confirmation = True
            self.pending_action = 'restart'
            return
        
        # Parse command
        command_type, params = self.command_parser.parse(text)
        self.log(f"Command: {command_type} | Params: {params}")
        
        # Execute
        result = self.command_executor.execute(command_type, params)
        self.log(f"Result: {result}")
        
        # Speak feedback
        self.voice_engine.speak(result)
        
        self.status_label.config(text="Status: Listening...", fg='#00ff00')
    
    def exit_app(self):
        """Exit the application"""
        self.running = False
        self.is_listening = False
        self.root.quit()
    
    def run(self):
        """Run the application"""
        try:
            self.voice_engine.speak("Leo assistant ready. Say hey computer to activate.")
        except:
            pass
        self.root.mainloop()

# ============== ENTRY POINT ==============
if __name__ == "__main__":
    print("Starting Leo Voice Assistant...")
    app = LeoAssistant()
    app.run()
