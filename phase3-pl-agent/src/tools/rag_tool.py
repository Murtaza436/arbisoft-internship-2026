import re
import difflib
import pandas as pd

from src.ingest.pipeline import (
    get_collection,
    get_player_collection,
)

# =====================================================
# TEAM ALIASES & NAMES
# =====================================================

TEAM_ALIASES = {
    "man city": "manchester city",
    "manchester city fc": "manchester city",

    "man utd": "manchester united",
    "man united": "manchester united",
    "manchester united fc": "manchester united",

    "spurs": "tottenham",
    "tottenham hotspur": "tottenham",

    "wolves": "wolverhampton",
    "wolverhampton wanderers": "wolverhampton",

    "newcastle": "newcastle united",
    "west ham": "west ham united",

    "brighton": "brighton hove albion",
    "brighton & hove albion": "brighton hove albion",

    "forest": "nottingham forest",

    "leicester": "leicester city",

    "bournemouth": "afc bournemouth",
}

# Add teams that don't typically need aliases
STANDARD_TEAMS = [
    "arsenal", 
    "aston villa", 
    "chelsea", 
    "crystal palace", 
    "everton", 
    "fulham", 
    "liverpool", 
    "luton town",
    "sheffield united",
    "brentford",
    "burnley",
    "sunderland afc",
    "swansea city",
    "hull city",
    "middlesbrough",
    "cardiff city",
    "norwich city",
    "watford"
]

# Combine both lists so every team is detectable
TEAM_NAMES = sorted(set(list(TEAM_ALIASES.values()) + STANDARD_TEAMS))

STAT_KEYWORDS = {
    "goal",
    "goals",
    "assist",
    "assists",
    "yellow",
    "red",
    "minute",
    "minutes",
    "games",
    "appearance",
    "appearances",
    "career",
    "stats",
    "statistics",
    "season",
    "player",
}

# =====================================================
# NORMALIZE TEXT
# =====================================================

def normalize(text: str):

    text = text.lower()

    text = re.sub(r"[^\w\s]", " ", text)

    for old, new in TEAM_ALIASES.items():
        text = text.replace(old, new)

    return " ".join(text.split())

# =====================================================
# PLAYER DETECTOR
# =====================================================

def find_player(query, metadata):

    if not metadata:
        return None

    names = sorted(
        list(
            {
                m["player"]
                for m in metadata
                if "player" in m
            }
        )
    )

    q = query.lower()

    # full name
    for name in names:
        if name.lower() in q:
            return name

    # surname
    for name in names:
        last = name.split()[-1].lower()
        if last in q:
            return name

    # fuzzy
    match = difflib.get_close_matches(
        q,
        [n.lower() for n in names],
        n=1,
        cutoff=0.65,
    )

    if match:
        for name in names:
            if name.lower() == match[0]:
                return name

    return None

# =====================================================
# QUERY TYPE
# =====================================================

def is_match_query(query):

    q = normalize(query)

    teams = [
        team
        for team in TEAM_NAMES
        if team in q
    ]

    return len(teams) >= 2

def is_player_query(query):

    q = normalize(query)

    if any(word in q for word in STAT_KEYWORDS):
        return True

    if re.search(r"20\d{2}", q):
        return True

    return False

def search_historical_stats_df(query: str, n_results: int = 25):

    q = normalize(query)

    # =====================================================
    # PLAYER SEARCH
    # =====================================================

    player_collection = get_player_collection()

    probe = player_collection.query(
        query_texts=[q],
        n_results=20,
    )

    metadata = probe["metadatas"][0]

    player_name = find_player(q, metadata)

    if player_name:

        results = player_collection.query(
            query_texts=[q],
            n_results=500,
        )

        metadata = results["metadatas"][0]

        if player_name:
            metadata = [
                row
                for row in metadata
                if row["player"] == player_name
            ]

        year_match = re.search(r"(20\d{2})", q)

        if year_match:

            year = int(year_match.group(1))

            metadata = [
                row
                for row in metadata
                if row["season"] == year
            ]

        if len(metadata) == 0:
            return "No player statistics found."

        metadata = sorted(
            metadata,
            key=lambda x: x["season"],
        )

        season_rows = []

        total_games = 0
        total_minutes = 0
        total_goals = 0
        total_assists = 0
        total_yellow = 0
        total_red = 0

        for row in metadata:

            total_games += row.get("games", 0)
            total_minutes += row.get("minutes", 0)
            total_goals += row.get("goals", 0)
            total_assists += row.get("assists", 0)
            total_yellow += row.get("yellow_cards", 0)
            total_red += row.get("red_cards", 0)

            season_rows.append({
                "Season": row["season"],
                "Club": row["team"],
                "Games": row["games"],
                "Minutes": row["minutes"],
                "Goals": row["goals"],
                "Assists": row["assists"],
                "Yellow Cards": row["yellow_cards"],
                "Red Cards": row["red_cards"],
            })

        career_df = pd.DataFrame([{
            "Player": metadata[0]["player"],
            "Games": total_games,
            "Minutes": total_minutes,
            "Goals": total_goals,
            "Assists": total_assists,
            "Yellow Cards": total_yellow,
            "Red Cards": total_red,
        }])

        season_df = pd.DataFrame(season_rows)

        return {
            "career": career_df,
            "season": season_df,
        }

    # =====================================================
    # MATCH SEARCH
    # =====================================================

    collection = get_collection()

    results = collection.query(
        query_texts=[q],
        n_results=n_results,
    )

    docs = results["documents"][0]

    if len(docs) == 0:
        return "No historical matches found."

    requested_teams = [
        team
        for team in TEAM_NAMES
        if team in q
    ]

    rows = []

    for doc in docs:

        season = re.search(r"Season:\s*(.*?)\.", doc)
        competition = re.search(r"Competition:\s*(.*?)\.", doc)
        matchday = re.search(r"Matchday:\s*(.*?)\.", doc)
        home = re.search(r"Home Team:\s*(.*?)\.", doc)
        away = re.search(r"Away Team:\s*(.*?)\.", doc)
        score = re.search(r"Score:\s*([0-9\-]+)", doc)
        winner = re.search(r"Winner:\s*(.*?)\.", doc)

        if not home or not away:
            continue

        home_team = normalize(home.group(1))
        away_team = normalize(away.group(1))

        if len(requested_teams) >= 2:

            if not (
                (
                    requested_teams[0] in home_team
                    and requested_teams[1] in away_team
                )
                or
                (
                    requested_teams[1] in home_team
                    and requested_teams[0] in away_team
                )
            ):
                continue

        elif len(requested_teams) == 1:

            if (
                requested_teams[0] not in home_team
                and
                requested_teams[0] not in away_team
            ):
                continue

        rows.append({
            "Season": season.group(1) if season else "-",
            "Competition": competition.group(1) if competition else "-",
            "Matchday": matchday.group(1).strip() if matchday else "-",
            "Home": home.group(1).replace(" FC", ""),
            "Score": score.group(1) if score else "-",
            "Away": away.group(1).replace(" FC", ""),
            "Winner": winner.group(1).replace(" FC", "") if winner else "-",
        })

    if len(rows) == 0:
        return "No historical matches found."

    df = pd.DataFrame(rows)

    if "Season" in df.columns:
        df = df.sort_values("Season")

    return df

def search_historical_stats(query: str, n_results: int = 25) -> str:
    """
    Wrapper for the RAG agent.

    The notebook uses:
        search_historical_stats_df()

    The agent uses:
        search_historical_stats()

    Always returns a string.
    """

    result = search_historical_stats_df(query, n_results)

    # -----------------------------
    # Error messages
    # -----------------------------
    if isinstance(result, str):
        return result

    # -----------------------------
    # Player search
    # -----------------------------
    if isinstance(result, dict):

        career_df = result["career"]
        season_df = result["season"]

        try:
            career = career_df.to_markdown(index=False)
            season = season_df.to_markdown(index=False)
        except Exception:
            career = career_df.to_string(index=False)
            season = season_df.to_string(index=False)

        return (
            "# PLAYER CAREER SUMMARY\n\n"
            f"{career}\n\n"
            "# PLAYER SEASON BREAKDOWN\n\n"
            f"{season}"
        )

    # -----------------------------
    # Historical matches
    # -----------------------------
    if isinstance(result, pd.DataFrame):

        try:
            return result.to_markdown(index=False)
        except Exception:
            return result.to_string(index=False)

    return str(result)