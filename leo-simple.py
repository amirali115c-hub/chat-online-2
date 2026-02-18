"""
Leo Control Panel - Simple Version
"""
import tkinter as tk
from tkinter import ttk
import subprocess
import webbrowser
import os

WORKSPACE = r"C:\Users\HP\.openclaw\workspace"

def open_url(url):
    webbrowser.open(url)

def open_gmail():
    webbrowser.open("https://mail.google.com")

def open_jobs():
    webbrowser.open("https://www.linkedin.com/jobs/search/?keywords=copywriter&location=Remote")

def open_vscode():
    subprocess.Popen(['code', WORKSPACE])

def open_explorer():
    subprocess.Popen(['explorer.exe', WORKSPACE])

# Simple GUI
root = tk.Tk()
root.title("Leo Control Panel")
root.geometry("350x450")

# Style
root.configure(bg='#1e1e2e')
tk.Label(root, text="Leo Control Panel 🦁", font=('Arial', 16, 'bold'), 
         bg='#7c3aed', fg='white', pady=10).pack(fill='x')

frame = tk.Frame(root, bg='#1e1e2e')
frame.pack(padx=10, pady=10, fill='both', expand=True)

# Jobs
tk.Label(frame, text="Find Jobs", font=('Arial', 12, 'bold'), bg='#1e1e2e', fg='white').pack(pady=5)
ttk.Button(frame, text="LinkedIn Jobs", command=open_jobs).pack(fill='x', pady=2)
ttk.Button(frame, text="Indeed Remote", command=lambda: open_url("https://indeed.com")).pack(fill='x', pady=2)
ttk.Button(frame, text="Upwork", command=lambda: open_url("https://upwork.com")).pack(fill='x', pady=2)

# Email
tk.Label(frame, text="Email", font=('Arial', 12, 'bold'), bg='#1e1e2e', fg='white', pady=10).pack()
ttk.Button(frame, text="Open Gmail", command=open_gmail).pack(fill='x', pady=2)
ttk.Button(frame, text="Job Applications Draft", 
           command=lambda: open_url(f"file://{WORKSPACE}/remote-job-applications.md")).pack(fill='x', pady=2)

# Apps
tk.Label(frame, text="Apps", font=('Arial', 12, 'bold'), bg='#1e1e2e', fg='white', pady=10).pack()
ttk.Button(frame, text="VS Code", command=open_vscode).pack(fill='x', pady=2)
ttk.Button(frame, text="File Explorer", command=open_explorer).pack(fill='x', pady=2)
ttk.Button(frame, text="Browser", command=lambda: subprocess.Popen(
    [r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'])).pack(fill='x', pady=2)

# Status
tk.Label(root, text="Ready", bg='#1e1e2e', fg='gray').pack(pady=5)

root.mainloop()
