# Leo Workflow

## Description
Build complex automation workflows by chaining multiple tools together. Create multi-step processes that combine search, fetch, process, and output.

## Tools Used
- `web_search` - Search the web
- `web_fetch` - Fetch web page content
- `exec` - Run commands and scripts
- `read` - Read files and data
- `write` - Write output files
- `sessions_spawn` - Create sub-agents for parallel tasks

## When to Use
When you need to:
- Research a topic end-to-end (search → fetch → summarize → write)
- Create automated pipelines
- Process multiple data sources
- Run parallel tasks
- Build multi-step workflows

## Workflow Patterns

### Pattern 1: Research Pipeline
```
1. web_search (find relevant sources)
2. web_fetch (extract content from top results)
3. exec (process with Python/script)
4. write (save research to file)
```

### Pattern 2: Data Processing
```
1. read (load input data)
2. exec (process with Python)
3. write (save output)
4. exec (commit to git)
```

### Pattern 3: Parallel Processing
```
1. sessions_spawn (create multiple sub-agents)
2. Each agent does a sub-task
3. Aggregate results
4. write (final output)
```

### Pattern 4: N8N Integration
```
1. exec (trigger N8N webhook)
2. web_fetch (get workflow result)
3. process result
4. write (save or send)
```

## Examples

### Example 1: Blog Post Research
```python
# Step 1: Search for topics
results = web_search(query="best SEO practices 2024", count=5)

# Step 2: Fetch top articles
for result in results:
    content = web_fetch(url=result['url'])

# Step 3: Process and write
write(content=summary, path="research.md")
```

### Example 2: Automated Backup
```python
# Step 1: Read key files
data = read("important.json")

# Step 2: Run backup script
exec(command='python backup.py')

# Step 3: Commit
exec(command='git add -A && git commit -m "backup"')
```

### Example 3: Multi-Source Aggregation
```python
# Spawn parallel fetches
sessions_spawn(task="Fetch weather for Lahore", label="weather-lhr")
sessions_spawn(task="Fetch weather for Dubai", label="weather-dub")

# Aggregate when done
# (results sent back to main session)
```

## Building Custom Workflows

1. **Define the goal** - What should the workflow achieve?
2. **Break into steps** - Divide into tool calls
3. **Determine order** - Sequential vs parallel
4. **Handle errors** - Add fallback logic
5. **Output format** - How should results be saved?

## Best Practices

- **Small steps:** Break complex workflows into manageable chunks
- **Error handling:** Check each step's output
- **Logging:** Write progress to memory files
- **Commits:** Commit after completing major workflow milestones
- **Testing:** Test each step individually before chaining

## N8N Webhook Example

To trigger N8N workflows:
```python
import requests

webhook_url = "http://localhost:5678/webhook/your-trigger"
payload = {"data": "your_data"}

response = requests.post(webhook_url, json=payload)
result = response.json()
```

## External APIs

Build and call custom APIs:
```python
# Create API (external service)
# Flask app on port 5001

# Call from workflow
result = web_fetch(url="http://localhost:5001/api/your-endpoint")
```
