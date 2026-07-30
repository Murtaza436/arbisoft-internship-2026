from src.tools.rag_tool import search_historical_stats
from src.tools.live_tool import (
    get_standings,
    get_top_scorers,
    get_recent_results,
    get_upcoming_fixtures,
    get_team_matches,
)
from src.tools.search_tool import brave_search

TOOL_MAP = {
    'search_historical_stats': search_historical_stats,
    'get_standings': get_standings,
    'get_top_scorers': get_top_scorers,
    'get_recent_results': get_recent_results,
    'get_upcoming_fixtures': get_upcoming_fixtures,
    'get_team_matches': get_team_matches,
    'brave_search': brave_search,
}

TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'search_historical_stats',
            'description': (
                'Search historical Premier League player statistics from '
                '2015-16 to 2022-23 seasons. Use for questions about specific '
                'player performance, goals, assists, shots in past seasons.'
            ),
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The search query about historical player stats.',
                    }
                },
                'required': ['query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_standings',
            'description': (
                'Get current Premier League standings and table. '
                'Use for questions about current league position, points, '
                'who is top of the table right now.'
            ),
            'parameters': {'type': 'object', 'properties': {}, 'required': []},
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_top_scorers',
            'description': (
                'Get current Premier League top scorers this season. '
                'Use for questions about who is leading scorer right now.'
            ),
            'parameters': {'type': 'object', 'properties': {}, 'required': []},
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_recent_results',
            'description': (
                'Get recent Premier League match results. '
                'Use for questions about recent scores and results.'
            ),
            'parameters': {'type': 'object', 'properties': {}, 'required': []},
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_upcoming_fixtures',
            'description': (
                'Get upcoming Premier League fixtures. '
                'Use for questions about when teams play next.'
            ),
            'parameters': {'type': 'object', 'properties': {}, 'required': []},
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_team_matches',
            'description': (
                'Get matches for a specific Premier League team. '
                'Use when asking about a particular club results or fixtures.'
            ),
            'parameters': {
                'type': 'object',
                'properties': {
                    'team_name': {
                        'type': 'string',
                        'description': 'The name of the Premier League team.',
                    }
                },
                'required': ['team_name'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'brave_search',
            'description': (
                'Search the web for Premier League news, transfers, injuries, '
                'manager news, or any information not available in stats or live data.'
            ),
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The search query.',
                    }
                },
                'required': ['query'],
            },
        },
    },
]
