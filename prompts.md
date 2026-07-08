# prompts.md — AI Interaction Log

## Week 3: RAG, Vector DBs and Structured Outputs

### 2026-06-28
**Prompt:** "Give me the complete week 3 setup from start to finish including RAG pipeline, structured outputs and validation tests."
**Model:** Claude (claude.ai)
**Result:** Received full project structure, ingest.py for PDF loading and chunking, retriever.py for ChromaDB search, rag_pipeline.py combining retrieval and generation, structured.py with Pydantic validation, and complete jupyter notebook cells.

### 2026-06-28
**Prompt:** "What is RAG and why is chunking important?"
**Model:** Claude (claude.ai)
**Result:** RAG stands for Retrieval Augmented Generation. Chunking splits documents into smaller pieces so the most relevant section can be retrieved rather than the entire document. Overlap between chunks ensures sentences at boundaries are not missed.

### 2026-06-28
**Prompt:** "How does Pydantic validation catch LLM output errors?"
**Model:** Claude (claude.ai)
**Result:** Pydantic defines a schema as a Python class. When the LLM output is parsed as JSON and passed to the class, Pydantic checks every field type and raises a ValidationError if anything is wrong. This catches missing fields, wrong types, and unexpected values.

### 2026-06-28
**Prompt:** "How do I detect hallucinations in a RAG system?"
**Model:** Claude (claude.ai)
**Result:** Two main ways: ask about topics not in the documents and check if the model says I do not know versus making something up, and check if the answer contains words actually present in the retrieved chunks. Added explicit prompt instruction to say I do not know if the answer is not in the context.
