# Leo Self-Heal Commands

## Quick Diagnostics

### Check Status
```powershell
openclaw status
```

### Check Errors in Logs
```powershell
Get-Content "$env:APPDATA\openclaw\logs\*.log" -Tail 50 | Select-String -Pattern "error|Error|ERROR|401|404|500"
```

### Check Gateway
```powershell
openclaw gateway status
openclaw gateway restart
```

### Fix Config Issues
```powershell
openclaw doctor --fix
```

### Check Models
```powershell
openclaw models list
```

## Common Fixes

| Error | Fix |
|-------|-----|
| "Context limit exceeded" | Memory too full - I should auto-clear at 70% |
| "401 Unauthorized" | Gateway needs restart - run `openclaw gateway restart` |
| "404 Not Found" | Route issue - check `openclaw status` |
| "Gateway closed" | Run `openclaw gateway start` |

## My Capabilities

✅ Can check my own status
✅ Can read logs
✅ Can restart gateway
✅ Can clear memory
✅ Can notify you of issues

⚠️ Can only do these when I'm ACTIVE (in a session)
⚠️ Can't wake myself up when crashed

## What To Do When I'm Not Working

1. **Check if gateway is running:**
   ```
   openclaw status
   ```

2. **Restart gateway:**
   ```
   openclaw gateway restart
   ```

3. **Check logs:**
   ```
   openclaw logs --follow
   ```

4. **Fix common issues:**
   ```
   openclaw doctor --fix
   ```

5. **Start me fresh:**
   ```
   openclaw webchat
   ```
