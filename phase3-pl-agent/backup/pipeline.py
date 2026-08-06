import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from src.ingest.statsbomb import (
    get_competition_id,
    load_matches,
    load_events,
    extract_player_stats,
    stats_to_text,
)

EMBEDDING_FN = SentenceTransformerEmbeddingFunction(
    model_name='all-MiniLM-L6-v2'
)
COLLECTION_NAME = 'pl_player_stats'


def get_chroma_client():
    return chromadb.PersistentClient(path='./chroma_db')


def get_or_create_collection():
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    return client.create_collection(
        COLLECTION_NAME,
        embedding_function=EMBEDDING_FN,
    )


def get_collection():
    client = get_chroma_client()
    return client.get_collection(
        COLLECTION_NAME,
        embedding_function=EMBEDDING_FN,
    )


def ingest_statsbomb(data_path: str, max_seasons: int = None):
    print(f'Loading StatsBomb data from {data_path}...')
    seasons = get_competition_id(data_path)

    if not seasons:
        print('No Premier League seasons found in StatsBomb data.')
        print('Make sure you cloned github.com/statsbomb/open-data')
        return None

    if max_seasons:
        seasons = seasons[:max_seasons]

    print(f'Found {len(seasons)} Premier League seasons to ingest')
    collection = get_or_create_collection()

    all_texts = []
    all_ids = []
    all_metadata = []
    chunk_id = 0

    for season_info in seasons:
        competition_id = season_info['competition_id']
        season_id = season_info['season_id']
        season_name = season_info['season_name']
        print(f'Processing season: {season_name}...')

        matches = load_matches(data_path, competition_id, season_id)
        print(f'  Found {len(matches)} matches')

        for match in matches:
            match_id = match.get('match_id')
            events = load_events(data_path, match_id)

            if not events:
                continue

            player_stats_list = extract_player_stats(match, events)

            for stats in player_stats_list:
                text = stats_to_text(stats)
                all_texts.append(text)
                all_ids.append(f'chunk_{chunk_id}')
                all_metadata.append({
                    'player': stats['player_name'],
                    'team': stats['team'],
                    'season': stats['season'],
                    'match_date': stats['match_date'],
                })
                chunk_id += 1

            if chunk_id % 500 == 0:
                print(f'  Processed {chunk_id} player-match records...')

    if not all_texts:
        print('No records found to ingest.')
        return None

    batch_size = 100
    for i in range(0, len(all_texts), batch_size):
        batch_texts = all_texts[i:i + batch_size]
        batch_ids = all_ids[i:i + batch_size]
        batch_meta = all_metadata[i:i + batch_size]
        collection.add(
            documents=batch_texts,
            ids=batch_ids,
            metadatas=batch_meta,
        )
        if (i // batch_size) % 10 == 0:
            print(f'  Stored {i + len(batch_texts)} records in ChromaDB...')

    print(f'Ingestion complete. Total records: {collection.count()}')
    return collection
