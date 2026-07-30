import os
import json


def get_competition_id(data_path: str) -> list:
    competitions_file = os.path.join(data_path, 'data', 'competitions.json')
    if not os.path.exists(competitions_file):
        return []
    with open(competitions_file, 'r', encoding='utf-8') as f:
        competitions = json.load(f)
    pl_seasons = [
        c for c in competitions
        if c.get('competition_name') == 'Premier League'
        and int(c.get('season_name', '0').split('/')[0]) >= 2015
    ]
    return pl_seasons


def load_matches(data_path: str, competition_id: int, season_id: int) -> list:
    matches_file = os.path.join(
        data_path, 'data', 'matches',
        str(competition_id), f'{season_id}.json'
    )
    if not os.path.exists(matches_file):
        return []
    with open(matches_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_events(data_path: str, match_id: int) -> list:
    events_file = os.path.join(
        data_path, 'data', 'events', f'{match_id}.json'
    )
    if not os.path.exists(events_file):
        return []
    with open(events_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_player_stats(match: dict, events: list) -> list:
    home_team = match.get('home_team', {}).get('home_team_name', '')
    away_team = match.get('away_team', {}).get('away_team_name', '')
    match_date = match.get('match_date', '')
    season = match.get('season', {}).get('season_name', '')
    home_score = match.get('home_score', 0)
    away_score = match.get('away_score', 0)

    player_stats = {}

    for event in events:
        player = event.get('player', {})
        if not player:
            continue
        player_id = player.get('id')
        player_name = player.get('name', '')
        team_name = event.get('team', {}).get('name', '')

        if player_id not in player_stats:
            opponent = away_team if team_name == home_team else home_team
            player_stats[player_id] = {
                'player_name': player_name,
                'team': team_name,
                'opponent': opponent,
                'match_date': match_date,
                'season': season,
                'home_score': home_score,
                'away_score': away_score,
                'goals': 0,
                'assists': 0,
                'shots': 0,
                'shots_on_target': 0,
                'passes_completed': 0,
                'minutes_played': 0,
            }

        event_type = event.get('type', {}).get('name', '')

        if event_type == 'Shot':
            player_stats[player_id]['shots'] += 1
            outcome = event.get('shot', {}).get('outcome', {}).get('name', '')
            if outcome == 'Goal':
                player_stats[player_id]['goals'] += 1
            if outcome in ['Goal', 'Saved', 'Saved to Post']:
                player_stats[player_id]['shots_on_target'] += 1

        elif event_type == 'Pass':
            pass_data = event.get('pass', {})
            outcome = pass_data.get('outcome', {})
            if not outcome:
                player_stats[player_id]['passes_completed'] += 1
            goal_assist = pass_data.get('goal_assist', False)
            if goal_assist:
                player_stats[player_id]['assists'] += 1

    for player_id, stats in player_stats.items():
        stats['minutes_played'] = min(90, stats.get('minutes_played', 90))

    return list(player_stats.values())


def stats_to_text(stats: dict) -> str:
    return (
        f"{stats['player_name']} | "
        f"{stats['team']} vs {stats['opponent']} | "
        f"{stats['match_date']} | "
        f"Season: {stats['season']} | "
        f"Goals: {stats['goals']} | "
        f"Assists: {stats['assists']} | "
        f"Shots: {stats['shots']} | "
        f"Shots on Target: {stats['shots_on_target']} | "
        f"Passes Completed: {stats['passes_completed']} | "
        f"Minutes: {stats['minutes_played']} | "
        f"Score: {stats['team']} "
        f"{stats['home_score']}-{stats['away_score']} {stats['opponent']}"
    )
