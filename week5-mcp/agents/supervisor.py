import os
from openai import OpenAI
from dotenv import load_dotenv
from agents.search_worker import search_worker
from agents.summary_worker import summary_worker
from src.tracer import trace
from src.constants import SUPERVISOR_COLOR, RESET, BOLD, DIM

load_dotenv()

MODEL = 'nvidia/nemotron-3-ultra-550b-a55b:free'


def get_client():
    return OpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=os.getenv('OPENROUTER_API_KEY'),
    )


ROUTING_PROMPT = '''You are a supervisor agent. Given a user task, decide which worker to use:

- search_worker: use when the task requires searching the web for current information
- summary_worker: use when the task requires summarizing a file or provided content

Respond with ONLY a JSON object like this:
{"worker": "search_worker", "task": "the specific task for the worker"}
or
{"worker": "summary_worker", "task": "the specific task", "filepath": "path/to/file or null"}

No extra text, no markdown, just the JSON.'''


def supervisor(user_request: str) -> str:
    trace('supervisor', 'request_received', {'request': user_request})
    print(f'{SUPERVISOR_COLOR}{BOLD}[Supervisor]{RESET} Routing: {user_request}')

    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {'role': 'system', 'content': ROUTING_PROMPT},
            {'role': 'user', 'content': user_request},
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace('`json', '').replace('`', '').strip()

    try:
        import json
        decision = json.loads(raw)
        worker = decision.get('worker')
        task = decision.get('task', user_request)

        trace('supervisor', 'routing_decision', {'worker': worker, 'task': task})
        print(f'{SUPERVISOR_COLOR}[Supervisor]{RESET} Routing to: {BOLD}{worker}{RESET}')

        if worker == 'search_worker':
            result = search_worker(task)
        elif worker == 'summary_worker':
            filepath = decision.get('filepath')
            result = summary_worker(task, filepath)
        else:
            result = f'Unknown worker: {worker}'

        trace('supervisor', 'task_complete', {'preview': result[:200]})
        return result

    except Exception as e:
        trace('supervisor', 'routing_error', {'error': str(e), 'raw': raw})
        print(f'Routing failed, using search worker directly. Error: {e}')
        return search_worker(user_request)
