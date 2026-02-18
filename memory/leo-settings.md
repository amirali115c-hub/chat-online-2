# Leo's Settings (Per Boss's Request)

## Model Parameters (Per-Request)
When Boss says "use creative mode" or specifies settings, apply:
- **Temperature:** 0.9
- **Top-K:** 90
- **Top-P:** 0.9

## Copywriting & Blog Writing
**IMPORTANT:** For ALL copywriting, blog posts, or content writing tasks:
- Always use creative mode (temp 0.9, top-k 90, top-p 0.9)
- Follow the copywriting framework in memory/copywriting-skills.md
- Follow the master framework in memory/fortune-500-copywriting-mastery.md

## How It Works
- These are inference-time parameters OpenClaw would pass to Ollama
- Currently not persistently configurable via OpenClaw config
- I'll remember and apply these per request when asked

## Commands Boss Can Use
- "use creative mode" → applies temp 0.9, top-k 90, top-p 0.9
- "use normal mode" → uses default Ollama settings

## Last Updated
2026-02-14
