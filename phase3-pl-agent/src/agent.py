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
from src.constants import RESET, DIM

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = 'deepseek/deepseek-v4-flash'
FALLBACK_MODEL = 'tinyllama:latest'

SYSTEM_PROMPT = '''You are a Premier League football research assistant inspired by FotMob.

You have access to football tools.

AVAILABLE TOOLS

1. search_historical_stats
2. get_standings
3. get_top_scorers
4. get_recent_results
5. get_upcoming_fixtures
6. get_team_matches
7. brave_search

STRICT RULES

You MUST answer every football question using one of the provided tools.

Do not answer from memory.

Choose exactly one tool when one tool is sufficient.
Use multiple tools only when the question genuinely requires comparison or multi-hop reasoning.

Wait for the tool output.

Only after receiving tool output may you answer.

Never call the same tool twice.

If the tool returns "No data", answer exactly that.

HISTORICAL PLAYER QUESTIONS
→ search_historical_stats

HISTORICAL MATCH QUESTIONS
→ search_historical_stats

CURRENT STANDINGS
→ get_standings

CURRENT TOP SCORERS
→ get_top_scorers

FIXTURES
→ get_upcoming_fixtures

RECENT RESULTS
→ get_recent_results

TEAM SCHEDULE
→ get_team_matches

TRANSFERS / NEWS
→ brave_search


OUTPUT FORMAT RULES

When comparing two or more players, teams, seasons, competitions,
or historical campaigns, ALWAYS use a Markdown table.

Examples include:

- Mohamed Salah vs Erling Haaland
- Leicester City 2015-16 vs Liverpool 2019-20
- Liverpool 2019-20 vs Liverpool current season
- Two players' career statistics
- Two clubs' historical records
- Current player vs historical player
- Current season vs historical season

For comparisons, prefer a structure like:

| Stat | Option A | Option B | Difference |
|---|---:|---:|---:|

When comparing seasons or teams, include the most relevant
available statistics such as points, wins, draws, losses,
goals, goal difference, position, or other statistics returned
by the tools.

When comparing players, include relevant available statistics
such as games, minutes, goals, assists, yellow cards, and red
cards.

If a value is not available from the tool output, use "—".
Never invent a missing statistic.

For rankings, standings, scorers, fixtures, and results,
use Markdown tables whenever the data is naturally tabular.

For ordinary questions that only need one or two facts,
a short answer is acceptable.

For comparison questions:
1. Give a short heading.
2. Give the comparison table.
3. Give a short factual conclusion.
4. Do not add unsupported statistics.

Preserve all numbers and facts returned by the tools.
Do not invent information.
'''


FALLBACK_SYSTEM_PROMPT = '''You are a Premier League football assistant.

You MUST answer ONLY using the supplied tool output.

RULES

- Do NOT invent facts.
- Do NOT use outside football knowledge.
- Do NOT rewrite standings into paragraphs.
- Preserve rankings exactly as given.
- Preserve scores exactly as given.
- A 1-1 score is a draw.
- Never describe a draw as a win.
- Never change the winning team.
- If a table is provided, reproduce it in markdown.
- If a list is provided, preserve the same ordering.
- If the tool says no data is available, tell the user exactly that.
- Keep answers concise and factual.
'''


def get_primary_client():
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=os.getenv('OPENROUTER_API_KEY'),
    )


def get_fallback_client():
    return OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama',
    )


def run_fallback_agent(user_message: str, memory: SessionMemory) -> str:
    client = get_fallback_client()
    lower_msg = user_message.lower()

    tool_results = []

    if any(w in lower_msg for w in [
        'standing',
        'standings',
        'table',
        'league table',
        'top of',
        'bottom',
        'position',
        'rank',
        'ranking',
        'points'
    ]):
        from src.tools.live_tool import get_standings
        tool_results.append(get_standings())
    elif any(w in lower_msg for w in [
        'scorer',
        'scorers',
        'top scorer',
        'leading scorer',
        'golden boot',
        'goals this season',
        'most goals'
    ]):
        from src.tools.live_tool import get_top_scorers
        tool_results.append(get_top_scorers())
    elif any(w in lower_msg for w in [
        'result',
        'results',
        'score',
        'scores',
        'latest match',
        'recent match',
        'last match',
        'last game',
        'won',
        'lost',
        'draw',
        'vs',
        'versus'
    ]):
        from src.tools.live_tool import get_recent_results
        tool_results.append(get_recent_results())
    elif any(w in lower_msg for w in [
        'fixture',
        'fixtures',
        'upcoming',
        'next match',
        'next game',
        'play next',
        'when do',
        'when does'
    ]):
        from src.tools.live_tool import get_upcoming_fixtures
        tool_results.append(get_upcoming_fixtures())
    elif any(w in lower_msg for w in ['transfer', 'news', 'injury', 'injured', 'manager', 'signing', 'sign']):
        from src.tools.search_tool import brave_search
        tool_results.append(brave_search(user_message))
    else:
        from src.tools.rag_tool import search_historical_stats
        try:
            tool_results.append(search_historical_stats(user_message, n_results=30))
        except Exception:
            from src.tools.search_tool import brave_search
            tool_results.append(brave_search(user_message))

    context = '\n\n'.join(tool_results) if tool_results else 'No data available.'

    messages = [
        {'role': 'system', 'content': FALLBACK_SYSTEM_PROMPT},
        {
            'role': 'user',
            'content': (
                f'Data:\n{context}\n\n'
                f'Question: {user_message}\n\n'
                f'''Answer ONLY using the supplied data.

Rules:

- Do not invent information.
- Do not rewrite league tables into paragraphs.
- Preserve rankings exactly.
- Preserve scores exactly.
- Never infer winners from draws.
- If the data is already formatted as a table or list, keep the same structure.
- If the data says no information is available, say exactly that.
- Do not use outside football knowledge.
'''
            )
        }
    ]

    try:
        response = client.chat.completions.create(
            model=FALLBACK_MODEL,
            messages=messages,
        )
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content
        return f'Here is what I found:\n\n{context}'
    except Exception as e:
        return f'Here is what I found:\n\n{context}'


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
    if use_fallback:
        print(f'{DIM}Agent thinking... (model: {FALLBACK_MODEL}){RESET}')
        return run_fallback_agent(user_message, memory)

    client = get_primary_client()
    model = DEFAULT_MODEL

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

    max_iterations = 6
    iteration = 0
    tool_call_counts = {}
    collected_results = []

    while iteration < max_iterations:
        iteration += 1
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0,
                top_p=0.9,
                timeout=60,
        )
        except Exception as e:
            print("="*70)
            print("PRIMARY MODEL FAILED")
            print(type(e).__name__)
            print(str(e))
            print("="*70)
            return run_fallback_agent(user_message, memory)

        if not response.choices:
            print(f'{DIM}No choices returned by model, switching to fallback...{RESET}')
            return run_fallback_agent(user_message, memory)

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        if not message.content and not message.tool_calls:
            print(f'{DIM}Empty response, switching to fallback...{RESET}')
            return run_fallback_agent(user_message, memory)

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
                tool_call_counts[tool_name] = tool_call_counts.get(tool_name, 0) + 1

                if tool_call_counts[tool_name] > 1:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Already searched with {tool_name}. Use the previous result.",
                    })
                    continue

                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except Exception:
                    tool_args = {}

                pre_tool_hook(tool_name, tool_args)
                tool_fn = TOOL_MAP.get(tool_name)
                if tool_fn:
                    try:
                        result = tool_fn(**tool_args)
                    except Exception as e:
                        result = f'Tool error: {str(e)}'
                else:
                    result = f'Unknown tool: {tool_name}'

                post_tool_hook(tool_name, result)
                collected_results.append(result)
                memory.add_fact(
                    f"{tool_name}: {result[:150]}"
                )

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': result,
                })

        else:
            final_answer = message.content or ''
            if final_answer:
                memory.add_message('assistant', final_answer)
                return final_answer
            break

    if collected_results:
        final_answer = "\n\n".join(collected_results)
        memory.add_message('assistant', final_answer) # Saves raw data to memory
        return final_answer

    fallback_answer = run_fallback_agent(user_message, memory)
    memory.add_message('assistant', fallback_answer) # Saves fallback to memory
    return fallback_answer