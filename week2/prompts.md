# prompts.md — AI Interaction Log

## Week 2: Deep Learning and LLM Fundamentals

### 2026-06-28
**Prompt:** "Can you provide a summary of the Week 2 tasks and a roadmap for what I need to accomplish?"
**Model:** Claude (claude.ai)
**Result:** Received a high-level overview of the Week 2 assignments, including a step-by-step roadmap for setting up the project, understanding LLM fundamentals, building the chat interface, and comparing models.

### 2026-06-28
**Prompt:** "Give me the complete week 2 setup from branch creation to code to jupyter notebook."
**Model:** Claude (claude.ai)
**Result:** Received full project structure, src/model_compare.py and src/chat.py helper scripts, and complete jupyter notebook cells for model comparison, results table, and multi-turn chat demo.

### 2026-07-01
**Prompt:** "What are the best free models available on OpenRouter that have decent rate limits?"
**Model:** Claude (claude.ai)
**Result:** Received recommendations for top free-tier models on OpenRouter, such as Llama 3 8B Instruct and Gemini 1.5 Flash, along with details on balancing performance with context windows and token generation limits.

### 2026-07-01
**Prompt:** "I got a 'failed to push some refs' error when trying to push my new week-2-pr branch after running git init."
**Model:** Gemini
**Result:** Learned that running git init in a new folder creates a completely isolated repository, causing GitHub to reject the push due to unrelated histories with the Week 1 main branch.

### 2026-07-01
**Prompt:** "I already committed my Week 2 files in the new folder. How do I fix the history error and push to GitHub?"
**Model:** Gemini
**Result:** Used git fetch origin and git merge origin/main --allow-unrelated-histories -X theirs to stitch the new local files together with the official GitHub history, allowing a successful push to the PR branch.
