# prompts.md - AI Interaction Log

## Week 1: AI/ML Foundations

### 2026-06-23
**Prompt:** "Explain the full week 1 and week 2 assignments from my Arbisoft internship roadmap in detail."
**Model:** Claude (claude.ai)
**Result:** Received complete breakdown of project structure and function-by-function explanation. Used as conceptual foundation before writing any code.

### 2026-06-23
**Prompt:** "pytest is giving ModuleNotFoundError: No module named src."
**Model:** Claude (claude.ai)
**Result:** Fixed by creating empty __init__.py files and adding pythonpath to pyproject.toml.

### 2026-06-23
**Prompt:** "ruff check returning 6 errors: W292 and F401."
**Model:** Claude (claude.ai)
**Result:** All fixed with --fix flag. W292 means no newline at end of file. F401 means unused import.

## Week 2: Deep Learning and LLM Fundamentals

### 2026-06-25
**Prompt:** "Give me complete week 2 setup including model comparison and chat app."
**Model:** Claude (claude.ai)
**Result:** Received full project structure, src/model_compare.py and src/chat.py with multi-turn conversation history.

### 2026-06-25
**Prompt:** "How does multi-turn conversation work if LLMs are stateless?"
**Model:** Claude (claude.ai)
**Result:** Learned that conversation history is maintained as a list client-side and full list sent on every API call. Implemented in chat_turn function.

### 2026-06-25
**Prompt:** "Why create a separate constants.py for colors?"
**Model:** Claude (claude.ai)
**Result:** Single source of truth principle. Define once, import everywhere. If color changes, update one file only.

## Week 3: RAG, Vector DBs and Structured Outputs

### 2026-06-28
**Prompt:** "Give me complete week 3 setup including RAG pipeline, structured outputs and validation tests."
**Model:** Claude (claude.ai)
**Result:** Received full structure with ingest.py for PDF chunking, retriever.py for ChromaDB search, rag_pipeline.py combining retrieval and generation, structured.py with Pydantic validation.

### 2026-06-28
**Prompt:** "ChromaDB is timing out trying to download embedding model."
**Model:** Claude (claude.ai)
**Result:** Switched to SentenceTransformerEmbeddingFunction with all-MiniLM-L6-v2 which runs locally without downloading at runtime.

### 2026-06-28
**Prompt:** "How does Pydantic catch LLM output errors?"
**Model:** Claude (claude.ai)
**Result:** Pydantic defines schema as Python class. When LLM output parsed as JSON and passed to class, Pydantic checks every field type and raises ValidationError if wrong.

### 2026-06-28
**Prompt:** "How do I detect hallucinations in a RAG system?"
**Model:** Claude (claude.ai)
**Result:** Ask about topics not in documents and check if model says I do not know. Added explicit instruction in prompt to say I do not know if answer not in context.

## Week 4: Agentic AI - Tools, Memory and Hooks

### 2026-07-01
**Prompt:** "Give me complete week 4 setup including research agent, web search, memory and hooks."
**Model:** Claude (claude.ai)
**Result:** Received full structure with tools.py, memory.py, hooks.py, agent.py and complete jupyter notebook demo.

### 2026-07-01
**Prompt:** "What is the difference between an agent and a regular LLM call?"
**Model:** Claude (claude.ai)
**Result:** Regular LLM call is one step. Agent has a loop where LLM decides tools, executes them, observes results, decides if more steps needed. LLM acts as planner.

### 2026-07-01
**Prompt:** "Free OpenRouter models keep returning 404 when using tools parameter."
**Model:** Claude (claude.ai)
**Result:** Learned that function calling is a premium feature not supported on free tier models. Switched to nvidia/nemotron-3-ultra-550b-a55b:free which supports it.

## Week 5: MCP and Multi-Agent Orchestration

### 2026-07-05
**Prompt:** "Give me complete week 5 setup including MCP server, supervisor worker agents, and tracing."
**Model:** Claude (claude.ai)
**Result:** Received full project structure with MCP server exposing resource and tool, supervisor agent routing tasks to search and summary workers, and tracing layer logging all events.

### 2026-07-05
**Prompt:** "What is MCP and how is it different from regular function calling?"
**Model:** Claude (claude.ai)
**Result:** MCP is a standard protocol like USB for AI tools. Regular function calling is custom per application. MCP gives one standard interface any AI can use to connect to any tool or data source.

### 2026-07-05
**Prompt:** "What is the supervisor worker pattern in multi-agent systems?"
**Model:** Claude (claude.ai)
**Result:** Supervisor receives user request, decides which specialized worker to use, routes the task, collects result. Workers are specialized agents that each do one thing well. Separates routing logic from execution logic.
