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

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a research assistant. Summarize search results concisely.',
                },
                {
                    'role': 'user',
                    'content': (
                        f'Task: {task}\n\n'
                        f'Search Results:\n{search_results}\n\n'
                        f'Provide a concise summary.'
                    ),
                },
            ],
        )

        if not response.choices or response.choices[0].message.content is None:
            result = f'Model returned empty response. Search results: {search_results[:200]}'
        else:
            result = response.choices[0].message.content

    except Exception as e:
        result = f'Error calling model: {str(e)}. Search results: {search_results[:200]}'

    trace('search_worker', 'task_complete', {'preview': result[:200]})
    return result
