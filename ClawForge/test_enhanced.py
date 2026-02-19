import requests
base = 'http://127.0.0.1:9000'

print('=== TESTING ENHANCED CHAT ===')
r = requests.post(f'{base}/api/chat', json={'message': 'Hello, my name is Amir!'})
data = r.json()
print(f'Status: {data.get("status")}')
print(f'Memory Enhanced: {data.get("memory_enhanced")}')
response_text = data.get('response', '')
if response_text:
    print(f'Response: {response_text[:100]}...')
else:
    print(f'Error: {data.get("error", "Unknown error")}')
