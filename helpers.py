#!/usr/bin/env python3
"""
Leo Helper Scripts - Extended Capabilities
Location: C:\Users\HP\.openclaw\workspace\helpers\

These scripts extend Leo's functionality.
"""

import json
import os
from pathlib import Path
from datetime import datetime

# ============================================
# HELPER 1: Workspace Backup
# ============================================

def backup_workspace(backup_name=None):
    """Create a timestamped backup of the workspace"""
    workspace = Path(r"C:\Users\HP\.openclaw\workspace")
    backup_dir = Path(r"C:\Users\HP\.openclaw\workspace\backups")
    
    if not backup_name:
        backup_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    backup_path = backup_dir / f"backup_{backup_name}"
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Copy key files
    files_to_backup = ["MEMORY.md", "USER.md", "SOUL.md", "TOOLS.md"]
    
    for file in files_to_backup:
        src = workspace / file
        if src.exists():
            import shutil
            shutil.copy2(src, backup_path / file)
    
    return str(backup_path)

# ============================================
# HELPER 2: JSON Data Manager
# ============================================

class JSONManager:
    """Handle JSON read/write operations"""
    
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or Path(r"C:\Users\HP\.openclaw\workspace\data")
        self.data_dir.mkdir(exist_ok=True)
    
    def read(self, filename):
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        def write(self, return None
    
    filename, data):
        filepath = self.data_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return str(filepath)
    
    def append(self, filename, new_data):
        existing = self.read(filename) or []
        if isinstance(existing, list):
            existing.append(new_data)
        elif isinstance(existing, dict):
            existing.update(new_data)
        return self.write(filename, existing)

# ============================================
# HELPER 3: Quick Notes
# ============================================

def save_quick_note(note, tag="general"):
    """Save a quick note to daily memory"""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = Path(rf"C:\Users\HP\.openclaw\workspace\memory\{today}.md")
    
    timestamp = datetime.now().strftime("%H:%M")
    entry = f"\n### {tag.upper()} - {timestamp}\n{note}\n"
    
    with open(memory_file, 'a') as f:
        f.write(entry)
    
    return f"Saved to {memory_file}"

# ============================================
# HELPER 4: API Status Checker
# ============================================

def check_services():
    """Check status of various services"""
    import subprocess
    
    services = {
        "OpenClaw": "openclaw status",
        "Ollama": "ollama list",
        "Git": "git --version"
    }
    
    results = {}
    for name, cmd in services.items():
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )
            results[name] = "✅ Running" if result.returncode == 0 else f"❌ Error: {result.stderr}"
        except Exception as e:
            results[name] = f"❌ {str(e)}"
    
    return results

# ============================================
# HELPER 5: Memory Search
# ============================================

def search_memory(query, memory_dir=None):
    """Search through memory files"""
    memory_dir = memory_dir or Path(r"C:\Users\HP\.openclaw\workspace\memory")
    results = []
    
    for md_file in memory_dir.glob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if query.lower() in content.lower():
                    # Find context around match
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            context = '\n'.join(lines[max(0,i-2):min(len(lines),i+3)])
                            results.append({
                                'file': md_file.name,
                                'line': i+1,
                                'context': context
                            })
        except Exception as e:
            continue
    
    return results

# ============================================
# HELPER 6: Commit & Push
# ============================================

def auto_commit(message):
    """Auto commit workspace changes"""
    import subprocess
    workspace = r"C:\Users\HP\.openclaw\workspace"
    
    commands = [
        f'cd "{workspace}" && git add -A',
        f'cd "{workspace}" && git commit -m "{message}"',
        f'cd "{workspace}" && git push'
    ]
    
    results = []
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        results.append(result.stdout + result.stderr)
    
    return '\n'.join(results)

# ============================================
# MAIN - Run helpers directly
# ============================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python helpers.py <command> [args]")
        print("Commands: backup, note, check, search, commit")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "backup":
        result = backup_workspace()
        print(f"Backup created: {result}")
    
    elif cmd == "check":
        results = check_services()
        for service, status in results.items():
            print(f"{service}: {status}")
    
    elif cmd == "search" and len(sys.argv) > 2:
        query = sys.argv[2]
        results = search_memory(query)
        print(f"Found {len(results)} matches:")
        for r in results:
            print(f"  - {r['file']}:{r['line']}")
            print(f"    {r['context'][:100]}...")
    
    elif cmd == "commit" and len(sys.argv) > 2:
        message = ' '.join(sys.argv[2:])
        result = auto_commit(message)
        print(result)
    
    else:
        print(f"Unknown command: {cmd}")
