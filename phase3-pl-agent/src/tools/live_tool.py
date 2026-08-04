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
CURRENT_SEASON = 2025


def get_headers():
    return {'X-Auth-Token': API_KEY}


def cache_key(endpoint: str) -> str:
    return endpoint.replace('/', '_').replace('?', '_') + '.json'


def get_cached(endpoint: str):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, cache_key(endpoint))
    if os.path.exists(cache_file):
        modified = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - modified < timedelta(hours=CACHE_DURATION_HOURS):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None


def save_cache(endpoint: str, data: dict):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, cache_key(endpoint))
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def api_get(endpoint: str) -> dict:
    cached = get_cached(endpoint)
    if cached:
        return cached
    url = f'{BASE_URL}{endpoint}'
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        data = response.json()
        save_cache(endpoint, data)
        return data
    return {'error': f'API returned {response.status_code}: {response.text[:200]}'}


def get_standings() -> str:
    data = api_get(f'/competitions/PL/standings?season={CURRENT_SEASON}')
    if 'error' in data:
        return f'Could not fetch standings: {data["error"]}'
    try:
        season = data.get('season', {})
        start = season.get('startDate', '')[:4]
        end = season.get('endDate', '')[:4]
        season_str = f"{start}-{end}"
        standings = data['standings'][0]['table']
        lines = [f'Premier League Standings {season_str}:\n']
        for team in standings[:20]:
            pos = team['position']
            name = team['team']['name']
            pts = team['points']
            played = team['playedGames']
            won = team['won']
            drawn = team['draw']
            lost = team['lost']
            gd = team['goalDifference']
            lines.append(
                f'{pos}. {name} | Pts: {pts} | '
                f'P:{played} W:{won} D:{drawn} L:{lost} | GD:{gd}'
            )
        return '\n'.join(lines)
    except Exception as e:
        return f'Error parsing standings: {str(e)}'


def get_top_scorers() -> str:
    data = api_get(f'/competitions/PL/scorers?season={CURRENT_SEASON}&limit=10')
    if 'error' in data:
        return f'Could not fetch scorers: {data["error"]}'
    try:
        scorers = data.get('scorers', [])
        if not scorers:
            return 'No scorers data available for this season.'
        lines = ['Premier League Top Scorers 2025-26:\n']
        for i, scorer in enumerate(scorers, 1):
            player = scorer['player']['name']
            team = scorer['team']['name']
            goals = scorer.get('goals', 0) or 0
            assists = scorer.get('assists', 0) or 0
            lines.append(
                f'{i}. {player} ({team}) | '
                f'Goals: {goals} | Assists: {assists}'
            )
        return '\n'.join(lines)
    except Exception as e:
        return f'Error parsing scorers: {str(e)}'


def get_recent_results() -> str:
    data = api_get(
        f'/competitions/PL/matches?season={CURRENT_SEASON}&status=FINISHED'
    )
    if 'error' in data:
        return f'Could not fetch results: {data["error"]}'
    try:
        matches = data.get('matches', [])
        if not matches:
            return 'No finished matches found for 2025-26 season.'
        recent = matches[-10:]
        lines = ['Recent Premier League Results 2025-26:\n']
        for match in recent:
            home = match['homeTeam']['name']
            away = match['awayTeam']['name']
            hs = match['score']['fullTime']['home']
            aws = match['score']['fullTime']['away']
            date = match['utcDate'][:10]
            lines.append(f'{date}: {home} {hs} - {aws} {away}')
        return '\n'.join(lines)
    except Exception as e:
        return f'Error parsing results: {str(e)}'


def get_upcoming_fixtures() -> str:
    data = api_get(
        f'/competitions/PL/matches?season={CURRENT_SEASON}&status=SCHEDULED'
    )
    if 'error' in data:
        return f'Could not fetch fixtures: {data["error"]}'
    try:
        matches = data.get('matches', [])
        if not matches:
            return 'No upcoming fixtures found. Season may not have started yet.'
        lines = ['Upcoming Premier League Fixtures 2025-26:\n']
        for match in matches[:10]:
            home = match['homeTeam']['name']
            away = match['awayTeam']['name']
            date = match['utcDate'][:10]
            lines.append(f'{date}: {home} vs {away}')
        return '\n'.join(lines)
    except Exception as e:
        return f'Error parsing fixtures: {str(e)}'


def get_team_matches(team_name: str) -> str:
    data = api_get(
        f'/competitions/PL/matches?season={CURRENT_SEASON}'
    )
    if 'error' in data:
        return f'Could not fetch matches: {data["error"]}'
    try:
        matches = data.get('matches', [])
        team_matches = [
            m for m in matches
            if team_name.lower() in m['homeTeam']['name'].lower()
            or team_name.lower() in m['awayTeam']['name'].lower()
        ]
        if not team_matches:
            return f'No matches found for {team_name} in 2025-26 season.'
        lines = [f'Matches for {team_name} (2025-26):\n']
        for match in team_matches[:10]:
            home = match['homeTeam']['name']
            away = match['awayTeam']['name']
            date = match['utcDate'][:10]
            status = match['status']
            if status == 'FINISHED':
                hs = match['score']['fullTime']['home']
                aws = match['score']['fullTime']['away']
                lines.append(f'{date}: {home} {hs}-{aws} {away}')
            else:
                lines.append(f'{date}: {home} vs {away} ({status})')
        return '\n'.join(lines)
    except Exception as e:
        return f'Error: {str(e)}'
