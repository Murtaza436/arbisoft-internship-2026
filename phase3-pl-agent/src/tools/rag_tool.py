import re
from src.ingest.pipeline import get_collection
import difflib

TEAM_ALIASES = {
    "man city": "manchester city",
    "manchester city fc": "manchester city",
    "man utd": "manchester united",
    "man united": "manchester united",
    "manchester united fc": "manchester united",
    "spurs": "tottenham",
    "tottenham hotspur": "tottenham",
    "tottenham hotspur fc": "tottenham",
    "wolves": "wolverhampton",
    "wolverhampton wanderers": "wolverhampton",
    "wolverhampton wanderers fc": "wolverhampton",
    "newcastle": "newcastle united",
    "newcastle united fc": "newcastle united",
    "west ham": "west ham united",
    "west ham united fc": "west ham united",
    "brighton": "brighton hove albion",
    "brighton & hove albion": "brighton hove albion",
    "brighton & hove albion fc": "brighton hove albion",
    "forest": "nottingham forest",
    "nottingham forest fc": "nottingham forest",
    "leicester": "leicester city",
    "leicester city fc": "leicester city",
    "arsenal fc": "arsenal",
    "chelsea fc": "chelsea",
    "liverpool fc": "liverpool",
    "everton fc": "everton",
    "burnley fc": "burnley",
    "aston villa fc": "aston villa",
    "crystal palace fc": "crystal palace",
    "fulham fc": "fulham",
    "bournemouth": "afc bournemouth",
}


def normalize(text: str) -> str:
    text = text.lower()

    text = re.sub(r"[^\w\s]", " ", text)

    for old, new in TEAM_ALIASES.items():
        text = text.replace(old, new)

    text = " ".join(text.split())

    return text


def find_player(query, metadata):

    names = sorted(list(set(m["player"] for m in metadata)))

    q = query.lower()

    # Exact substring match
    for name in names:
        if name.lower() in q:
            return name

    # Last name match
    for name in names:
        last = name.split()[-1].lower()
        if last in q:
            return name

    # Fuzzy match
    match = difflib.get_close_matches(
        q,
        [n.lower() for n in names],
        n=1,
        cutoff=0.6,
    )

    if match:

        for name in names:
            if name.lower() == match[0]:
                return name

    return None

from src.ingest.pipeline import get_collection, get_player_collection
import re


def search_historical_stats(query: str, n_results: int = 10):

    q = normalize(query)

    # ---------- PLAYER STATS ----------
    stat_keywords = [
        "goal", "goals",
        "assist", "assists",
        "yellow",
        "red",
        "minute",
        "minutes",
        "games",
        "appearances",
        "stats",
        "statistics",
        "player"
    ]

    player_query = (
        any(k in q for k in stat_keywords)
        or len(q.split()) <= 4
    )

    if player_query:

        try:
            collection = get_player_collection()

            results = collection.query(
                query_texts=[q],
                n_results=50,
            )

            docs = results["documents"][0]
            meta = results["metadatas"][0]
            if not meta:
                return "No player statistics found."
            player_name = find_player(q, meta)
            year_match = re.search(r"(20\d{2})", q)

            selected_year = None

            if year_match:
                selected_year = int(year_match.group(1))

            if player_name:

                meta = [
                    m for m in meta
                    if m["player"] == player_name
                ]

            if selected_year:

                meta = [
                    m for m in meta
                    if m["year"] == selected_year
                ]
                
            if not meta:
                return "No player statistics found for that player/season."
            
            if not docs:
                return "No player statistics found."

            meta.sort(key=lambda x: x["year"])
            
            total_games = 0
            total_minutes = 0
            total_goals = 0
            total_assists = 0
            total_yellow = 0
            total_red = 0

            player = meta[0]["player"]

            season_breakdown = []

            for m in meta:

                total_games += m.get("games", 0)
                total_minutes += m.get("minutes", 0)
                total_goals += m.get("goals", 0)
                total_assists += m.get("assists", 0)
                total_yellow += m.get("yellow_cards", 0)
                total_red += m.get("red_cards", 0)

                season_breakdown.append(
                    f"""
            ### {m['year']}

            Games: {m['games']}

            Minutes: {m['minutes']}

            Goals: {m['goals']}

            Assists: {m['assists']}

            Yellow Cards: {m['yellow_cards']}

            Red Cards: {m['red_cards']}
            """
                )

            return f"""
            # {player}

            ## Career Statistics

            Games: **{total_games}**

            Minutes: **{total_minutes}**

            Goals: **{total_goals}**

            Assists: **{total_assists}**

            Yellow Cards: **{total_yellow}**

            Red Cards: **{total_red}**

            ---

            ## Season Breakdown

            {''.join(season_breakdown)}
            """

        except Exception as e:
            return f"Player search failed: {e}"

    # ---------- MATCH SEARCH ----------

    try:

        collection = get_collection()

        results = collection.query(
            query_texts=[q],
            n_results=n_results,
        )

        docs = results["documents"][0]

        if not docs:
            return "No historical matches found."

        output = ["# Historical Premier League Matches\n"]

        for doc in docs:

            season = re.search(r"Season:\s*([0-9\-]+)", doc)
            home = re.search(r"Home Team:\s*(.*?)\.", doc)
            away = re.search(r"Away Team:\s*(.*?)\.", doc)
            score = re.search(r"Score:\s*([0-9\-]+)", doc)
            winner = re.search(r"Winner:\s*(.*?)\.", doc)

            output.append(
                f"""
        ## {home.group(1)} {score.group(1)} {away.group(1)}

        Season: {season.group(1)}

        Winner: {winner.group(1)}
        """
            )

        return "\n\n".join(output)

    except Exception as e:

        return f"Historical search failed: {e}"