# Leo Helpers

## Description
Extended automation and helper capabilities for Leo AI. Provides backup, service monitoring, memory search, and auto-commit functions.

## Tools Used
- `exec` - Run Python helper scripts and shell commands
- `read` - Read files, logs, and script outputs
- `write` - Create/modify files and scripts

## When to Use
When you need to:
- Backup workspace or specific files
- Check status of services (OpenClaw, Ollama, Git)
- Search through memory files
- Auto-commit and push changes to Git
- Manage JSON data files
- Run automation scripts

## How to Use

### 1. Check Services
```bash
python "C:\Users\HP\.openclaw\workspace\helpers.py" check
```
Checks if OpenClaw, Ollama, and Git are running.

### 2. Backup Workspace
```bash
python "C:\Users\HP\.openclaw\workspace\helpers.py" backup
```
Creates timestamped backup in `backups/` folder.

### 3. Search Memory
```bash
python "C:\Users\HP\.openclaw\workspace\helpers.py" search "query"
```
Search all memory files for a term.

### 4. Auto Commit & Push
```bash
python "C:\Users\HP\.openclaw\workspace\helpers.py" commit "Your commit message"
```
Adds, commits, and pushes all changes to GitHub.

## Script Location
`C:\Users\HP\.openclaw\workspace\helpers.py`

## Requirements
- Python 3.x installed on the system
- Git installed and configured
- Access to workspace directory

## Adding New Helpers
To add new helper functions, edit `helpers.py` and add a new function:
```python
def new_helper_function(arg1, arg2):
    # Your logic here
    return result
```

Then call it from command line:
```bash
python helpers.py new_helper_function arg1 arg2
```
