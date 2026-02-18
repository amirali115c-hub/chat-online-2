"""
Leo Control Panel - Full Laptop Control App
Features: Email, Jobs, Copywriting, Files, System Control
Created by: Leo (AI Assistant)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import webbrowser
import os
from datetime import datetime

# ============== CONFIGURATION ==============
WORKSPACE = r"C:\Users\HP\.openclaw\workspace"
EMAIL_SIGNATURE = """
Best regards,
Amir Ali
amircontentwriter@gmail.com
WhatsApp: +92 320 4779972
"""

# ============== JOB LINKS ==============
JOB_SITES = {
    "LinkedIn Jobs": "https://www.linkedin.com/jobs/search/?keywords=copywriter&location=Remote",
    "Indeed Remote": "https://www.indeed.com/jobs?q=copywriter&l=Remote",
    "Indeed Pakistan": "https://www.indeed.com/jobs?q=copywriter&l=Lahore%2C+Pakistan",
    "Upwork": "https://www.upwork.com/nx/jobs/search/?category2=Webwriting&subcategory2=ContentWriting",
    "Fiverr": "https://www.fiverr.com/categories/content/writing",
    "PeoplePerHour": "https://www.peopleperhour.com/freelance-jobs/content-writing",
}

# ============== EMAIL TEMPLATES ==============
EMAIL_TEMPLATES = {
    "Job Application": """Subject: Application for {position} Position

Hi {hiring_manager},

I'm Amir Ali, a professional SEO copywriter with 4+ years of experience. I'm excited to apply for the {position} role at {company}.

What I offer:
- SEO content that ranks on Google
- Website copy that converts visitors to customers
- Blog posts, landing pages, product descriptions
- Experience with US and Dubai clients

I'm available for remote work and eager to contribute to your team.

{signature}""",

    "Freelance Inquiry": """Subject: Professional Copywriting Services Available

Hi,

I'm Amir Ali, an SEO copywriter with 4+ years of experience helping businesses attract more customers through compelling content.

I specialize in:
- Website copy that converts
- SEO blogs that rank
- Landing pages
- Product descriptions

Would you be open to a brief call to discuss your needs?

{signature}""",

    "Follow Up": """Subject: Following Up - {position} Application

Hi,

I recently applied for the {position} position and wanted to follow up on my application.

I'm very excited about this opportunity and would love to discuss how I can contribute to your team.

{signature}""",
}

# ============== FUNCTIONS ==============
def open_url(url):
    webbrowser.open(url)

def open_gmail_compose(to='', subject='', body=''):
    import urllib.parse
    base_url = "https://mail.google.com/mail/u/0/?view=cm&fs=1"
    if to:
        base_url += f"&to={urllib.parse.quote(to)}"
    if subject:
        base_url += f"&su={urllib.parse.quote(subject)}"
    webbrowser.open(base_url)

def open_vscode():
    subprocess.Popen(['code', WORKSPACE])

def open_browser():
    subprocess.Popen([r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'])

def open_file_explorer():
    subprocess.Popen(['explorer.exe', WORKSPACE])

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)

def show_email_template(key):
    template = EMAIL_TEMPLATES[key]
    text_area.delete('1.0', tk.END)
    text_area.insert('1.0', template)

def send_email():
    to = entry_to.get()
    subject = entry_subject.get()
    body = text_area.get('1.0', tk.END)
    open_gmail_compose(to, subject, body)

def copy_email():
    subject = entry_subject.get()
    body = text_area.get('1.0', tk.END)
    full_email = f"Subject: {subject}\n\n{body}"
    copy_to_clipboard(full_email)
    label_status.config(text="Copied to clipboard!", fg="green")

# ============== GUI ==============
root = tk.Tk()
root.title("Leo Control Panel - Full Control")
root.geometry("800x700")

# Style
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('Arial', 10), padding=8)
style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
style.configure('Section.TLabel', font=('Arial', 11, 'bold'))

# Colors
BG_COLOR = '#1e1e2e'
FG_COLOR = '#ffffff'
ACCENT_COLOR = '#7c3aed'

# Header
header = tk.Label(root, text="Leo Control Panel 🦁", font=('Arial', 20, 'bold'), 
                  bg=ACCENT_COLOR, fg='white', pady=10)
header.pack(fill='x')

# Notebook (Tabs)
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

# ============== TAB 1: QUICK LINKS ==============
tab_quick = ttk.Frame(notebook)
notebook.add(tab_quick, text="🚀 Quick Links")

quick_frame = tk.Frame(tab_quick, bg=BG_COLOR)
quick_frame.pack(fill='both', expand=True, padx=10, pady=10)

tk.Label(quick_frame, text="Job Search Sites", font=('Arial', 12, 'bold'), 
         bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)

for name, url in JOB_SITES.items():
    ttk.Button(quick_frame, text=f"🔍 {name}", 
               command=lambda u=url: open_url(u)).pack(fill='x', pady=2)

tk.Label(quick_frame, text="Email", font=('Arial', 12, 'bold'), 
         bg=BG_COLOR, fg=FG_COLOR, pady=10).pack()
ttk.Button(quick_frame, text="📧 Open Gmail", 
           command=lambda: open_url("https://mail.google.com")).pack(fill='x', pady=2)

# ============== TAB 2: EMAIL ==============
tab_email = ttk.Frame(notebook)
notebook.add(tab_email, text="📧 Email")

email_frame = tk.Frame(tab_email, bg=BG_COLOR)
email_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Template buttons
tk.Label(email_frame, text="Email Templates", font=('Arial', 11, 'bold'), 
         bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
for name in EMAIL_TEMPLATES.keys():
    ttk.Button(email_frame, text=f"📝 {name}", 
               command=lambda n=name: show_email_template(n)).pack(fill='x', pady=2)

# To field
tk.Label(email_frame, text="To:", bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w')
entry_to = tk.Entry(email_frame, font=('Arial', 10))
entry_to.pack(fill='x', pady=2)

# Subject field
tk.Label(email_frame, text="Subject:", bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w')
entry_subject = tk.Entry(email_frame, font=('Arial', 10))
entry_subject.pack(fill='x', pady=2)

# Body
tk.Label(email_frame, text="Body:", bg=BG_COLOR, fg=FG_COLOR).pack(anchor='w')
text_area = scrolledtext.ScrolledText(email_frame, font=('Arial', 10), height=8)
text_area.pack(fill='x', pady=2)

# Buttons
btn_frame = tk.Frame(email_frame, bg=BG_COLOR)
btn_frame.pack(fill='x', pady=5)
ttk.Button(btn_frame, text="📤 Open in Gmail", command=send_email).pack(side='left', padx=5)
ttk.Button(btn_frame, text="📋 Copy to Clipboard", command=copy_email).pack(side='left', padx=5)

# ============== TAB 3: APPS ==============
tab_apps = ttk.Frame(notebook)
notebook.add(tab_apps, text="💻 Apps")

apps_frame = tk.Frame(tab_apps, bg=BG_COLOR)
apps_frame.pack(fill='both', expand=True, padx=10, pady=10)

tk.Label(apps_frame, text="Applications", font=('Arial', 12, 'bold'), 
         bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)

ttk.Button(apps_frame, text="💻 VS Code", command=open_vscode).pack(fill='x', pady=2)
ttk.Button(apps_frame, text="🌐 Browser", command=open_browser).pack(fill='x', pady=2)
ttk.Button(apps_frame, text="📁 File Explorer", command=open_file_explorer).pack(fill='x', pady=2)
ttk.Button(apps_frame, text="📝 Notepad", command=lambda: subprocess.Popen(['notepad.exe'])).pack(fill='x', pady=2)
ttk.Button(apps_frame, text="🧮 Calculator", command=lambda: subprocess.Popen(['calc.exe'])).pack(fill='x', pady=2)
ttk.Button(apps_frame, text="🎮 Task Manager", command=lambda: subprocess.Popen(['taskmgr.exe'])).pack(fill='x', pady=2)
ttk.Button(apps_frame, text="⚙️ Settings", command=lambda: subprocess.Popen(['ms-settings:'])).pack(fill='x', pady=2)

# ============== TAB 4: COPYWRITING ==============
tab_copy = ttk.Frame(notebook)
notebook.add(tab_copy, text="✍️ Copywriting")

copy_frame = tk.Frame(tab_copy, bg=BG_COLOR)
copy_frame.pack(fill='both', expand=True, padx=10, pady=10)

tk.Label(copy_frame, text="Research & Tools", font=('Arial', 12, 'bold'), 
         bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)

ttk.Button(copy_frame, text="📄 Copywriting Research Report", 
           command=lambda: open_url(f"file://{WORKSPACE}/copywriting-research-report.md")).pack(fill='x', pady=2)
ttk.Button(copy_frame, text="📋 Job Applications Draft", 
           command=lambda: open_url(f"file://{WORKSPACE}/remote-job-applications.md")).pack(fill='x', pady=2)

tk.Label(copy_frame, text="Quick Tips", font=('Arial', 12, 'bold'), 
         bg=BG_COLOR, fg=FG_COLOR, pady=10).pack()

tips = """
📝 Copywriting Tips:
• "So What?" Test - every sentence must matter
• Use "you" more than "we"
• Be specific - numbers > vague claims
• Active verbs over passive
• Keep headlines under 3 words where possible
• Benefit stacking

🎯 Action Items:
• Apply to 5 jobs daily
• Customize each application
• Follow up after 1 week
• Update LinkedIn regularly
"""
tk.Label(copy_frame, text=tips, bg=BG_COLOR, fg=FG_COLOR, justify='left',
         font=('Arial', 9)).pack(anchor='w', pady=5)

# ============== TAB 5: SYSTEM ==============
tab_system = ttk.Frame(notebook)
notebook.add(tab_system, text="⚙️ System")

system_frame = tk.Frame(tab_system, bg=BG_COLOR)
system_frame.pack(fill='both', expand=True, padx=10, pady=10)

tk.Label(system_frame, text="System Info", font=('Arial', 12, 'bold'), 
         bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)

info = f"""
Computer: {os.environ.get('COMPUTERNAME', 'Unknown')}
User: {os.environ.get('USERNAME', 'Unknown')}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Workspace: {WORKSPACE}
"""
tk.Label(system_frame, text=info, bg=BG_COLOR, fg=FG_COLOR, justify='left',
         font=('Arial', 9)).pack(anchor='w', pady=5)

tk.Label(system_frame, text="Quick Actions", font=('Arial', 12, 'bold'), 
         bg=BG_COLOR, fg=FG_COLOR, pady=10).pack()

ttk.Button(system_frame, text="🔄 Restart Gateway", 
           command=lambda: subprocess.Popen(['openclaw', 'gateway', 'restart'])).pack(fill='x', pady=2)
ttk.Button(system_frame, text="📊 OpenClaw Status", 
           command=lambda: subprocess.Popen(['openclaw', 'status'])).pack(fill='x', pady=2)

# Status
label_status = tk.Label(root, text="Ready - Made by Leo 🦁", font=('Arial', 9), 
                        fg='gray', pady=5)
label_status.pack()

# Run
root.mainloop()
