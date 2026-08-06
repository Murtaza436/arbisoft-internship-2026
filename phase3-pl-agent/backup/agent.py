import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from src.tools.registry import TOOLS, TOOL_MAP
from src.memory import SessionMemory
from src.hooks import pre_tool_hook, post_tool_hook
from src.constants import RESET, BOLD, DIM

load_dotenv()

DEFAULT_MODEL = 'openai/gpt-oss-20b:free'
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

? Always use tool results as the source of truth.

? Never invent:
  - seasons
  - clubs
  - scores
  - standings
  - transfers
  - statistics

? If a tool returns no data, tell the user exactly that.

? Never rewrite league tables into paragraphs.

? If a tool returns a table or list, preserve the ordering.

? Never change match scores.

? Never infer a winner from a draw.

? Never say a team won 1-1.

? Never say a team won 5-8.

? If a match is 1-1 it is a draw.

? If historical data is requested and no season is specified,
search across every available historical season.

? Never invent seasons such as
Mohamed Salah 2015-16
unless the user explicitly requested that season.

? Call the most appropriate tool once.

? Do not repeatedly call the same tool.

? After receiving tool output, answer immediately.

? Keep answers factual.

? Do not embellish or narrate statistics.

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
        base_url='https://openrouter.ai/api/v1',
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

    max_iterations = 4
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
                tool_choice='auto',
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

                if tool_call_counts[tool_name] > 2:
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': f'Already searched with {tool_name}. Use the results already collected to answer.',
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
                memory.add_fact(f'Used {tool_name} for: {user_message[:50]}')

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
        summary_client = get_primary_client()
        try:
            summary = summary_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'Summarize this Premier League data clearly. Use markdown tables for stats.',
                    },
                    {
                        'role': 'user',
                        'content': f'Question: {user_message}\n\nData collected:\n{chr(10).join(collected_results[:3])}\n\nProvide a clear answer.',
                    },
                ],
            )
            if summary.choices and summary.choices[0].message.content:
                return summary.choices[0].message.content
        except Exception:
            pass
        return '\n\n'.join(collected_results[:2])

    return run_fallback_agent(user_message, memory)


