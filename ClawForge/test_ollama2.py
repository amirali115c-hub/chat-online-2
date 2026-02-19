import requests
import json

print("Testing Ollama chat with qwen2.5:3b...")
r = requests.post('http://127.0.0.1:8888/api/chat/ollama', json={
    'message': 'Hello! What can you do?'
}, timeout=60)
data = r.json()
print(json.dumps(data, indent=2))
