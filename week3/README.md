# Week 3 — RAG, Vector Databases and Structured Outputs

## What This Week Covers
Building a Retrieval Augmented Generation (RAG) pipeline that reads PDF documents,
stores them in a vector database, and answers questions from the retrieved content.
Also covers structured outputs with Pydantic validation and hallucination detection.

## Folder Structure
week3/
+-- src/
<<<<<<< HEAD
¦ +-- ingest.py # loads PDFs, chunks text, stores in ChromaDB
¦ +-- retriever.py # searches ChromaDB for relevant chunks
¦ +-- rag_pipeline.py # combines retrieval and LLM generation
¦ +-- structured.py # structured output pipeline with Pydantic
¦ +-- constants.py # color constants for terminal output
+-- tests/
¦ +-- test_structured.py # validation tests for Pydantic schema
+-- data/
¦ +-- pdfs/ # put your PDF files here
+-- week3_analysis.ipynb # main notebook with all outputs and results
+-- prompts.md # AI interaction log
+-- .env # API keys (never committed)
## How to Run

### 1. Setup
`ash
cd week3
uv sync
uv add openai python-dotenv chromadb sentence-transformers pypdf pydantic pandas jupyter notebook
`
=======
¦   +-- ingest.py        - loads PDFs, chunks text, stores in ChromaDB
¦   +-- retriever.py     - searches ChromaDB for relevant chunks
¦   +-- rag_pipeline.py  - combines retrieval and LLM generation
¦   +-- structured.py    - structured output pipeline with Pydantic
¦   +-- constants.py     - color constants for terminal output
+-- tests/
¦   +-- test_structured.py  - validation tests for Pydantic schema
+-- data/
¦   +-- pdfs/            - put your PDF files here
+-- week3_analysis.ipynb - main notebook with all outputs and results
+-- prompts.md           - AI interaction log
+-- .env                 - API keys never committed

## How to Run

### 1. Setup
cd week3
uv sync
uv add openai python-dotenv chromadb sentence-transformers pypdf pydantic pandas jupyter notebook
>>>>>>> main

### 2. Add API Key
Create a .env file in the week3 folder:
OPENROUTER_API_KEY=your-key-here
<<<<<<< HEAD
### 3. Add PDF Files
Put any PDF files inside data/pdfs/ folder.
Make sure they are text-based PDFs not scanned images.
Good sources: Wikipedia pages downloaded as PDF, research papers from arxiv.org.

### 4. Run the Notebook
`ash
uv run jupyter notebook
`
Open week3_analysis.ipynb and run ALL cells in order from top to bottom.

**Important:** Cell 2 must run first — it ingests PDFs into ChromaDB.
Do not skip it or the remaining cells will fail.

## Cell Order in Notebook
| Cell | What it does |
|------|-------------|
| Cell 1 | Imports and setup |
| Cell 2 | Ingests PDFs into ChromaDB — run this first |
| Cell 3 | Tests retrieval — finds relevant chunks for a query |
| Cell 4 | RAG answers — agent answers questions from documents |
| Cell 5 | Structured output — LLM returns validated JSON |
| Cell 6 | Results table |
| Cell 7 | Hallucination analysis |
| Cell 8 | Findings and notes |

## Run Tests
`ash
uv run pytest tests/ -v
`

=======

### 3. Add PDF Files
Put any PDF files inside data/pdfs/ folder.
Make sure they are text-based PDFs not scanned images.

### 4. Run the Notebook
uv run jupyter notebook
Open week3_analysis.ipynb and run ALL cells in order from top to bottom.
Important: Cell 2 must run first to ingest PDFs into ChromaDB.

## Cell Order in Notebook
Cell 1 - Imports and setup
Cell 2 - Ingests PDFs into ChromaDB, run this first
Cell 3 - Tests retrieval, finds relevant chunks for a query
Cell 4 - RAG answers, agent answers questions from documents
Cell 5 - Structured output, LLM returns validated JSON
Cell 6 - Results table
Cell 7 - Hallucination analysis
Cell 8 - Findings and notes

## Run Tests
uv run pytest tests/ -v

>>>>>>> main
## Key Concepts Demonstrated
- RAG: Retrieve relevant chunks, augment the prompt, generate answer
- ChromaDB: vector database storing text as embeddings for semantic search
- Embeddings: all-MiniLM-L6-v2 local model, no API cost
- Chunking: 500 character chunks with 50 character overlap
- Pydantic: validates LLM JSON output against a schema
- Hallucination: detected by prompting the model to say I do not know

## Models Used
- Embedding model: all-MiniLM-L6-v2 via SentenceTransformers (local, free)
- LLM: nvidia/nemotron-3-ultra-550b-a55b:free via OpenRouter
<<<<<<< HEAD
- Structured output: poolside/laguna-xs-2.1:free via OpenRouter
=======
>>>>>>> main
