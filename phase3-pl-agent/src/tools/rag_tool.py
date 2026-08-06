import re
import difflib
import pandas as pd

from src.ingest.pipeline import get_collection, get_player_collection


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


def normalize(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)

    for old, new in TEAM_ALIASES.items():
        text = text.replace(old, new)

    text = " ".join(text.split())
    return text


def find_player(query, metadata):
    """
    Returns the player name if the query clearly refers to a player.
    """
    names = sorted(
        list(
            set(
                m["player"]
                for m in metadata
                if "player" in m
            )
        )
    )

    q = query.lower()

    # Exact full name
    for name in names:
        if name.lower() in q:
            return name

    # Last-name match
    for name in names:
        last = name.split()[-1].lower()
        if last in q:
            return name

    # Fuzzy match
    match = difflib.get_close_matches(
        q,
        [n.lower() for n in names],
        n=1,
        cutoff=0.75,
    )

    if match:
        for name in names:
            if name.lower() == match[0]:
                return name

    return None


# ----------------------------------------------------
# 1. DATAFRAME VERSION (For Jupyter Notebook)
# ----------------------------------------------------
def search_historical_stats_df(query: str, n_results: int = 10):
    
    q = normalize(query)

    # ----------------------------------------------------
    # PLAYER DETECTION
    # ----------------------------------------------------
    stat_keywords = {
        "goal", "goals",
        "assist", "assists",
        "yellow", "red",
        "minute", "minutes",
        "games", "appearance", "appearances",
        "stats", "statistics",
        "career", "player",
        "season"
    }

    # Detect if the query is likely asking about a match
    team_names = [
        "arsenal", "chelsea", "liverpool",
        "manchester city", "manchester united",
        "tottenham", "everton", "aston villa",
        "newcastle united", "leicester city",
        "west ham united", "brighton hove albion",
        "crystal palace", "wolverhampton",
        "nottingham forest", "fulham",
        "afc bournemouth", "burnley"
    ]

    team_count = sum(team in q for team in team_names)

    player_name = None

    # Only search the player database if this is NOT clearly a match query
    if team_count < 2:
        try:
            player_collection = get_player_collection()
            result = player_collection.query(
                query_texts=[q],
                n_results=10,
            )
            player_name = find_player(
                q,
                result["metadatas"][0]
            )
        except Exception:
            player_name = None

    player_query = (
        player_name is not None
        or any(word in q for word in stat_keywords)
    )

    # ----------------------------------------------------
    # PLAYER SEARCH
    # ----------------------------------------------------
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

            year_match = re.search(r"(20\d{2})", q)
            selected_year = None

            if year_match:
                selected_year = int(year_match.group(1))

            if player_name:
                meta = [
                    m
                    for m in meta
                    if m["player"] == player_name
                ]

            if selected_year:
                meta = [
                    m
                    for m in meta
                    if m["year"] == selected_year
                ]

            if not meta:
                return "No player statistics found."

            meta.sort(key=lambda x: x["year"])

            total_games = 0
            total_minutes = 0
            total_goals = 0
            total_assists = 0
            total_yellow = 0
            total_red = 0

            player = meta[0]["player"]
            season_rows = []

            for m in meta:
                total_games += m.get("games", 0)
                total_minutes += m.get("minutes", 0)
                total_goals += m.get("goals", 0)
                total_assists += m.get("assists", 0)
                total_yellow += m.get("yellow_cards", 0)
                total_red += m.get("red_cards", 0)

                season_rows.append({
                    "Season": m["year"],
                    "Games": m["games"],
                    "Minutes": m["minutes"],
                    "Goals": m["goals"],
                    "Assists": m["assists"],
                    "Yellow Cards": m["yellow_cards"],
                    "Red Cards": m["red_cards"],
                })

            career_df = pd.DataFrame([{
                "Player": player,
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

        except Exception as e:
            return f"Player search failed: {e}"

    # ----------------------------------------------------
    # MATCH SEARCH
    # ----------------------------------------------------
    try:
        collection = get_collection()
        all_data = collection.get()
        docs = all_data["documents"]

        requested = []
        for team in team_names:
            if team in q:
                requested.append(team)

        matches = []
        for doc in docs:
            home = re.search(r"Home Team:\s*(.*?)\.", doc)
            away = re.search(r"Away Team:\s*(.*?)\.", doc)

            if not home or not away:
                continue

            home_team = normalize(home.group(1))
            away_team = normalize(away.group(1))

            if len(requested) >= 2:
                if (
                    requested[0] in home_team
                    and requested[1] in away_team
                ) or (
                    requested[1] in home_team
                    and requested[0] in away_team
                ):
                    matches.append(doc)

            elif len(requested) == 1:
                if (
                    requested[0] in home_team
                    or requested[0] in away_team
                ):
                    matches.append(doc)

        if not matches:
            return "No historical matches found."

        rows = []
        for doc in matches:
            season = re.search(r"Season:\s*(.*?)\.", doc)
            matchday = re.search(r"Matchday:\s*(.*?)\.", doc)
            competition = re.search(r"Competition:\s*(.*?)\.", doc)
            home = re.search(r"Home Team:\s*(.*?)\.", doc)
            away = re.search(r"Away Team:\s*(.*?)\.", doc)
            score = re.search(r"Score:\s*([0-9\-]+)", doc)
            winner = re.search(r"Winner:\s*(.*?)\.", doc)

            rows.append({
                "Season": season.group(1) if season else "-",
                "Matchday": matchday.group(1).replace("▪","").strip() if matchday else "-",
                "Home": home.group(1).replace(" FC","") if home else "-",
                "Score": score.group(1) if score else "-",
                "Away": away.group(1).replace(" FC","") if away else "-",
                "Winner": winner.group(1).replace(" FC","") if winner else "-",
            })

        df = pd.DataFrame(rows)
        df = df.sort_values("Season")

        return df

    except Exception as e:
        return f"Historical search failed: {e}"


# ----------------------------------------------------
# 2. STRING VERSION (For RAG Agent Tools)
# ----------------------------------------------------
def search_historical_stats(query: str, n_results: int = 10) -> str:
    """
    Wrapper that executes the search and guarantees a string return type 
    so the agent pipeline context builder does not break.
    """
    result = search_historical_stats_df(query, n_results)

    # 1. Handle error strings or "not found" messages
    if isinstance(result, str):
        return result

    # 2. Handle Player Dictionary format
    if isinstance(result, dict) and "career" in result and "season" in result:
        # Using .to_string(index=False) safely converts DataFrame to a text grid
        career_str = result["career"].to_string(index=False)
        season_str = result["season"].to_string(index=False)
        
        return (
            f"Player Career Stats:\n{career_str}\n\n"
            f"Player Season Stats:\n{season_str}"
        )

    # 3. Handle Match DataFrame format
    if isinstance(result, pd.DataFrame):
        return result.to_string(index=False)

    # 4. Catch-all fallback
    return str(result)