import requests
base = 'http://127.0.0.1:7777'

print('=== TESTING COMBINED SEARCH ===\n')

# Test combined search
r = requests.post(f'{base}/api/web/search', json={'query': 'Python 3.13 release date', 'num_results': 5})
data = r.json()
print(f'Status: {data.get("status")}')
print(f'Sources: {data.get("sources", [])}')
print(f'Total Results: {data.get("count")}')

print('\n=== TOP RESULTS ===')
for i, result in enumerate(data.get('results', [])[:3], 1):
    title = result.get('title', 'N/A')[:60]
    print(f"{i}. {title}")
    print(f"   Source: {result.get('source', 'N/A')}")
    url = result.get('url', 'N/A')[:60]
    print(f"   URL: {url}")

print('\n=== PROVIDERS INFO ===')
r = requests.get(f'{base}/api/web/providers')
info = r.json()
print(f"Strategy: {info.get('strategy')}")
print(f"Deduplication: {info.get('deduplication')}")
