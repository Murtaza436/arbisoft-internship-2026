import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

CACHE_DIR = "data/cache"
CACHE_DURATION_HOURS = 1
CURRENT_SEASON = 2025


def get_headers():
    if not API_KEY:
        return {}
    return {"X-Auth-Token": API_KEY}


def cache_key(endpoint: str):
    return (
        endpoint.replace("/", "_")
        .replace("?", "_")
        .replace("&", "_")
        .replace("=", "_")
        + ".json"
    )


def get_cached(endpoint: str):
    os.makedirs(CACHE_DIR, exist_ok=True)

    filename = os.path.join(CACHE_DIR, cache_key(endpoint))

    if not os.path.exists(filename):
        return None

    try:
        modified = datetime.fromtimestamp(os.path.getmtime(filename))

        if datetime.now() - modified > timedelta(hours=CACHE_DURATION_HOURS):
            return None

        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return None


def save_cache(endpoint: str, data: dict):
    os.makedirs(CACHE_DIR, exist_ok=True)

    filename = os.path.join(CACHE_DIR, cache_key(endpoint))

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def api_get(endpoint: str):

    if not API_KEY:
        return {"error": "FOOTBALL_DATA_API_KEY missing"}

    cached = get_cached(endpoint)

    if cached is not None:
        return cached

    try:
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=get_headers(),
            timeout=15,
        )

        if response.status_code != 200:
            return {
                "error": f"HTTP {response.status_code}: {response.text[:250]}"
            }

        data = response.json()

        save_cache(endpoint, data)

        return data

    except Exception as e:
        return {"error": str(e)}


# ===========================================================
# CURRENT STANDINGS
# ===========================================================

def get_standings():

    data = api_get("/competitions/PL/standings")

    if "error" in data:
        return f"Could not fetch standings.\n{data['error']}"

    try:

        table = data["standings"][0]["table"]

        season = data.get("season", {})

        season_string = (
            f"{season.get('startDate','')[:4]}-{season.get('endDate','')[:4]}"
        )

        output = [
            f"# Premier League Standings ({season_string})",
            ""
        ]

        for club in table:

            output.append(
                f"{club['position']}. "
                f"{club['team']['name']} | "
                f"Pts {club['points']} | "
                f"P {club['playedGames']} | "
                f"W {club['won']} | "
                f"D {club['draw']} | "
                f"L {club['lost']} | "
                f"GD {club['goalDifference']}"
            )

        return "\n".join(output)

    except Exception as e:
        return f"Error parsing standings: {e}"


# ===========================================================
# TOP SCORERS
# ===========================================================

def get_top_scorers():

    data = api_get(
        "/competitions/PL/scorers?season=2025&limit=10"
    )

    if "error" in data:
        return f"Could not fetch top scorers.\n{data['error']}"

    try:

        scorers = data.get("scorers", [])

        if not scorers:
            return "No top scorer data was returned."

        output = [
            "# Premier League Top Scorers (2025-26)",
            ""
        ]

        for i, scorer in enumerate(scorers, start=1):

            player = scorer.get("player", {})
            team = scorer.get("team", {})

            output.append(
                f"""## {i}. {player.get('name','Unknown')}

Club: {team.get('name','Unknown')}

Goals: {scorer.get('goals',0)}

Assists: {scorer.get('assists',0)}
"""
            )

        return "\n".join(output)

    except Exception as e:
        return f"Error parsing scorers: {e}"
    
# ===========================================================
# RECENT RESULTS
# ===========================================================

def get_recent_results():

    data = api_get(
        "/competitions/PL/matches?season=2025&status=FINISHED&limit=10"
    )

    if "error" in data:
        return f"Could not fetch results.\n{data['error']}"

    try:

        matches = data.get("matches", [])

        if not matches:
            return "No recent results were returned."

        output = ["# Recent Premier League Results", ""]

        for match in matches[-10:]:

            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            score = match["score"]["fullTime"]

            hs = score["home"]
            aws = score["away"]

            if hs > aws:
                result = f"{home} won"
            elif aws > hs:
                result = f"{away} won"
            else:
                result = "Draw"

            date = (match.get("utcDate") or "")[:10]

            output.append(
                f"""### {date}

{home} {hs}-{aws} {away}

Result: {result}
"""
            )

        return "\n".join(output)

    except Exception as e:
        return f"Error parsing recent results: {e}"


# ===========================================================
# UPCOMING FIXTURES
# ===========================================================

def get_upcoming_fixtures():

    data = api_get(
        "/competitions/PL/matches?status=SCHEDULED&limit=10"
    )

    if "error" in data:
        return f"Could not fetch fixtures.\n{data['error']}"

    try:

        matches = data.get("matches", [])

        if not matches:
            return "No upcoming fixtures were returned."

        output = ["# Upcoming Premier League Fixtures", ""]

        for match in matches[:10]:

            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            date = (match.get("utcDate") or "")[:10]

            output.append(
                f"""### {date}

{home}

vs

{away}
"""
            )

        return "\n".join(output)

    except Exception as e:
        return f"Error parsing fixtures: {e}"


# ===========================================================
# TEAM MATCHES
# ===========================================================

def get_team_matches(team_name: str):

    if not team_name.strip():
        return "Please provide a team name."

    data = api_get("/competitions/PL/matches?limit=50")

    if "error" in data:
        return f"Could not fetch team matches.\n{data['error']}"

    try:

        matches = data.get("matches", [])

        output = [
            f"# Matches for {team_name}",
            ""
        ]

        found = False

        for match in matches:

            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            if (
                team_name.lower() not in home.lower()
                and team_name.lower() not in away.lower()
            ):
                continue

            found = True

            date = (match.get("utcDate") or "")[:10]
            status = match.get("status", "")

            if status == "FINISHED":

                score = match["score"]["fullTime"]

                hs = score["home"]
                aws = score["away"]

                output.append(
                    f"""### {date}

{home} {hs}-{aws} {away}
"""
                )

            else:

                output.append(
                    f"""### {date}

{home}

vs

{away}

Status: {status}
"""
                )

        if not found:
            return f"No matches found for {team_name}."

        return "\n".join(output)

    except Exception as e:
        return f"Error parsing team matches: {e}"