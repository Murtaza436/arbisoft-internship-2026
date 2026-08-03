# Week 4 — Agentic AI with Tools, Memory and Hooks

## What This Week Covers
Building a research agent that can search the web, read files, remember facts
from earlier in the session, and log every tool call with a timestamp.
<<<<<<< HEAD
This is the first full agentic AI system — the LLM decides what tools to use
and in what order rather than just answering directly.
=======
The LLM decides what tools to use and in what order.
>>>>>>> main

## Folder Structure
week4/
+-- src/
<<<<<<< HEAD
¦ +-- agent.py # main agent logic and tool calling loop
¦ +-- tools.py # web_search and read_file tool functions
¦ +-- memory.py # session memory — stores facts and conversation history
¦ +-- hooks.py # pre and post tool hooks with timestamp logging
¦ +-- runner.py # CLI interface to run the agent interactively
¦ +-- constants.py # color constants for terminal output
+-- tests/
¦ +-- test_tools.py # tests for file reading tool
+-- files/ # put .txt and .pdf files here for the agent to read
+-- logs/ # tool call logs saved here automatically
+-- week4_analysis.ipynb # main notebook with agent demo and trace logs
## How to Run

### 1. Setup
`ash
cd week4
uv sync
uv add openai python-dotenv requests pypdf jupyter notebook pandas
`
=======
¦   +-- agent.py      - main agent logic and tool calling loop
¦   +-- tools.py      - web_search and read_file tool functions
¦   +-- memory.py     - session memory, stores facts and conversation history
¦   +-- hooks.py      - pre and post tool hooks with timestamp logging
¦   +-- runner.py     - CLI interface to run the agent interactively
¦   +-- constants.py  - color constants for terminal output
+-- tests/
¦   +-- test_tools.py - tests for file reading tool
+-- files/            - put .txt and .pdf files here for the agent to read
+-- logs/             - tool call logs saved here automatically
+-- week4_analysis.ipynb - main notebook with agent demo and trace logs

## How to Run

### 1. Setup
cd week4
uv sync
uv add openai python-dotenv requests pypdf jupyter notebook pandas
>>>>>>> main

### 2. Add API Keys
Create a .env file in the week4 folder:
OPENROUTER_API_KEY=your-key-here
BRAVE_API_KEY=your-brave-key-here
<<<<<<< HEAD
Get Brave API key free at brave.com/search/api — 2000 queries per month free.

### 3. Run the Notebook
`ash
uv run jupyter notebook
`
Open week4_analysis.ipynb and run all cells in order from top to bottom.

### 4. Run the CLI Agent (optional)
`ash
uv run python -m src.runner
`
This opens an interactive chat where you can talk to the agent directly.
Type exit to quit, clear to reset memory, memory to see stored facts.

## Cell Order in Notebook
| Cell | What it does |
|------|-------------|
| Cell 1 | Imports and setup |
| Cell 2 | Initialize session memory |
| Cell 3 | Web search tool demo — tests Brave Search directly |
| Cell 4 | File read tool demo — reads chelsea.txt |
| Cell 5 | Multi-hop agent demo — agent uses multiple tools in sequence |
| Cell 6 | Memory contents — shows facts stored during conversation |
| Cell 7 | Hook trace logs — shows every tool call with timestamp |
| Cell 8 | Findings and notes |

## Run Tests
`ash
uv run pytest tests/ -v
`

## How the Agent Works
User sends message
?
Agent receives message + memory facts in system prompt
?
LLM decides which tool to call (web_search or read_file)
?
Pre-hook logs the tool call with timestamp
?
Tool executes and returns result
?
Post-hook logs the result preview
?
Result sent back to LLM
?
LLM decides if more tools needed or gives final answer
=======
Get Brave API key free at brave.com/search/api, 2000 queries per month free.

### 3. Run the Notebook
uv run jupyter notebook
Open week4_analysis.ipynb and run all cells in order from top to bottom.

### 4. Run the CLI Agent
uv run python -m src.runner
Type exit to quit, clear to reset memory, memory to see stored facts.

## Cell Order in Notebook
Cell 1 - Imports and setup
Cell 2 - Initialize session memory
Cell 3 - Web search tool demo
Cell 4 - File read tool demo
Cell 5 - Multi-hop agent demo
Cell 6 - Memory contents
Cell 7 - Hook trace logs
Cell 8 - Findings and notes

## Run Tests
uv run pytest tests/ -v

## How the Agent Works
User sends message
        ?
Agent receives message plus memory facts in system prompt
        ?
LLM decides which tool to call
        ?
Pre-hook logs the tool call with timestamp
        ?
Tool executes and returns result
        ?
Post-hook logs the result preview
        ?
Result sent back to LLM
        ?
LLM decides if more tools needed or gives final answer

>>>>>>> main
## Key Concepts Demonstrated
- Function calling: LLM returns structured tool call requests
- ReAct pattern: Reason and Act loop until final answer
- In-context memory: conversation history and facts in system prompt
<<<<<<< HEAD
- Hooks: pre and post interceptors for logging without changing tool logic
- Multi-hop reasoning: chaining multiple tool calls to answer complex questions

## Models Used
- LLM: nvidia/nemotron-3-ultra-550b-a55b:free via OpenRouter
- Fallback: tinyllama via Ollama (local, free, no internet needed)

## Log Files
Every tool call is logged automatically to logs/tool_calls.log.
Each log entry contains timestamp, tool name, arguments, and result preview.
=======
- Hooks: pre and post interceptors for logging
- Multi-hop reasoning: chaining multiple tool calls

## Models Used
- LLM: nvidia/nemotron-3-ultra-550b-a55b:free via OpenRouter
- Fallback: tinyllama via Ollama, local and free
>>>>>>> main
