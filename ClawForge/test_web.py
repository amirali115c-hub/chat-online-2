import requests
base = 'http://127.0.0.1:8888'

print('=== WEB SEARCH TEST ===')
r = requests.post(f'{base}/api/web/search', json={'query': 'latest Python news', 'num_results': 3})
data = r.json()
print(f'Status: {data.get("status")}')
if data.get('results'):
    for i, result in enumerate(data['results'][:3], 1):
        print(f"\n{i}. {result.get('title', 'N/A')}")
        print(f"   URL: {result.get('url', 'N/A')}")
else:
    print(f"Error: {data}")

print('\n=== WEB FETCH TEST ===')
r = requests.post(f'{base}/api/web/fetch', json={'url': 'https://python.org', 'extract_mode': 'markdown'})
data = r.json()
print(f'Status: {data.get("status")}')
if data.get('content'):
    print(f"Content length: {len(data['content'])} chars")
    print(f"First 200 chars: {data['content'][:200]}...")
