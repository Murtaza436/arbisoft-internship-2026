import os
from openai import OpenAI
from dotenv import load_dotenv
from src.tools import web_search
from src.tracer import trace
from src.constants import WORKER_COLOR, RESET, BOLD

load_dotenv()

MODEL = 'nvidia/nemotron-3-ultra-550b-a55b:free'


def get_client():
    return OpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=os.getenv('OPENROUTER_API_KEY'),
    )


def search_worker(task: str) -> str:
    trace('search_worker', 'task_received', {'task': task})
    print(f'{WORKER_COLOR}{BOLD}[Search Worker]{RESET} Searching for: {task}')

    search_results = web_search(task)
    trace('search_worker', 'search_complete', {
        'preview': search_results[:200],
    })

    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                'role': 'system',
                'content': 'You are a research assistant. Summarize search results concisely.',
            },
            {
                'role': 'user',
                'content': f'Task: {task}\n\nSearch Results:\n{search_results}\n\nProvide a concise summary.',
            },
        ],
    )
    result = response.choices[0].message.content
    trace('search_worker', 'task_complete', {'preview': result[:200]})
    return result
