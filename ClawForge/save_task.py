import requests
base = 'http://127.0.0.1:9000'

print('=== SAVING TASK TO MEMORY ===')

# Save task completion to memory
r = requests.post(f'{base}/api/longterm-memory/history/message', json={
    'role': 'user',
    'content': 'Task completed: Full memory and web browsing integration for ClawForge. Duration: ~25 minutes. Features: Memory-aware chat, enhanced system prompt, web browsing, session history, automatic memory loading.'
})
print(r.json())

# Save to memory stats
r = requests.post(f'{base}/api/longterm-memory/facts', json={
    'fact': 'ClawForge now has long-term memory and web browsing capabilities integrated.'
})
print('\n=== SAVING FACT ===')
print(r.json())

print('\n✅ Task completion saved to ClawForge memory!')
