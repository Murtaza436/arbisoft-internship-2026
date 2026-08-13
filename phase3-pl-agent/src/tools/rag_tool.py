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

    "bournemouth": "afc bournemouth",
    "afc bournemouth": "afc bournemouth",

    "arsenal fc": "arsenal",
    "chelsea fc": "chelsea",
    "liverpool fc": "liverpool",
    "aston villa fc": "aston villa",
    "everton fc": "everton",
    "burnley fc": "burnley",
    "crystal palace fc": "crystal palace",
    "fulham fc": "fulham",
}


STANDARD_TEAMS = [
    "arsenal",
    "aston villa",
    "afc bournemouth",
    "brighton hove albion",
    "burnley",
    "chelsea",
    "crystal palace",
    "everton",
    "fulham",
    "leicester city",
    "liverpool",
    "manchester city",
    "manchester united",
    "newcastle united",
    "nottingham forest",
    "tottenham",
    "west ham united",
    "wolverhampton",
    "luton town",
    "sheffield united",
    "brentford",
    "sunderland afc",
    "swansea city",
    "hull city",
    "middlesbrough",
    "cardiff city",
    "norwich city",
    "watford",
]


TEAM_NAMES = sorted(
    set(list(TEAM_ALIASES.values()) + STANDARD_TEAMS)
)


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
# TEXT NORMALIZATION
# =====================================================

def normalize(text: str) -> str:
    """
    Normalize user queries and team names so that aliases
    such as 'Man City' and 'Manchester City' are treated
    consistently.
    """

    text = text.lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
    )

    for old, new in TEAM_ALIASES.items():
        text = text.replace(old, new)

    return " ".join(text.split())


# =====================================================
# PLAYER DETECTION
# =====================================================

def find_player(query: str, metadata):
    """
    Find a player name from a query.

    Detection order:

    1. Exact full-name match
    2. First-name + surname match
    3. Unique surname match
    4. Fuzzy player-name match

    Unlike the previous version, this function receives
    metadata from the entire player collection rather than
    only Chroma's top semantic-search results.
    """

    if not metadata:
        return None

    names = sorted(
        list(
            {
                m["player"]
                for m in metadata
                if m.get("player")
            }
        )
    )

    q = normalize(query)

    q_words = set(q.split())

    # -------------------------------------------------
    # 1. Exact full-name match
    # -------------------------------------------------

    for name in names:

        if name.lower() in q:
            return name

    # -------------------------------------------------
    # 2. First name + surname
    # -------------------------------------------------

    for name in names:

        name_words = name.lower().split()

        if len(name_words) >= 2:

            first_name = name_words[0]
            surname = name_words[-1]

            if (
                first_name in q_words
                and surname in q_words
            ):
                return name

    # -------------------------------------------------
    # 3. Unique surname
    # -------------------------------------------------

    surname_matches = []

    for name in names:

        surname = name.split()[-1].lower()

        if surname in q_words:
            surname_matches.append(name)

    if len(surname_matches) == 1:
        return surname_matches[0]

    # -------------------------------------------------
    # 4. Fuzzy matching
    # -------------------------------------------------

    query_words = [
        word
        for word in q.split()
        if word not in STAT_KEYWORDS
    ]

    player_query = " ".join(query_words).strip()

    if player_query:

        match = difflib.get_close_matches(
            player_query,
            [name.lower() for name in names],
            n=1,
            cutoff=0.65,
        )

        if match:

            for name in names:

                if name.lower() == match[0]:
                    return name

    return None


# =====================================================
# PLAYER RECORD RETRIEVAL
# =====================================================

def get_player_records(player_name: str):
    """
    Retrieve every historical record belonging to one
    specific player.

    This uses Chroma metadata filtering rather than
    semantic search because the player name is already known.
    """

    collection = get_player_collection()

    results = collection.get(
        where={
            "player": player_name
        }
    )

    return results.get(
        "metadatas",
        [],
    )


# =====================================================
# QUERY TYPE
# =====================================================

def is_match_query(query: str):

    q = normalize(query)

    teams = [
        team
        for team in TEAM_NAMES
        if team in q
    ]

    return len(teams) >= 2


def is_player_query(query: str):

    q = normalize(query)

    if any(
        word in q
        for word in STAT_KEYWORDS
    ):
        return True

    if re.search(
        r"20\d{2}",
        q,
    ):
        return True

    return False


# =====================================================
# MAIN DATAFRAME SEARCH
# =====================================================

def search_historical_stats_df(
    query: str,
    n_results: int = 25,
):

    q = normalize(query)

    # =================================================
    # PLAYER SEARCH
    # =================================================

    player_collection = get_player_collection()

    # -------------------------------------------------
    # IMPORTANT FIX:
    #
    # Previously we used:
    #
    #     collection.query(..., n_results=20)
    #
    # and attempted to identify the player from only
    # those 20 semantic results.
    #
    # That could fail even when the player existed in
    # the database.
    #
    # We now retrieve the complete metadata list for
    # reliable player-name detection.
    # -------------------------------------------------

    probe = player_collection.get(
        include=["metadatas"]
    )

    all_player_metadata = probe.get(
        "metadatas",
        [],
    )

    player_name = find_player(
        q,
        all_player_metadata,
    )

    # =================================================
    # PLAYER SEARCH
    # =================================================

    if player_name:

        # -------------------------------------------------
        # Retrieve the player's records directly.
        #
        # No semantic search is necessary once we know
        # the exact player name.
        # -------------------------------------------------

        metadata = get_player_records(
            player_name
        )

        if len(metadata) == 0:
            return "No player statistics found."

        # -------------------------------------------------
        # Filter by season/year if supplied
        # -------------------------------------------------

        year_match = re.search(
            r"(20\d{2})",
            q,
        )

        if year_match:

            year = int(
                year_match.group(1)
            )

            metadata = [
                row
                for row in metadata
                if row.get("season") == year
            ]

        if len(metadata) == 0:
            return "No player statistics found."

        # -------------------------------------------------
        # Sort records by season
        # -------------------------------------------------

        metadata = sorted(
            metadata,
            key=lambda x: x.get(
                "season",
                0,
            ),
        )

        # -------------------------------------------------
        # Build season table
        # -------------------------------------------------

        season_rows = []

        total_games = 0
        total_minutes = 0
        total_goals = 0
        total_assists = 0
        total_yellow = 0
        total_red = 0

        for row in metadata:

            games = row.get(
                "games",
                0,
            )

            minutes = row.get(
                "minutes",
                0,
            )

            goals = row.get(
                "goals",
                0,
            )

            assists = row.get(
                "assists",
                0,
            )

            yellow = row.get(
                "yellow_cards",
                0,
            )

            red = row.get(
                "red_cards",
                0,
            )

            total_games += games
            total_minutes += minutes
            total_goals += goals
            total_assists += assists
            total_yellow += yellow
            total_red += red

            season_rows.append(
                {
                    "Season": row.get(
                        "season",
                        "-",
                    ),
                    "Club": row.get(
                        "team",
                        "-",
                    ),
                    "Games": games,
                    "Minutes": minutes,
                    "Goals": goals,
                    "Assists": assists,
                    "Yellow Cards": yellow,
                    "Red Cards": red,
                }
            )

        # -------------------------------------------------
        # Career summary
        # -------------------------------------------------

        career_df = pd.DataFrame(
            [
                {
                    "Player": metadata[0].get(
                        "player",
                        player_name,
                    ),
                    "Games": total_games,
                    "Minutes": total_minutes,
                    "Goals": total_goals,
                    "Assists": total_assists,
                    "Yellow Cards": total_yellow,
                    "Red Cards": total_red,
                }
            ]
        )

        season_df = pd.DataFrame(
            season_rows
        )

        return {
            "career": career_df,
            "season": season_df,
        }

    # =================================================
    # HISTORICAL MATCH SEARCH
    # =================================================

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

        season = re.search(
            r"Season:\s*(.*?)\.",
            doc,
        )

        competition = re.search(
            r"Competition:\s*(.*?)\.",
            doc,
        )

        matchday = re.search(
            r"Matchday:\s*(.*?)\.",
            doc,
        )

        home = re.search(
            r"Home Team:\s*(.*?)\.",
            doc,
        )

        away = re.search(
            r"Away Team:\s*(.*?)\.",
            doc,
        )

        score = re.search(
            r"Score:\s*([0-9\-]+)",
            doc,
        )

        winner = re.search(
            r"Winner:\s*(.*?)\.",
            doc,
        )

        if not home or not away:
            continue

        home_team = normalize(
            home.group(1)
        )

        away_team = normalize(
            away.group(1)
        )

        # -------------------------------------------------
        # Two-team filtering
        # -------------------------------------------------

        if len(requested_teams) >= 2:

            if not (
                (
                    requested_teams[0] in home_team
                    and
                    requested_teams[1] in away_team
                )
                or
                (
                    requested_teams[1] in home_team
                    and
                    requested_teams[0] in away_team
                )
            ):
                continue

        # -------------------------------------------------
        # One-team filtering
        # -------------------------------------------------

        elif len(requested_teams) == 1:

            if (
                requested_teams[0]
                not in home_team
                and
                requested_teams[0]
                not in away_team
            ):
                continue

        rows.append(
            {
                "Season": (
                    season.group(1)
                    if season
                    else "-"
                ),

                "Competition": (
                    competition.group(1)
                    if competition
                    else "-"
                ),

                "Matchday": (
                    matchday.group(1).strip()
                    if matchday
                    else "-"
                ),

                "Home": (
                    home.group(1)
                    .replace(" FC", "")
                    if home
                    else "-"
                ),

                "Score": (
                    score.group(1)
                    if score
                    else "-"
                ),

                "Away": (
                    away.group(1)
                    .replace(" FC", "")
                    if away
                    else "-"
                ),

                "Winner": (
                    winner.group(1)
                    .replace(" FC", "")
                    if winner
                    else "-"
                ),
            }
        )

    if len(rows) == 0:
        return "No historical matches found."

    df = pd.DataFrame(rows)

    if "Season" in df.columns:

        df = df.sort_values(
            "Season"
        )

    return df


# =====================================================
# STRING VERSION FOR AGENT
# =====================================================

def search_historical_stats(
    query: str,
    n_results: int = 25,
) -> str:

    """
    Wrapper for the RAG agent.

    Notebook:
        search_historical_stats_df()

    Agent:
        search_historical_stats()

    Always returns a string.
    """

    result = search_historical_stats_df(
        query,
        n_results,
    )

    # =================================================
    # ERROR / NO DATA
    # =================================================

    if isinstance(result, str):

        return result

    # =================================================
    # PLAYER STATISTICS
    # =================================================

    if isinstance(result, dict):

        career_df = result["career"]

        season_df = result["season"]

        try:

            career = career_df.to_markdown(
                index=False
            )

            season = season_df.to_markdown(
                index=False
            )

        except Exception:

            career = career_df.to_string(
                index=False
            )

            season = season_df.to_string(
                index=False
            )

        return (
            "# PLAYER CAREER SUMMARY\n\n"
            f"{career}\n\n"
            "# PLAYER SEASON BREAKDOWN\n\n"
            f"{season}"
        )

    # =================================================
    # HISTORICAL MATCHES
    # =================================================

    if isinstance(
        result,
        pd.DataFrame,
    ):

        try:

            return result.to_markdown(
                index=False
            )

        except Exception:

            return result.to_string(
                index=False
            )

    # =================================================
    # FALLBACK
    # =================================================

    return str(result)