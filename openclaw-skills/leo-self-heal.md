# Leo Self-Heal

## Description
Self-diagnosis and recovery capabilities for troubleshooting Leo AI when issues occur. Includes status checks, log analysis, and recovery procedures.

## Tools Used
- `exec` - Run shell commands
- `read` - Read log files
- `session_status` - Check session health

## When to Use
When:
- Leo is not responding
- Gateway errors occur
- Model is not loading
- Token limit exceeded
- Connection issues arise
- General troubleshooting needed

## Diagnostic Commands

### 1. Check Gateway Status
```bash
openclaw status
openclaw gateway status
```
Shows if gateway is running and healthy.

### 2. Restart Gateway
```bash
openclaw gateway restart
```
Restarts the OpenClaw gateway service.

### 3. Check Logs
```bash
Get-Content "$env:APPDATA\openclaw\logs\*.log" -Tail 50
```
View recent log entries for errors.

### 4. Run Diagnostics
```bash
openclaw doctor --fix
```
Auto-detect and fix common issues.

### 5. Check Models
```bash
openclaw models list
```
List available Ollama models.

### 6. Check Ports
```bash
netstat -ano | findstr :11434
```
Check if Ollama port is in use.

## Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Token limit exceeded** | "Context limit exceeded" | Restart session, clear memory |
| **Gateway 401** | Unauthorized errors | `openclaw gateway restart` |
| **Route 404** | Not found errors | `openclaw status` |
| **Gateway closed** | Connection refused | `openclaw gateway start` |
| **Model not responding** | Ollama timeout | Check Ollama running, try different model |
| **Port conflict** | Address already in use | Kill process using port |

## Recovery Procedures

### If Leo Won't Start
1. Check status: `openclaw status`
2. Restart gateway: `openclaw gateway restart`
3. Check logs: `openclaw logs --follow`
4. Run doctor: `openclaw doctor --fix`

### If Model Fails
1. Check Ollama: `ollama list`
2. Pull model: `ollama pull <model-name>`
3. Try different model
4. Restart Ollama service

### If Memory Full
1. Check token usage: `session_status`
2. If >70%, restart session
3. Clear conversation history
4. Start fresh

### If Webchat Fails
1. Try: `openclaw webchat`
2. Check browser console for errors
3. Try different channel

## Manual Recovery

### Check OpenClaw Service
```powershell
Get-Service openclaw
```

### Start Manually
```powershell
cd "C:\Users\HP\AppData\Roaming\npm\node_modules\openclaw"
npm start
```

### Reset Everything
```powershell
openclaw gateway stop
openclaw gateway start
```

## Self-Heal API (If Implemented)

If the Chat Online app has self-heal endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/selfheal/status` | GET | Check system status |
| `/api/selfheal/logs` | GET | Get recent logs |
| `/api/selfheal/diagnostics` | GET | Full diagnostics |
| `/api/selfheal/restart` | POST | Restart services |
| `/api/selfheal/autoheal` | POST | Auto-fix issues |

## Prevention

- Monitor token usage regularly
- Commit changes frequently
- Keep logs accessible
- Check session status periodically

## Emergency Contacts

If completely stuck:
1. Kill terminal sessions
2. Run: `openclaw gateway restart`
3. Start fresh: `openclaw webchat`
4. Check GitHub for updates
