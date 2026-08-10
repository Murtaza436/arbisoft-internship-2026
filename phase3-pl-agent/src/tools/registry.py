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
    "search_historical_stats": search_historical_stats,
    "get_standings": get_standings,
    "get_top_scorers": get_top_scorers,
    "get_recent_results": get_recent_results,
    "get_upcoming_fixtures": get_upcoming_fixtures,
    "get_team_matches": get_team_matches,
    "brave_search": brave_search,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_historical_stats",
            "description": (
                "Search the historical Premier League database. "
                "Use this for ANY historical question about matches or players. "
                "Includes Premier League matches from OpenFootball (2015 onwards) "
                "and player season statistics from the local dataset (2014-2024). "
                "Examples: "
                "'How many goals did Harry Kane score?', "
                "'Mohamed Salah assists 2021', "
                "'Liverpool vs Arsenal 2019', "
                "'Manchester United results 2018', "
                "'Kevin De Bruyne yellow cards', "
                "'Erling Haaland career stats'. "
                "Do NOT use this for current standings, current fixtures or today's news."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Historical football query.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_standings",
            "description": (
                "Return the CURRENT Premier League standings only. "
                "Use for league table, rankings, positions, points, "
                "top four, relegation zone and similar questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_scorers",
            "description": (
                "Return the CURRENT Premier League Golden Boot table. "
                "Use ONLY when the user asks about this season's top scorers, "
                "leading goalscorers or current scoring rankings."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_results",
            "description": (
                "Return the latest completed Premier League matches. "
                "Use for latest scores, recent results, last games or "
                "'who won yesterday?'."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_fixtures",
            "description": (
                "Return upcoming Premier League fixtures. "
                "Use for next matches, upcoming games and future fixtures."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_matches",
            "description": (
                "Return fixtures and results for ONE specific Premier League club. "
                "Examples: "
                "'Liverpool next matches', "
                "'Chelsea fixtures', "
                "'Arsenal recent games'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team_name": {
                        "type": "string",
                        "description": "Premier League team name.",
                    }
                },
                "required": ["team_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "brave_search",
            "description": (
                "Search the live web for football news. "
                "Use ONLY for transfers, injuries, manager news, "
                "press conferences, rumours or breaking football news. "
                "Do NOT use this for historical statistics or league tables."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Football news search query.",
                    }
                },
                "required": ["query"],
            },
        },
    },
]