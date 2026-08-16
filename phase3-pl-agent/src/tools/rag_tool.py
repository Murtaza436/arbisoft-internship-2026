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
    set(
        list(TEAM_ALIASES.values())
        + STANDARD_TEAMS
    )
)


# =====================================================
# STAT KEYWORDS
# =====================================================

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
# TOP SCORER KEYWORDS
# =====================================================

TOP_SCORER_KEYWORDS = [
    "top scorer",
    "top scorers",
    "top scoring",
    "leading scorer",
    "leading scorers",
    "leading goal scorer",
    "leading goal scorers",
    "most goals",
    "highest goals",
    "highest goal scorer",
    "highest goal scorers",
    "golden boot",
    "golden boot winner",
    "who scored the most",
    "who has the most goals",
]


# =====================================================
# TEXT NORMALIZATION
# =====================================================

def normalize(text: str) -> str:
    """
    Normalize text and common team aliases.
    """

    text = str(text).lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
    )

    for old, new in TEAM_ALIASES.items():
        text = text.replace(
            old,
            new,
        )

    return " ".join(text.split())


# =====================================================
# YEAR / SEASON DETECTION
# =====================================================

def extract_year(query: str):
    """
    Extract a four-digit year from a query.

    Example:
        'top scorer 2021'
        -> 2021
    """

    match = re.search(
        r"\b(20\d{2})\b",
        query,
    )

    if match:
        return int(match.group(1))

    return None


def extract_season(query: str):
    """
    Extract a season written as:

        2020-21
        2021-22
        2019/20

    Returns the starting year.

    Example:
        'top scorer 2020-21'
        -> 2020
    """

    match = re.search(
        r"\b(20\d{2})[-/](\d{2})\b",
        query,
    )

    if match:
        return int(match.group(1))

    return None


# =====================================================
# TOP SCORER DETECTION
# =====================================================

def is_top_scorer_query(query: str) -> bool:
    """
    Detect leaderboard/top-scorer questions.
    """

    q = normalize(query)

    return any(
        phrase in q
        for phrase in TOP_SCORER_KEYWORDS
    )


# =====================================================
# PLAYER DETECTION
# =====================================================

def find_player(
    query: str,
    metadata,
):
    """
    Detect a player using:

    1. Full name
    2. First name + surname
    3. Unique surname
    4. Fuzzy matching
    """

    if not metadata:
        return None

    names = sorted(
        {
            m["player"]
            for m in metadata
            if m.get("player")
        }
    )

    q = normalize(query)

    q_words = set(
        q.split()
    )

    # -------------------------------------------------
    # Exact full name
    # -------------------------------------------------

    for name in names:

        if normalize(name) in q:

            return name

    # -------------------------------------------------
    # First name + surname
    # -------------------------------------------------

    for name in names:

        name_words = normalize(
            name
        ).split()

        if len(name_words) >= 2:

            first_name = name_words[0]
            surname = name_words[-1]

            if (
                first_name in q_words
                and surname in q_words
            ):

                return name

    # -------------------------------------------------
    # Unique surname
    # -------------------------------------------------

    surname_matches = []

    for name in names:

        surname = (
            normalize(name)
            .split()[-1]
        )

        if surname in q_words:

            surname_matches.append(
                name
            )

    if len(surname_matches) == 1:

        return surname_matches[0]

    # -------------------------------------------------
    # Fuzzy matching
    # -------------------------------------------------

    query_words = [
        word
        for word in q.split()
        if word not in STAT_KEYWORDS
        and word not in TOP_SCORER_KEYWORDS
    ]

    player_query = " ".join(
        query_words
    ).strip()

    if player_query:

        matches = difflib.get_close_matches(
            player_query,
            [
                normalize(name)
                for name in names
            ],
            n=1,
            cutoff=0.65,
        )

        if matches:

            matched = matches[0]

            for name in names:

                if normalize(name) == matched:

                    return name

    return None


# =====================================================
# PLAYER RECORD RETRIEVAL
# =====================================================

def get_player_records(
    player_name: str,
):
    """
    Retrieve all records belonging to
    one specific player using metadata.
    """

    collection = get_player_collection()

    results = collection.get(
        where={
            "player": player_name
        },
        include=[
            "metadatas"
        ],
    )

    return results.get(
        "metadatas",
        [],
    )


# =====================================================
# TOP SCORER SEARCH
# =====================================================

def search_top_scorers(
    query: str,
    n_results: int = 10,
):
    """
    Find the highest-scoring players for a
    requested season.

    This MUST happen before normal player
    or historical match search.
    """

    collection = get_player_collection()

    # -------------------------------------------------
    # Determine requested season
    # -------------------------------------------------

    season = extract_season(query)

    if season is None:

        year = extract_year(query)

        if year is None:

            return (
                "Please specify a Premier League "
                "season or year."
            )

        # ---------------------------------------------
        # Interpret a plain year as the season
        # beginning in that year.
        #
        # Example:
        # 2021 -> 2021-22 dataset
        #
        # If your dataset instead stores 2021
        # for 2020-21, change this mapping.
        # ---------------------------------------------

        season = year

    # -------------------------------------------------
    # Retrieve complete player metadata
    # -------------------------------------------------

    results = collection.get(
        include=[
            "metadatas"
        ],
    )

    metadata = results.get(
        "metadatas",
        [],
    )

    if not metadata:

        return "No player statistics found."

    # -------------------------------------------------
    # Filter season
    # -------------------------------------------------

    season_rows = [
        row
        for row in metadata
        if row.get("season") == season
    ]

    if not season_rows:

        return (
            f"No player statistics found for "
            f"season {season}."
        )

    # -------------------------------------------------
    # Build dataframe
    # -------------------------------------------------

    rows = []

    for row in season_rows:

        rows.append(
            {
                "Player": row.get(
                    "player",
                    "-",
                ),
                "Team": row.get(
                    "team",
                    "-",
                ),
                "Games": row.get(
                    "games",
                    0,
                ),
                "Minutes": row.get(
                    "minutes",
                    0,
                ),
                "Goals": row.get(
                    "goals",
                    0,
                ),
                "Assists": row.get(
                    "assists",
                    0,
                ),
                "Yellow Cards": row.get(
                    "yellow_cards",
                    0,
                ),
                "Red Cards": row.get(
                    "red_cards",
                    0,
                ),
            }
        )

    df = pd.DataFrame(
        rows
    )

    if df.empty:

        return "No player statistics found."

    # -------------------------------------------------
    # Sort by goals
    # -------------------------------------------------

    df = df.sort_values(
        [
            "Goals",
            "Assists",
        ],
        ascending=[
            False,
            False,
        ],
    )

    # -------------------------------------------------
    # Return top players
    # -------------------------------------------------

    return df.head(
        n_results
    ).reset_index(
        drop=True
    )


# =====================================================
# QUERY TYPE
# =====================================================

def is_match_query(
    query: str,
):

    q = normalize(query)

    teams = [
        team
        for team in TEAM_NAMES
        if team in q
    ]

    return len(teams) >= 2


def is_player_query(
    query: str,
):

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
    # 1. TOP SCORER / LEADERBOARD QUERY
    # =================================================

    if is_top_scorer_query(q):

        return search_top_scorers(
            q,
            n_results=n_results,
        )

    # =================================================
    # 2. PLAYER SEARCH
    # =================================================

    player_collection = get_player_collection()

    # Get all player metadata so that a player is not
    # missed because semantic search ranked their record
    # too low.

    probe = player_collection.get(
        include=[
            "metadatas"
        ],
    )

    all_player_metadata = probe.get(
        "metadatas",
        [],
    )

    player_name = find_player(
        q,
        all_player_metadata,
    )

    if player_name:

        metadata = get_player_records(
            player_name
        )

        if not metadata:

            return (
                "No player statistics found."
            )

        # -------------------------------------------------
        # Season filter
        # -------------------------------------------------

        requested_season = extract_season(
            q
        )

        if requested_season is None:

            requested_season = extract_year(
                q
            )

        if requested_season is not None:

            metadata = [
                row
                for row in metadata
                if row.get(
                    "season"
                ) == requested_season
            ]

        if not metadata:

            return (
                "No player statistics found."
            )

        # -------------------------------------------------
        # Sort by season
        # -------------------------------------------------

        metadata = sorted(
            metadata,
            key=lambda x: x.get(
                "season",
                0,
            ),
        )

        # -------------------------------------------------
        # Build season rows
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
    # 3. HISTORICAL MATCH SEARCH
    # =================================================

    collection = get_collection()

    results = collection.query(
        query_texts=[
            q
        ],
        n_results=n_results,
    )

    docs = results.get(
        "documents",
        [[]],
    )[0]

    if not docs:

        return (
            "No historical matches found."
        )

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

            team_a = requested_teams[0]
            team_b = requested_teams[1]

            valid_match = (
                (
                    team_a in home_team
                    and
                    team_b in away_team
                )
                or
                (
                    team_b in home_team
                    and
                    team_a in away_team
                )
            )

            if not valid_match:

                continue

        # -------------------------------------------------
        # One-team filtering
        # -------------------------------------------------

        elif len(requested_teams) == 1:

            team = requested_teams[0]

            if (
                team not in home_team
                and
                team not in away_team
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
                    .replace(
                        " FC",
                        "",
                    )
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
                    .replace(
                        " FC",
                        "",
                    )
                    if away
                    else "-"
                ),

                "Winner": (
                    winner.group(1)
                    .replace(
                        " FC",
                        "",
                    )
                    if winner
                    else "-"
                ),
            }
        )

    if not rows:

        return (
            "No historical matches found."
        )

    df = pd.DataFrame(
        rows
    )

    if "Season" in df.columns:

        df = df.sort_values(
            "Season"
        )

    return df.reset_index(
        drop=True
    )


# =====================================================
# STRING VERSION FOR AGENT
# =====================================================

def search_historical_stats(
    query: str,
    n_results: int = 25,
) -> str:

    """
    Wrapper used by the agent.

    Dataframe mode:
        search_historical_stats_df()

    Agent mode:
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

    if isinstance(
        result,
        str,
    ):

        return result

    # =================================================
    # TOP SCORER DATAFRAME
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
    # PLAYER STATISTICS
    # =================================================

    if isinstance(
        result,
        dict,
    ):

        career_df = result[
            "career"
        ]

        season_df = result[
            "season"
        ]

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
    # FALLBACK
    # =================================================

    return str(
        result
    )