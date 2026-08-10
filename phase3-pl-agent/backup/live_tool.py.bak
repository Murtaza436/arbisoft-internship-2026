import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
BASE_URL = 'https://api.football-data.org/v4'

CACHE_DIR = 'data/cache'
CACHE_DURATION_HOURS = 1


def get_headers():
    if not API_KEY:
        return {}

    return {
        'X-Auth-Token': API_KEY
    }


def cache_key(endpoint: str) -> str:
    return (
        endpoint
        .replace('/', '_')
        .replace('?', '_')
        .replace('&', '_')
        .replace('=', '_')
        + '.json'
    )


def get_cached(endpoint: str):
    os.makedirs(CACHE_DIR, exist_ok=True)

    cache_file = os.path.join(
        CACHE_DIR,
        cache_key(endpoint)
    )

    if os.path.exists(cache_file):
        try:
            modified = datetime.fromtimestamp(
                os.path.getmtime(cache_file)
            )

            if (
                datetime.now() - modified
                < timedelta(hours=CACHE_DURATION_HOURS)
            ):
                with open(
                    cache_file,
                    'r',
                    encoding='utf-8'
                ) as f:
                    return json.load(f)

        except Exception:
            return None

    return None


def save_cache(endpoint: str, data: dict):
    os.makedirs(CACHE_DIR, exist_ok=True)

    cache_file = os.path.join(
        CACHE_DIR,
        cache_key(endpoint)
    )

    try:
        with open(
            cache_file,
            'w',
            encoding='utf-8'
        ) as f:
            json.dump(data, f)
    except Exception:
        pass


def api_get(endpoint: str) -> dict:
    if not API_KEY:
        return {
            'error': (
                'FOOTBALL_DATA_API_KEY is missing '
                'from the .env file.'
            )
        }

    cached = get_cached(endpoint)

    if cached is not None:
        return cached

    url = f'{BASE_URL}{endpoint}'

    try:
        response = requests.get(
            url,
            headers=get_headers(),
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            if data is None:
                return {
                    'error': 'API returned an empty response.'
                }

            save_cache(endpoint, data)
            return data

        return {
            'error': (
                f'API returned HTTP '
                f'{response.status_code}: '
                f'{response.text[:300]}'
            )
        }

    except requests.RequestException as e:
        return {
            'error': f'Network/API request failed: {str(e)}'
        }

    except Exception as e:
        return {
            'error': f'Unexpected API error: {str(e)}'
        }


def get_standings() -> str:
    data = api_get('/competitions/PL/standings')

    if not data:
        return 'Could not fetch standings: API returned no data.'

    if 'error' in data:
        return f'Could not fetch standings: {data["error"]}'

    try:
        season = data.get('season') or {}

        start_date = season.get('startDate') or ''
        end_date = season.get('endDate') or ''

        season_str = (
            f'{start_date[:4]}-{end_date[:4]}'
            if start_date and end_date
            else 'Current Season'
        )

        standings_list = data.get('standings') or []

        if not standings_list:
            return 'No standings data was returned by the API.'

        table = standings_list[0].get('table') or []

        if not table:
            return 'The standings table is empty.'

        lines = [
            f'Premier League Standings {season_str}:\n'
        ]

        for team in table[:20]:
            team_data = team.get('team') or {}

            lines.append(
                f'{team.get("position", "N/A")}. '
                f'{team_data.get("name", "Unknown Team")} | '
                f'Pts: {team.get("points", 0)} | '
                f'P: {team.get("playedGames", 0)} '
                f'W: {team.get("won", 0)} '
                f'D: {team.get("draw", 0)} '
                f'L: {team.get("lost", 0)} | '
                f'GD: {team.get("goalDifference", 0)}'
            )

        return '\n'.join(lines)

    except Exception as e:
        return f'Error parsing standings: {str(e)}'


def get_top_scorers() -> str:
    data = api_get(
    '/competitions/PL/scorers?season=2025&limit=10'
    )
    if not data:
        return 'Could not fetch scorers: API returned no data.'

    if 'error' in data:
        return f'Could not fetch scorers: {data["error"]}'

    try:
        scorers = data.get('scorers') or []

        if not scorers:
            return 'No top scorer data was returned.'

        lines = [
            'Premier League Top Scorers '
            '(2025-26 Season):\n'
        ]

        for i, scorer in enumerate(scorers, 1):
            player = scorer.get('player') or {}
            team = scorer.get('team') or {}

            lines.append(
                f'{i}. '
                f'{player.get("name", "Unknown Player")} '
                f'({team.get("name", "Unknown Team")}) | '
                f'Goals: {scorer.get("goals", 0)} | '
                f'Assists: {scorer.get("assists", 0)}'
            )

        return '\n'.join(lines)

    except Exception as e:
        return f'Error parsing scorers: {str(e)}'


def get_recent_results() -> str:
    data = api_get(
        '/competitions/PL/matches?season=2025&status=FINISHED&limit=10'
    )

    if not data:
        return 'Could not fetch results: API returned no data.'

    if 'error' in data:
        return f'Could not fetch results: {data["error"]}'

    try:
        matches = data.get('matches') or []

        if not matches:
            return 'No recent results were returned.'

        lines = [
            'Recent Premier League Results:\n'
        ]

        for match in matches[-10:]:
            home_team = match.get('homeTeam') or {}
            away_team = match.get('awayTeam') or {}
            score = match.get('score') or {}
            full_time = score.get('fullTime') or {}

            lines.append(
                f'{(match.get("utcDate") or "")[:10]}: '
                f'{home_team.get("name", "Unknown")} '
                f'{full_time.get("home", 0)} - '
                f'{full_time.get("away", 0)} '
                f'{away_team.get("name", "Unknown")}'
            )

        return '\n'.join(lines)

    except Exception as e:
        return f'Error parsing results: {str(e)}'


def get_upcoming_fixtures() -> str:
    data = api_get(
        '/competitions/PL/matches?status=SCHEDULED&limit=10'
    )

    if not data:
        return 'Could not fetch fixtures: API returned no data.'

    if 'error' in data:
        return f'Could not fetch fixtures: {data["error"]}'

    try:
        matches = data.get('matches') or []

        if not matches:
            return 'No upcoming fixtures were returned.'

        lines = [
            'Upcoming Premier League Fixtures:\n'
        ]

        for match in matches[:10]:
            home_team = match.get('homeTeam') or {}
            away_team = match.get('awayTeam') or {}

            lines.append(
                f'{(match.get("utcDate") or "")[:10]}: '
                f'{home_team.get("name", "Unknown")} vs '
                f'{away_team.get("name", "Unknown")}'
            )

        return '\n'.join(lines)

    except Exception as e:
        return f'Error parsing fixtures: {str(e)}'


def get_team_matches(team_name: str) -> str:
    if not team_name or not team_name.strip():
        return 'Please provide a team name.'

    data = api_get(
        '/competitions/PL/matches?limit=50'
    )

    if not data:
        return 'Could not fetch matches: API returned no data.'

    if 'error' in data:
        return f'Could not fetch matches: {data["error"]}'

    try:
        matches = data.get('matches') or []

        team_name_lower = team_name.lower()

        team_matches = []

        for match in matches:
            home_team = match.get('homeTeam') or {}
            away_team = match.get('awayTeam') or {}

            home_name = home_team.get('name', '')
            away_name = away_team.get('name', '')

            if (
                team_name_lower in home_name.lower()
                or team_name_lower in away_name.lower()
            ):
                team_matches.append(match)

        if not team_matches:
            return f'No matches found for {team_name}'

        lines = [
            f'Matches for {team_name}:\n'
        ]

        for match in team_matches[:10]:
            home_team = match.get('homeTeam') or {}
            away_team = match.get('awayTeam') or {}

            home = home_team.get('name', 'Unknown')
            away = away_team.get('name', 'Unknown')

            date = (
                match.get('utcDate') or ''
            )[:10]

            status = match.get(
                'status',
                'UNKNOWN'
            )

            if status == 'FINISHED':
                score = match.get('score') or {}
                full_time = score.get(
                    'fullTime'
                ) or {}

                hs = full_time.get(
                    'home',
                    0
                )

                aws = full_time.get(
                    'away',
                    0
                )

                lines.append(
                    f'{date}: '
                    f'{home} {hs}-{aws} {away}'
                )

            else:
                lines.append(
                    f'{date}: '
                    f'{home} vs {away} '
                    f'({status})'
                )

        return '\n'.join(lines)

    except Exception as e:
        return f'Error: {str(e)}'
