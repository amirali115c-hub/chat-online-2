# CONTEXT MANAGEMENT SYSTEM

## Smart Context Handler

This system manages conversation context to prevent overflow while keeping relevant information.

### How It Works

1. **Message Classification** - Each message is tagged as:
   - `relevant` - Directly related to current task/project
   - `neutral` - General chat, greetings
   - `irrelevant` - Off-topic, personal, unrelated

2. **Context Window** - Keep last 20 messages, but prioritize:
   - Last 5 messages (recent)
   - User's current task/goals
   - Important decisions
   - Code snippets or technical details

3. **Auto-Cleanup** - Remove:
   - Very old messages (>50 total)
   - Neutral messages when context gets full
   - Duplicate information

### Implementation

```python
class ContextManager:
    def __init__(self, max_messages=50):
        self.max_messages = max_messages
        self.current_task = None
        self.relevant_topics = []
        
    def classify_message(self, message: str) -> str:
        """Classify if message is relevant to current task"""
        # Keywords for relevance
        task_keywords = ['code', 'build', 'project', 'fix', 'error', 
                        'write', 'create', 'deploy', 'git', 'api', 
                        'website', 'search', 'research', 'blog']
        
        message_lower = message.lower()
        for keyword in task_keywords:
            if keyword in message_lower:
                return 'relevant'
        return 'neutral'
    
    def should_search_web(self, message: str) -> bool:
        """Decide if we should proactively search the web"""
        search_triggers = [
            'what is', 'how to', 'what are', 'find information',
            'research', 'latest', 'news', 'best', 'compare',
            'about', 'explain', 'documentation', 'guide',
            ' tutorial', 'example', 'website', 'project'
        ]
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in search_triggers)
    
    def cleanup_context(self, messages: list) -> list:
        """Clean up context, keeping most relevant"""
        if len(messages) <= self.max_messages:
            return messages
            
        # Separate by relevance
        relevant = [m for m in messages if m.get('relevant')]
        neutral = [m for m in messages if not m.get('relevant')]
        
        # Keep recent + relevant
        kept = messages[-10:]  # Last 10
        kept.extend(relevant[-10:])  # Last 10 relevant
        
        # Dedupe and return
        seen = set()
        result = []
        for m in kept:
            key = m.get('content', '')[:50]
            if key not in seen:
                seen.add(key)
                result.append(m)
        
        return result[-self.max_messages:]
```

### Usage in NeoLeo

```python
# Before processing any message
context = ContextManager(max_messages=50)

# Check if should search web proactively
if context.should_search_web(user_message):
    # Auto-search for relevant information
    results = web_search(query)
    context.add_search_results(results)

# After processing, cleanup if needed
messages = context.cleanup_context(messages)
```

### Keywords That Trigger Web Search

| Category | Triggers |
|----------|----------|
| **Research** | what is, how to, what are, explain |
| **Information** | find, research, latest, news |
| **Comparisons** | best, compare, vs, difference |
| **Learning** | tutorial, guide, documentation, example |
| **Projects** | about, website, project, framework |

### Context Priority

1. 🔴 **HIGH** - Code, errors, technical solutions
2. 🟡 **MEDIUM** - Project decisions, files modified
3. 🟢 **LOW** - Greetings, small talk

---

**This system is already integrated into NeoLeo!**
When you ask about any project/website, I automatically search the web for better information.
