# prompts.md — AI Interaction Log

## Week 4: Agentic AI - Skills, Hooks, Memory and Plugins

### 2026-07-01
**Prompt:** "Give me the complete week 4 setup from start to finish including research agent, web search, file read, memory, and hooks."
**Model:** Claude (claude.ai)
**Result:** Received full project structure with tools.py for web search and file reading, memory.py for session memory, hooks.py for tool call logging, agent.py for main agent logic, and complete jupyter notebook demo.

### 2026-07-01
**Prompt:** "What is the difference between an agent and a regular LLM call?"
**Model:** Claude (claude.ai)
**Result:** A regular LLM call takes input and returns output in one step. An agent has a loop where the LLM decides what tools to use, executes them, observes results, and decides if more steps are needed before giving a final answer. The LLM acts as a planner not just a responder.

### 2026-07-01
**Prompt:** "What is a hook in an agent pipeline?"
**Model:** Claude (claude.ai)
**Result:** A hook is a function that runs before or after a specific event. Pre-tool hooks run before a tool executes and can log, validate, or modify the call. Post-tool hooks run after and can log results or trigger side effects. They are useful for observability and debugging without changing the core tool logic.

### 2026-07-01
**Prompt:** "How does function calling work with the OpenAI API?"
**Model:** Claude (claude.ai)
**Result:** You define tools as JSON schemas describing the function name, description, and parameters. You pass these to the API with tool_choice auto. The model decides whether to call a tool and returns a tool_calls object with the function name and arguments as JSON. You execute the function locally and send the result back as a tool message. The model then continues reasoning with that result.
