from src.ingest.pipeline import get_collection


def search_historical_stats(query: str, n_results: int = 5) -> str:
    try:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        chunks = results['documents'][0]
        if not chunks:
            return 'No historical records found for this query.'
        output = ['Historical Premier League Stats (2015-16 to 2022-23):\n']
        for i, chunk in enumerate(chunks, 1):
            output.append(f'{i}. {chunk}')
        return '\n'.join(output)
    except Exception as e:
        return f'RAG search failed: {str(e)}. Make sure you have run the ingestion pipeline first.'
