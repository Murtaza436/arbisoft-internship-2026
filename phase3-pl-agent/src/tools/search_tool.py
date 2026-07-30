import os
import requests
from dotenv import load_dotenv

load_dotenv()


def brave_search(query: str) -> str:
    api_key = os.getenv('BRAVE_API_KEY')
    if not api_key:
        return 'Brave API key not found in .env file.'
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': api_key,
    }
    params = {'q': query, 'count': 5}
    try:
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
            return 'No search results found.'
        output = [f'Web Search Results for: {query}\n']
        for r in results[:3]:
            title = r.get('title', '')
            description = r.get('description', '')
            url = r.get('url', '')
            output.append(f'Title: {title}\nSummary: {description}\nURL: {url}\n')
        return '\n'.join(output)
    except Exception as e:
        return f'Search error: {str(e)}'
