import requests
base = 'http://127.0.0.1:6666'

print('=== TESTING ENHANCED MEMORY ===\n')

# Test 1: Check history
print('1. Checking chat history...')
r = requests.get(f'{base}/api/longterm-memory/history/recent')
data = r.json()
print(f"   Messages: {data.get('count')}")
for msg in data.get('messages', []):
    print(f"   {msg['role']}: {msg['content'][:60]}...")

# Test 2: Enhanced chat with memory
print('\n2. Testing enhanced chat...')
r = requests.post(f'{base}/api/chat', json={'message': 'What do you know about me?'})
data = r.json()
print(f"   Status: {data.get('status')}")
print(f"   Memory Enhanced: {data.get('memory_enhanced')}")
response = data.get('response', '')
if 'Amir' in response or 'Python' in response:
    print(f"   ✅ REMEMBERING! Response contains known info")
else:
    print(f"   Response: {response[:200]}...")

print('\n=== TEST COMPLETE ===')
