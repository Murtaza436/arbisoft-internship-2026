import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from src.ingest.player_stats import load_player_stats
from src.ingest.openfootball import load_matches

EMBEDDING_FN = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

MATCH_COLLECTION = "pl_history"

PLAYER_COLLECTION = "pl_players"


def get_chroma_client():
    return chromadb.PersistentClient(path="./chroma_db")


def get_or_create_collection():
    client = get_chroma_client()

    try:
        client.delete_collection(MATCH_COLLECTION)
    except Exception:
        pass

    return client.create_collection(
        MATCH_COLLECTION,
        embedding_function=EMBEDDING_FN,
    )


def get_collection():
    client = get_chroma_client()

    return client.get_collection(
        MATCH_COLLECTION,
        embedding_function=EMBEDDING_FN,
    )
    
def get_player_collection():

    client = get_chroma_client()

    return client.get_collection(
        PLAYER_COLLECTION,
        embedding_function=EMBEDDING_FN,
    )


def ingest_history(data_path="data/openfootball"):

    collection = get_or_create_collection()

    matches = load_matches(data_path)

    documents = []
    ids = []
    metadata = []

    for i, match in enumerate(matches):

        documents.append(match["text"])

        ids.append(f"match_{i}")

        metadata.append({
            "season": match["season"],
            "competition": "Premier League",
            "matchday": match["matchday"],
            "home": match["home"],
            "away": match["away"],
            "winner": match["winner"]
        })

    batch_size = 100

    for start in range(0, len(documents), batch_size):

        end = min(start + batch_size, len(documents))

        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadata[start:end]
        )

        print(
            f"Stored {min(end,len(documents))}/{len(documents)}"
        )

    print()

    print("Done.")

    print("Documents:", collection.count())

    return collection

def ingest_player_stats(csv_path="data/player_data/player.csv"):

    client = get_chroma_client()

    # Delete old player collection before rebuilding
    try:
        client.delete_collection(PLAYER_COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(
        PLAYER_COLLECTION,
        embedding_function=EMBEDDING_FN,
    )

    players = load_player_stats(csv_path)

    documents = []
    ids = []
    metadata = []

    for i, p in enumerate(players):

        documents.append(p["text"])
        ids.append(f"player_{i}")

        metadata.append(
            {
                "player": p["player"],
                "team": p["team"],
                "year": p["year"],
                "games": p["games"],
                "minutes": p["minutes"],
                "goals": p["goals"],
                "assists": p["assists"],
                "yellow_cards": p["yellow_cards"],
                "red_cards": p["red_cards"],
            }
        )

    # Add to ChromaDB in smaller batches
    batch_size = 500

    for start in range(0, len(documents), batch_size):

        end = min(start + batch_size, len(documents))

        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadata[start:end],
        )

        print(
            f"Stored {end}/{len(documents)} player seasons"
        )

    print()
    print("Player collection created.")
    print("Documents:", collection.count())

    return collection