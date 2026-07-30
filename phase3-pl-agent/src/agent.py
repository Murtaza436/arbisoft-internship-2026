import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from src.tools.registry import TOOLS, TOOL_MAP
from src.memory import SessionMemory
from src.hooks import pre_tool_hook, post_tool_hook
from src.constants import AGENT_COLOR, RESET, BOLD, DIM

load_dotenv()

DEFAULT_MODEL = 'nvidia/nemotron-3-ultra-550b-a55b:free'
FALLBACK_MODEL = 'tinyllama'

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


def get_client(use_fallback: bool = False):
    if use_fallback:
        return OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='ollama',
        ), FALLBACK_MODEL
    return OpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=os.getenv('OPENROUTER_API_KEY'),
    ), DEFAULT_MODEL


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
            return f'Error calling model: {str(e)}'

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
