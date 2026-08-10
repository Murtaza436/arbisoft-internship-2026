# Premier League Research Assistant

An AI-powered Premier League research assistant built with Python, ChromaDB, RAG, live football data, web search, and a Streamlit interface.

## Features

- Live Premier League standings
- Current top scorers
- Recent results and upcoming fixtures
- Team schedules
- Historical Premier League match search
- Historical player statistics
- Player comparisons such as Salah vs Haaland
- Team comparisons such as Liverpool vs Manchester City
- Historical comparisons such as Leicester City's 2015/16 title-winning season
- Interactive AI chat for natural-language football questions
- RAG-based retrieval using ChromaDB
- Web search for news, transfers, injuries, and other current information

## Tech Stack

- Python
- Streamlit
- ChromaDB
- Sentence Transformers
- OpenRouter
- Ollama
- Pandas
- OpenFootball historical data
- Live football API
- Brave Search

## Project Structure

`	ext
phase3-pl-agent/
│
├── app.py                  # Streamlit application
├── src/
│   ├── agent.py            # Main AI agent
│   ├── memory.py           # Session memory
│   ├── constants.py
│   ├── ingest/
│   │   ├── pipeline.py
│   │   ├── player_stats.py
│   │   └── openfootball.py
│   └── tools/
│       ├── live_tool.py
│       ├── rag_tool.py
│       ├── search_tool.py
│       └── registry.py
│
├── data/
├── chroma_db/
├── .env
├── .gitignore
└── README.md
`

## Setup

Clone the repository and create a virtual environment:

`ash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
`

Create a .env file containing the required API keys:

`	ext
OPENROUTER_API_KEY=your_key
BRAVE_API_KEY=your_key
`

Build the historical ChromaDB collections if required:

`ash
python -c "from src.ingest.pipeline import ingest_history, ingest_player_stats; ingest_history(); ingest_player_stats()"
`

## Run the Application

Start the Streamlit application from the project root:

`ash
streamlit run app.py
`

The application will open in your browser.

## Example Questions

The assistant can answer questions such as:

- "Show me the current Premier League standings."
- "Who are the top scorers?"
- "Compare Mohamed Salah and Erling Haaland."
- "Compare Liverpool and Manchester City."
- "How did Leicester City perform in the 2015/16 season?"
- "Compare Leicester's title-winning season with Liverpool's 2019/20 season."
- "Compare Arsenal and Chelsea."
- "What were Liverpool's recent results?"
- "What are Manchester City's upcoming fixtures?"
- "What happened in the 2017 Premier League season?"

## RAG System

Historical information is stored in ChromaDB using Sentence Transformer embeddings.
Two main collections are used:

- pl_history — historical Premier League matches
- pl_player_stats — historical player statistics

The RAG tool retrieves relevant historical information before generating an answer.

## Security

API keys and local databases are excluded from Git using .gitignore.
Never commit .env, API keys, or private credentials.

---

**Murtaza**
Premier League AI Research Assistant — Phase 3
