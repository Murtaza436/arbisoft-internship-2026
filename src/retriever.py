import chromadb


def get_collection(collection_name='week3_docs'):
    """Connect to existing ChromaDB collection."""
    client = chromadb.PersistentClient(path='./chroma_db')
    return client.get_collection(collection_name)


def retrieve(query, collection, n_results=3):
    """Retrieve most relevant chunks for a query."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    chunks = results['documents'][0]
    sources = [m['source'] for m in results['metadatas'][0]]
    return chunks, sources
