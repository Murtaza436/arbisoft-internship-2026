import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def brave_search(query: str) -> str:
    api_key = os.getenv('BRAVE_API_KEY')
    if not api_key:
        return 'Brave API key not found in .env file.'

    current_year = datetime.now().year
    if str(current_year) not in query and str(current_year - 1) not in query:
        query = f'{query} {current_year}'

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
        output = [
            f'Web Search Results for: {query}\n',
            'Note: Web results are unverified and may contain inaccuracies.\n'
        ]
        for r in results[:3]:
            title = r.get('title', '')
            description = r.get('description', '')
            url = r.get('url', '')
            output.append(f'Title: {title}')
            output.append(f'Summary: {description}')
            output.append(f'URL: {url}\n')
        return '\n'.join(output)
    except Exception as e:
        return f'Search error: {str(e)}'
