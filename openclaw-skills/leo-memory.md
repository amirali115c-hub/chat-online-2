# Leo Memory

## Description
Persistent memory management for AI assistants. Provides file-based long-term and short-term memory capabilities.

## Tools Used
- `read` - Read memory files
- `write` - Write/update memory files
- `memory_search` - Semantic search through memory
- `memory_get` - Get specific memory snippets

## When to Use
When you need to:
- Remember important information across sessions
- Search past conversations or notes
- Update long-term memory (MEMORY.md)
- Create daily notes
- Track conversations for continuity

## Memory System

### Long-Term Memory
**File:** `MEMORY.md` (workspace root)
- Curated, important information
- Updated after significant conversations
- Contains project details, preferences, credentials

### Daily Notes
**File:** `memory/YYYY-MM-DD.md`
- Raw logs of daily activities
- Created automatically for each day
- Contains session notes, tasks, discoveries

### Conversation Continuity
**File:** `conversation_continuity.md`
- Stores summary of last conversation
- Read at session start
- Updated after significant talks

### Skill-Specific Memory
**Files:** `memory/*.md`
- Various skill guides and checklists
- Reference materials
- User preferences

## How to Use

### Read Memory
```python
# Read main memory
read("MEMORY.md")

# Read today's notes
read("memory/2026-02-23.md")

# Search memory
memory_search(query="project details")
```

### Write Memory
```python
# Update memory
write(content="# New Memory Entry\nContent here", path="MEMORY.md")

# Add daily note
write(content="## Session Notes\n- Did something", path="memory/2026-02-23.md")
```

## Key Memory Files

| File | Purpose |
|------|---------|
| `MEMORY.md` | Long-term curated memory |
| `USER.md` | User preferences and info |
| `SOUL.md` | AI persona and voice |
| `TOOLS.md` | Local tool configurations |
| `conversation_continuity.md` | Session continuity |
| `memory/YYYY-MM-DD.md` | Daily notes |

## Best Practices

1. **After significant conversations:** Update `conversation_continuity.md`
2. **Weekly:** Review daily notes and update `MEMORY.md` with important learnings
3. **Before major tasks:** Read relevant memory files
4. **When instructed:** Add new info to appropriate memory file
5. **Commit changes:** Push memory updates to GitHub

## Token Management

Monitor token usage:
- Check `session_status` for current usage
- Clear memory if tokens > 70%
- Start fresh session if needed

## Adding New Memory Types

Create new memory files as needed:
- `memory/projects.md` - Project-specific notes
- `memory/skills.md` - Skill references
- `memory/todos.md` - Task tracking
