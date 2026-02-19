import requests

# Check available memory
r = requests.get('http://127.0.0.1:8888/api/ollama/models')
data = r.json()
print('Available models:')
for m in data.get('models', []):
    size_gb = m['size'] / (1024**3)
    print(f"  - {m['name']}: {size_gb:.1f} GB")

print('\nTry these smaller models:')
print("  ollama pull qwen3:1.5b   # Requires ~4GB RAM")
print("  ollama pull llama3.2:3b # Requires ~4GB RAM")
print("  ollama pull phi3:3.8b   # Requires ~5GB RAM")
