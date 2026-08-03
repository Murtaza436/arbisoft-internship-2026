import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from src.tools.registry import TOOLS, TOOL_MAP
from src.tools.live_tool import (
    get_standings,
    get_top_scorers,
    get_recent_results,
    get_upcoming_fixtures,
    get_team_matches,
)
from src.tools.rag_tool import search_historical_stats
from src.tools.search_tool import brave_search
from src.memory import SessionMemory
from src.hooks import pre_tool_hook, post_tool_hook
from src.constants import AGENT_COLOR, RESET, BOLD, DIM

load_dotenv()

DEFAULT_MODEL = 'nvidia/nemotron-3-ultra-550b-a55b:free'
FALLBACK_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1')
OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')

SYSTEM_PROMPT = '''You are a Premier League football research assistant inspired by FotMob.
You have access to:
1. search_historical_stats - detailed player stats from 2015-16 to 2022-23 seasons
2. get_standings - current Premier League table
3. get_top_scorers - current season top scorers
4. get_recent_results - latest match results
5. get_upcoming_fixtures - upcoming matches
6. get_team_matches - matches for a specific team
7. brave_search - web search for news and transfers

Guidelines:
- For historical player stats (2015-16 to 2022-23): use search_historical_stats
- For current season data: use get_standings, get_top_scorers, get_recent_results
- For news and transfers: use brave_search
- You can use multiple tools in sequence for complex questions
- Always cite which source your answer came from
- Be specific with numbers and statistics
- If comparing historical vs current, use both sources'''


def get_client(use_fallback: bool = True):
    if use_fallback:
        return OpenAI(
            base_url=OLLAMA_BASE_URL,
            api_key=os.getenv('OLLAMA_API_KEY', 'ollama'),
        ), FALLBACK_MODEL

    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=os.getenv('OPENROUTER_API_KEY'),
    ), DEFAULT_MODEL


def _extract_team_name(user_message: str) -> str:
    common_teams = [
        'arsenal', 'aston villa', 'bournemouth', 'brentford', 'brighton',
        'burnley', 'chelsea', 'crystal palace', 'everton', 'fulham',
        'liverpool', 'luton', 'manchester city', 'man city',
        'manchester united', 'man united', 'newcastle', 'nottingham forest',
        'sheffield united', 'spurs', 'tottenham', 'west ham', 'wolverhampton',
        'wolves', 'leicester',
    ]
    lower_message = user_message.lower()
    for team in common_teams:
        if team in lower_message:
            return team.title()
    return ''


def _build_direct_tool_context(user_message: str) -> tuple[str, list[str]]:
    lower_message = user_message.lower()
    sections = []
    sources = []

    if any(term in lower_message for term in [
        'transfer', 'transfers', 'injury', 'news', 'rumour', 'rumor',
        'signing', 'signed', 'loan', 'manager',
    ]):
        sections.append(brave_search(user_message))
        sources.append('brave_search')

    if any(term in lower_message for term in [
        'standings', 'table', 'top of the premier league', 'top of the table',
        'league position', 'current position',
    ]):
        sections.append(get_standings())
        sources.append('get_standings')

    if any(term in lower_message for term in [
        'top scorer', 'leading scorer', 'scorer', 'goal scorer',
    ]):
        sections.append(get_top_scorers())
        sources.append('get_top_scorers')

    if any(term in lower_message for term in [
        'recent result', 'recent results', 'latest result', 'latest results',
        'recent match', 'latest match', 'scoreline', 'scores', 'results',
    ]):
        sections.append(get_recent_results())
        sources.append('get_recent_results')

    if any(term in lower_message for term in [
        'upcoming fixture', 'upcoming fixtures', 'fixture', 'fixtures',
        'next match', 'next games', 'next fixture', 'schedule',
    ]):
        sections.append(get_upcoming_fixtures())
        sources.append('get_upcoming_fixtures')

    team_name = _extract_team_name(user_message)
    if team_name and any(term in lower_message for term in ['team', 'match', 'fixture', 'fixtures', 'results', 'games', 'for ', 'of ']):
        sections.append(get_team_matches(team_name))
        sources.append('get_team_matches')

    if any(term in lower_message for term in [
        'historical', 'compare', '2015', '2016', '2017', '2018', '2019',
        '2020', '2021', '2022', '2023',
    ]):
        sections.append(search_historical_stats(user_message))
        sources.append('search_historical_stats')

    if not sections:
        sections.append(brave_search(user_message))
        sources.append('brave_search')

    return '\n\n'.join(sections), sources


def _answer_with_local_model(
    user_message: str,
    tool_context: str,
    sources: list[str],
) -> str:
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key=os.getenv('OLLAMA_API_KEY', 'ollama'),
    )
    prompt = (
        'You are a Premier League football research assistant.\n'
        'Rewrite the provided tool output as a concise GitHub-flavored Markdown answer.\n'
        'When the information is ranked or tabular, use a markdown table.\n'
        'Keep names, spellings, numbers, and team names exactly as they appear in the tool output.\n'
        'Do not invent facts or add extra commentary.\n\n'
        f'User question:\n{user_message}\n\n'
        f'Source tools:\n{", ".join(sources) if sources else "direct_router"}\n\n'
        f'Tool output:\n{tool_context}\n'
    )
    try:
        response = client.chat.completions.create(
            model=FALLBACK_MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0,
        )
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
    except Exception:
        pass

    return tool_context or 'No answer generated.'


def run_agent(
    user_message: str,
    memory: SessionMemory,
    use_fallback: bool = False,
) -> str:
    client, model = get_client(use_fallback)

    facts = memory.get_facts()
    system = SYSTEM_PROMPT
    if facts != 'No facts stored yet.':
        system += f'\n\nContext from this session:\n{facts}'

    memory.add_message('user', user_message)

    messages = [
        {'role': 'system', 'content': system},
        *memory.get_history(),
    ]

    print(f'{DIM}Agent thinking... (model: {model}){RESET}')

    max_iterations = 8
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                tool_choice='auto',
            )
        except Exception as e:
            if not use_fallback:
                print(f'{DIM}Primary model failed, switching to fallback...{RESET}')
                return run_agent(user_message, memory, use_fallback=True)

            tool_context, sources = _build_direct_tool_context(user_message)
            answer = _answer_with_local_model(user_message, tool_context, sources)
            for source in sources or ['direct_router']:
                memory.add_fact(f'Used {source} for: {user_message[:50]}')
            memory.add_message('assistant', answer)
            return answer

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        if not message.content and not message.tool_calls:
            if not use_fallback:
                print(f'{DIM}Empty response, switching to fallback...{RESET}')
                return run_agent(user_message, memory, use_fallback=True)

            return 'Model returned empty response.'

        if finish_reason == 'tool_calls' and message.tool_calls:
            messages.append({
                'role': 'assistant',
                'content': message.content or '',
                'tool_calls': [
                    {
                        'id': tc.id,
                        'type': 'function',
                        'function': {
                            'name': tc.function.name,
                            'arguments': tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except Exception:
                    tool_args = {}

                pre_tool_hook(tool_name, tool_args)
                tool_fn = TOOL_MAP.get(tool_name)
                if tool_fn:
                    result = tool_fn(**tool_args)
                else:
                    result = f'Unknown tool: {tool_name}'
                post_tool_hook(tool_name, result)

                memory.add_fact(f'Used {tool_name} for: {user_message[:50]}')

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': result,
                })
        else:
            final_answer = message.content or 'No answer generated.'
            memory.add_message('assistant', final_answer)
            return final_answer

    return 'Agent reached maximum iterations without a final answer.'
