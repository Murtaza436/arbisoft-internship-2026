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
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                'role': 'system',
                'content': 'You are a summarization assistant. Provide clear concise summaries.',
            },
            {
                'role': 'user',
                'content': f'Task: {task}\n\nContent to summarize:\n{content}\n\nProvide a clear summary.',
            },
        ],
    )
    result = response.choices[0].message.content
    trace('summary_worker', 'task_complete', {'preview': result[:200]})
    return result
