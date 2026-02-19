import requests
base = 'http://127.0.0.1:9000'

print('=== ADDING TO HISTORY ===')
r = requests.post(f'{base}/api/longterm-memory/history/message', json={
    'role': 'user',
    'content': 'My name is Amir and I am a Python developer from Pakistan'
})
print(r.json())

print('\n=== CHECKING HISTORY ===')
r = requests.get(f'{base}/api/longterm-memory/history/stats')
print(r.json())

print('\n=== RECENT MESSAGES ===')
r = requests.get(f'{base}/api/longterm-memory/history/recent')
data = r.json()
print(f"Count: {data.get('count')}")
for msg in data.get('messages', []):
    role = msg['role']
    content = msg['content'][:50]
    print(f"{role}: {content}...")
