import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from src.ingest.openfootball import load_matches
from src.ingest.player_stats import load_player_stats

EMBEDDING_FN = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

MATCH_COLLECTION = "pl_history"
PLAYER_COLLECTION = "pl_player_stats"


def get_embedding_fn():
    return EMBEDDING_FN


def get_chroma_client():
    return chromadb.PersistentClient(path="./chroma_db")


# =====================================================
# MATCH COLLECTION
# =====================================================

def get_collection():
    client = get_chroma_client()

    return client.get_collection(
        MATCH_COLLECTION,
        embedding_function=EMBEDDING_FN,
    )


def create_match_collection():
    client = get_chroma_client()

    try:
        client.delete_collection(MATCH_COLLECTION)
    except Exception:
        pass

    return client.create_collection(
        MATCH_COLLECTION,
        embedding_function=EMBEDDING_FN,
    )


# =====================================================
# PLAYER COLLECTION
# =====================================================

def get_player_collection():
    client = get_chroma_client()

    return client.get_collection(
        PLAYER_COLLECTION,
        embedding_function=EMBEDDING_FN,
    )


def create_player_collection():
    client = get_chroma_client()

    try:
        client.delete_collection(PLAYER_COLLECTION)
    except Exception:
        pass

    return client.create_collection(
        PLAYER_COLLECTION,
        embedding_function=EMBEDDING_FN,
    )


# =====================================================
# INGEST MATCH HISTORY
# =====================================================

def ingest_history(data_path="data/openfootball"):

    collection = create_match_collection()

    matches = load_matches(data_path)

    documents = []
    ids = []
    metadatas = []

    for i, match in enumerate(matches):

        documents.append(match["text"])

        ids.append(f"match_{i}")

        metadatas.append(
            {
                "season": match["season"],
                "competition": "Premier League",
                "matchday": match["matchday"],
                "home": match["home"],
                "away": match["away"],
                "winner": match["winner"],
            }
        )

    batch_size = 100

    for start in range(0, len(documents), batch_size):

        end = min(start + batch_size, len(documents))

        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

        print(f"Stored {end}/{len(documents)}")

    print()
    print("Done.")
    print("Documents:", collection.count())

    return collection


# =====================================================
# INGEST PLAYER STATS
# =====================================================

def ingest_player_stats(csv_path="data/player_data/player.csv"):

    collection = create_player_collection()

    players = load_player_stats(csv_path)

    documents = []
    ids = []
    metadatas = []

    for i, player in enumerate(players):

        documents.append(player["text"])

        ids.append(f"player_{i}")

        metadatas.append(
            {
                "player": player["player"],
                "team": player["team"],
                "season": player["year"],
                "games": player["games"],
                "minutes": player["minutes"],
                "goals": player["goals"],
                "assists": player["assists"],
                "yellow_cards": player["yellow_cards"],
                "red_cards": player["red_cards"],
            }
        )

    batch_size = 500

    for start in range(0, len(documents), batch_size):

        end = min(start + batch_size, len(documents))

        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

        print(f"Stored {end}/{len(documents)} player records")

    print()
    print("Player collection created.")
    print("Documents:", collection.count())

    return collection