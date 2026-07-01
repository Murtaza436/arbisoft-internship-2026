# prompts.md — AI Interaction Log

## Week 2: Deep Learning and LLM Fundamentals

### 2026-06-28
**Prompt:** "Give me the complete week 2 setup from branch creation to code to jupyter notebook."
**Model:** Claude (claude.ai)
**Result:** Received full project structure, src/model_compare.py and src/chat.py helper scripts, and complete jupyter notebook cells for model comparison, results table, and multi-turn chat demo.

### 2026-06-28
**Prompt:** "How does multi-turn conversation work in LLMs if they are stateless?"
**Model:** Claude (claude.ai)
**Result:** Learned that conversation history is maintained as a list of message dictionaries on the client side and the full list is sent on every API call. Implemented this in src/chat.py in the chat_turn function.

### 2026-06-28
**Prompt:** "What is the difference between temperature 0 and temperature 1 in LLMs?"
**Model:** Claude (claude.ai)
**Result:** Temperature 0 is deterministic and always picks the most likely next token. Temperature 1 is more random and creative. Used lower temperature for factual tasks in the chat demo.

### 2026-07-01
**Prompt:** "I got a 'failed to push some refs' error when trying to push my new week-2-pr branch after running git init."
**Model:** Gemini
**Result:** Learned that running git init in a new folder creates a completely isolated repository, causing GitHub to reject the push due to unrelated histories with the Week 1 main branch.

### 2026-07-01
**Prompt:** "I already committed my Week 2 files in the new folder. How do I fix the history error and push to GitHub?"
**Model:** Gemini
**Result:** Used git fetch origin and git merge origin/main --allow-unrelated-histories -X theirs to stitch the new local files together with the official GitHub history, allowing a successful push to the PR branch.
