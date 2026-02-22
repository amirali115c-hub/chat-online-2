# HEARTBEAT.md

## Token Check (Run every heartbeat)

1. Check session token usage with `session_status`
2. If tokens > 140k (70% of 200k):
   - Log: "Memory at 70% - recommend clearing"
   - Set flag to notify user on next message
3. If flag set, inform user: "Session at 70% - want me to clear memory and start fresh?"

## Before New Session
- Check conversation_continuity.md for last session info
- Ask user if they want to continue or start fresh
