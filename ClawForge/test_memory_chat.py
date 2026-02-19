import requests
base = 'http://127.0.0.1:3333'

print('=== TESTING MEMORY & CHAT ===\n')

# 1. Add some messages to history
print('1. Adding conversation to history...')
convo = [
    {'role': 'user', 'content': 'Hi, my name is Amir and I am a Python developer from Pakistan'},
    {'role': 'assistant', 'content': 'Nice to meet you Amir! Python is a great language for development.'},
    {'role': 'user', 'content': 'I am also working on an AI project called ClawForge'},
    {'role': 'assistant', 'content': 'That sounds amazing! ClawForge is a great name for an AI project.'},
]

for msg in convo:
    r = requests.post(f'{base}/api/longterm-memory/history/message', json=msg)
    print(f"   {msg['role']}: {msg['content'][:40]}...")

# 2. Check history stats
print('\n2. History stats:')
r = requests.get(f'{base}/api/longterm-memory/history/stats')
data = r.json()
print(f"   Sessions: {data['total_sessions']}")
print(f"   Messages: {data['total_messages']}")

# 3. Test enhanced chat
print('\n3. Testing enhanced chat with memory:')
r = requests.post(f'{base}/api/chat', json={'message': 'What do you know about me?'})
data = r.json()
print(f"   Status: {data.get('status')}")
print(f"   Memory Enhanced: {data.get('memory_enhanced')}")
print(f"   Response: {data.get('response', '')[:200]}...")

print('\n=== TEST COMPLETE ===')
