---

## Week 6: Data Retrieval, Football Data and Tool Integration

### Week 6

**Prompt:** "Help me build and integrate the football data tools required for the Premier League research assistant, including standings, top scorers, recent results, upcoming fixtures, and team matches."

**Model:** GPT

**Result:** Developed the live football tool layer for retrieving Premier League standings, top scorers, recent results, upcoming fixtures, and team-specific matches.

### Week 6

**Prompt:** "Help me debug the football API and make sure the live tools return usable data for the agent."

**Model:** GPT

**Result:** Worked through API responses and tool errors, including cases where expected football data was missing or returned in an unexpected format. The tools were refined to provide structured outputs that could be passed to the AI agent.

### Week 6

**Prompt:** "How should the football tools be registered so that the agent can select and execute them?"

**Model:** GPT

**Result:** Structured the tool registry so the agent could access the available football tools through function calling and map tool names to their Python implementations.

---

## Week 7: Historical Data and RAG

### Week 7

**Prompt:** "Build a historical Premier League data pipeline using OpenFootball data and ChromaDB."

**Model:** GPT

**Result:** Developed the historical match ingestion pipeline and stored Premier League match records in a persistent ChromaDB collection named pl_history.

### Week 7

**Prompt:** "Add historical Premier League player statistics to the RAG system using a separate ChromaDB collection."

**Model:** GPT

**Result:** Added player-statistics ingestion using the player CSV dataset and created the pl_player_stats ChromaDB collection. Player records were converted into searchable documents with metadata such as season, team, games, minutes, goals, assists, yellow cards, and red cards.

### Week 7

**Prompt:** "Fix the ChromaDB client and collection access so the historical RAG tool can retrieve both match and player data."

**Model:** GPT

**Result:** Refactored the ChromaDB access functions so the application could retrieve the historical match collection and player-statistics collection independently.

### Week 7

**Prompt:** "Make the historical search understand whether the user is asking about a player or a match."

**Model:** GPT

**Result:** Improved the RAG search logic with team aliases, player detection, statistical keywords, season detection, and separate retrieval paths for historical matches and player statistics.

### Week 7

**Prompt:** "Make historical player searches such as Mohamed Salah 2017 return the relevant statistics."

**Model:** Gemini

**Result:** Added player-name detection, last-name matching, fuzzy matching, and season filtering to improve historical player retrieval.

### Week 7

**Prompt:** "Return historical RAG results in a format that can be used by both the Jupyter notebook and the AI agent."

**Model:** Gemini

**Result:** Created a dataframe-based search function for notebook use and a string-based wrapper for the agent. Player results could be returned as career and season tables, while historical match results could be returned as structured tables.

---

## Week 8: Final Premier League AI Research Assistant

### Week 8

**Prompt:** "Improve the Premier League research assistant so that it can answer live, historical, and web-search football questions using the appropriate tools."

**Model:** GPT

**Result:** Refined the agent architecture and tool routing so current football questions use live tools, historical questions use the RAG system, and news, transfers, injuries, and rumours can use web search.

### Week 8

**Prompt:** "Make the agent answer football questions using tool results instead of relying on its own football knowledge."

**Model:** GPT

**Result:** Strengthened the system prompt and fallback behaviour to reduce unsupported answers and require the assistant to ground football responses in retrieved tool data.

### Week 8

**Prompt:** "Improve historical football queries and team aliases so users can search teams using names such as Man City, Man United, Spurs, Wolves, Newcastle, and Leicester."

**Model:** Gemini

**Result:** Added and refined team aliases and text normalization so different ways of referring to Premier League clubs could be mapped to consistent team names.

### Week 8

**Prompt:** "Make comparisons such as Mohamed Salah vs Erling Haaland return a clear table instead of an unstructured answer."

**Model:** GPT

**Result:** Added structured comparison output so player comparisons can be presented using Markdown tables containing relevant statistics.

### Week 8

**Prompt:** "Make team comparisons such as Liverpool vs Manchester City and Arsenal vs Chelsea appear in a structured tabular format."

**Model:** GPT

**Result:** Improved the response formatting for multi-team questions so relevant statistics and retrieved information can be presented in a clear comparison table.

### Week 8

**Prompt:** "Allow historical comparisons such as Leicester City's title-winning season vs Liverpool's 2019/20 season."

**Model:** GPT

**Result:** Extended the research assistant's comparison capability to support historical Premier League seasons and present the retrieved information in a structured format.

### Week 8

**Prompt:** "Make the interactive chat support natural-language football research questions and return concise, structured answers."

**Model:** GPT

**Result:** Refined the interactive chat experience so users can ask questions about standings, scorers, fixtures, results, teams, players, historical matches, and comparisons using natural language.

### Week 8

**Prompt:** "Create a Streamlit application for the final version of the Premier League AI research assistant without replacing the existing agent and tool architecture."

**Model:** GPT

**Result:** Created pp.py as the Streamlit entry point while keeping the existing agent, memory, RAG, live tools, search tools, and ingestion pipeline.

### Week 8

**Prompt:** "Make the Streamlit application support the main comparison and research features of the football assistant."

**Model:** GPT

**Result:** Designed the final interface around interactive football research, including player comparisons, team comparisons, historical season comparisons, standings, scorers, fixtures, results, and historical searches.

### Week 8

**Prompt:** "Prepare the final README and prompts documentation for the Premier League AI research assistant."

**Model:** Gemini

**Result:** Created concise project documentation describing the system, features, technology stack, project structure, setup instructions, example questions, RAG architecture, security considerations, and AI-assisted development process.

---

## Overall AI-Assisted Development

Across Weeks 6�8, AI assistance was used for:

- Football API integration
- Tool development and debugging
- Tool registration and routing
- Historical data ingestion
- ChromaDB integration
- Sentence Transformer embeddings
- Player-statistics retrieval
- Historical match retrieval
- Query classification
- Team-name normalization
- Agent prompting
- Structured comparison output
- Streamlit interface development
- Debugging and documentation

The generated solutions were tested, modified, and integrated into the project during development rather than being used without verification.
