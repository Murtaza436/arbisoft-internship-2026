import os
from openai import OpenAI
from dotenv import load_dotenv
from src.tools import read_file
from src.tracer import trace
from src.constants import WORKER_COLOR, RESET, BOLD

load_dotenv()

MODEL = 'nvidia/nemotron-3-ultra-550b-a55b:free'


def get_client():
    return OpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=os.getenv('OPENROUTER_API_KEY'),
    )


def summary_worker(task: str, filepath: str = None) -> str:
    trace('summary_worker', 'task_received', {'task': task})
    print(f'{WORKER_COLOR}{BOLD}[Summary Worker]{RESET} Summarizing: {task}')

    content = ''
    if filepath:
        content = read_file(filepath)
        trace('summary_worker', 'file_read', {
            'filepath': filepath,
            'chars': len(content),
        })

    client = get_client()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a summarization assistant. Provide clear concise summaries.',
                },
                {
                    'role': 'user',
                    'content': (
                        f'Task: {task}\n\n'
                        f'Content to summarize:\n{content}\n\n'
                        f'Provide a clear summary.'
                    ),
                },
            ],
        )

        if not response.choices or response.choices[0].message.content is None:
            result = f'Model returned empty response. Content read: {content[:200]}'
        else:
            result = response.choices[0].message.content

    except Exception as e:
        result = f'Error calling model: {str(e)}. Content read: {content[:200]}'

    trace('summary_worker', 'task_complete', {'preview': result[:200]})
    return result
