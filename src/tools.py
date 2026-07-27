import os
import requests
from pypdf import PdfReader
from src.constants import TOOL_COLOR, RESET, BOLD


def web_search(query: str) -> str:
    """Search the web using Brave Search API."""
    api_key = os.getenv('BRAVE_API_KEY')
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': api_key,
    }
    params = {'q': query, 'count': 5}
    response = requests.get(
        'https://api.search.brave.com/res/v1/web/search',
        headers=headers,
        params=params,
    )
    if response.status_code != 200:
        return f'Search failed with status {response.status_code}'

    data = response.json()
    results = data.get('web', {}).get('results', [])

    if not results:
        return 'No results found.'

    output = []
    for r in results[:3]:
        title = r.get('title', '')
        description = r.get('description', '')
        url = r.get('url', '')
        output.append(f'Title: {title}\nSummary: {description}\nURL: {url}')

    return '\n\n'.join(output)


def read_file(filepath: str) -> str:
    """Read content from a .txt or .pdf file."""
    if not os.path.exists(filepath):
        return f'File not found: {filepath}'

    if filepath.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    elif filepath.endswith('.pdf'):
        reader = PdfReader(filepath)
        text = ''
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + ' '
        return text.strip() if text else 'No text could be extracted from PDF.'

    else:
        return f'Unsupported file type. Only .txt and .pdf are supported.'


TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'web_search',
            'description': 'Search the web for current information about a topic.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The search query to look up.',
                    }
                },
                'required': ['query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'read_file',
            'description': 'Read content from a .txt or .pdf file on disk.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'filepath': {
                        'type': 'string',
                        'description': 'Path to the file to read.',
                    }
                },
                'required': ['filepath'],
            },
        },
    },
]
