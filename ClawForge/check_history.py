import requests
base = 'http://127.0.0.1:3333'

print('=== CHECKING RECENT HISTORY ===')
r = requests.get(f'{base}/api/longterm-memory/history/recent')
data = r.json()
print(f"Count: {data.get('count')}")
for msg in data.get('messages', []):
    print(f"{msg['role']}: {msg['content'][:60]}")

print('\n=== CHECKING ALL HISTORY ===')
r = requests.get(f'{base}/api/longterm-memory/history/all')
data = r.json()
print(f"Total sessions: {len(data.get('sessions', []))}")
for session in data.get('sessions', [])[-3:]:
    print(f"Session {session['id']}: {session['message_count']} messages")
