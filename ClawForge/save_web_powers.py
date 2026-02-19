import requests
base = 'http://127.0.0.1:8888'

print('=== SAVING TASK TO MEMORY ===')

# Save completion task
r = requests.post(f'{base}/api/longterm-memory/history/message', json={
    'role': 'user',
    'content': 'Task completed: Made ClawForge fully aware of its web browsing powers. Updated system prompt to emphasize combined web search (Brave API + DuckDuckGo) and proactive use of web search for current events.'
})
print(r.json())

# Save as fact
r = requests.post(f'{base}/api/longterm-memory/facts', json={
    'fact': 'ClawForge has COMBINED WEB BROWSING: Brave API (high quality) + DuckDuckGo (free, always works). Should use web search proactively for current events and factual checks.'
})
print('\n=== SAVING FACT ===')
print(r.json())

print('\n✅ Task saved to memory!')
