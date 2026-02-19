import requests

print("Testing Ollama chat with qwen2.5:3b...")
r = requests.post('http://127.0.0.1:8888/api/chat/ollama', json={
    'message': 'Hello! What can you do?'
})
data = r.json()
print(f"Status: {data.get('status')}")
print(f"Provider: {data.get('provider')}")
print(f"Model: {data.get('model')}")
if data.get('status') == 'success':
    print(f"Response: {data.get('response', '')[:300]}...")
else:
    print(f"Error: {data.get('error')}")
    print(f"Message: {data.get('message')}")
