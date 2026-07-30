import pytest
from unittest.mock import patch, MagicMock
from src.tools.search_tool import brave_search
from src.tools.live_tool import get_standings, get_top_scorers


def test_brave_search_no_key():
    with patch.dict('os.environ', {'BRAVE_API_KEY': ''}):
        result = brave_search('Premier League')
        assert 'not found' in result.lower() or 'key' in result.lower()


def test_get_standings_returns_string():
    with patch('src.tools.live_tool.api_get') as mock_api:
        mock_api.return_value = {
            'season': {'startDate': '2025-08-01', 'endDate': '2026-05-31'},
            'standings': [{
                'table': [{
                    'position': 1,
                    'team': {'name': 'Arsenal'},
                    'points': 75,
                    'playedGames': 35,
                    'won': 23,
                    'draw': 6,
                    'lost': 6,
                    'goalDifference': 42,
                }]
            }]
        }
        result = get_standings()
        assert 'Arsenal' in result
        assert 'Standings' in result


def test_get_top_scorers_returns_string():
    with patch('src.tools.live_tool.api_get') as mock_api:
        mock_api.return_value = {
            'scorers': [{
                'player': {'name': 'Erling Haaland'},
                'team': {'name': 'Manchester City'},
                'goals': 28,
                'assists': 5,
            }]
        }
        result = get_top_scorers()
        assert 'Haaland' in result
        assert 'Goals' in result
