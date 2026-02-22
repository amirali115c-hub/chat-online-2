# Helper Scripts Skill

## Description
Access a collection of helper scripts that extend Leo's capabilities for automation, data management, and system operations.

## Tools Used
- `exec` - Run Python helper scripts
- `read` - Read script outputs and logs
- `write` - Create/modify helper scripts

## When to Use
When you need to:
- Backup workspace files
- Check service status
- Search through memory
- Auto-commit changes
- Manage JSON data
- Save quick notes

## How to Use

### 1. Check Services Status
```python
# Run: python helpers.py check
```
Returns status of OpenClaw, Ollama, Git

### 2. Backup Workspace
```python
# Run: python helpers.py backup
```
Creates timestamped backup in `backups/` folder

### 3. Search Memory
```python
# Run: python helpers.py search "query"
```
Search all memory files for a term

### 4. Auto Commit & Push
```python
# Run: python helpers.py commit "Your message"
```
Adds, commits, and pushes all changes

### 5. Save Quick Note
```python
# Add to daily memory via Python
save_quick_note("Your note", "tag")
```

## File Location
`C:\Users\HP\.openclaw\workspace\helpers.py`

## Extending Helpers
Add new functions to `helpers.py` to extend Leo's capabilities:
```python
def new_helper_function(arg):
    # Your logic here
    return result
```

## Requirements
- Python 3.x installed
- Access to workspace directory
