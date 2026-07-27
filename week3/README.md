# Arbisoft AI/ML Internship 2026

This repository contains all weekly assignments for the Arbisoft AI-focused internship program 2026.

## Repository Structure
arbisoft-internship-2026/
+-- week1/   ML foundations - Iris classifier, Random Forest, hyperparameter tuning
+-- week2/   LLM fundamentals - model comparison, CLI chat app, colored output
+-- week3/   RAG pipeline - ChromaDB, embeddings, structured outputs, Pydantic
+-- week4/   Agentic AI - research agent, web search, memory, hooks
## How to Navigate

### Week 1 - AI/ML Foundations
- Go to week1/ folder
- Main results and outputs: week1/week1_analysis.ipynb
- Helper functions: week1/src/data_prep.py, week1/src/train.py, week1/src/evaluate.py
- Run: cd week1 && uv sync && uv run jupyter notebook
- Open week1_analysis.ipynb and run all cells

### Week 2 - Deep Learning and LLM Fundamentals
- Go to week2/ folder
- Main results and outputs: week2/week2_analysis.ipynb
- Helper functions: week2/src/chat.py, week2/src/model_compare.py, week2/src/constants.py
- Add your OpenRouter API key to week2/.env
- Run: cd week2 && uv sync && uv run jupyter notebook
- Open week2_analysis.ipynb and run all cells

### Week 3 - RAG, Vector DBs and Structured Outputs
- Go to week3/ folder
- Main results and outputs: week3/week3_analysis.ipynb
- Helper functions: week3/src/ingest.py, week3/src/retriever.py, week3/src/rag_pipeline.py, week3/src/structured.py
- Add your OpenRouter API key to week3/.env
- Add PDF files to week3/data/pdfs/
- Run: cd week3 && uv sync && uv run jupyter notebook
- Open week3_analysis.ipynb and run ALL cells in order from top to bottom
- Cell 2 ingests PDFs into ChromaDB - must be run first before any other cells

### Week 4 - Agentic AI
- Go to week4/ folder
- Main results and outputs: week4/week4_analysis.ipynb
- Helper functions: week4/src/agent.py, week4/src/tools.py, week4/src/memory.py, week4/src/hooks.py
- Add your OpenRouter API key and Brave Search API key to week4/.env
- Run: cd week4 && uv sync && uv run jupyter notebook
- Open week4_analysis.ipynb and run all cells

## Environment Setup

Each week has its own isolated Python environment managed by uv.

To set up any week:
`ash
cd weekN
uv sync
`

To run Jupyter for any week:
`ash
cd weekN
uv run jupyter notebook
`
## API Keys Required

Create a .env file in each week folder with:
OPENROUTER_API_KEY=your-key-here   # weeks 2, 3, 4
BRAVE_API_KEY=your-key-here        # week 4 only

## prompts.md

All AI interactions are logged in prompts.md in each week folder documenting every significant prompt used during development.
