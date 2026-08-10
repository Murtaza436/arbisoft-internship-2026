import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"


def brave_search(query: str) -> str:
    api_key = os.getenv("BRAVE_API_KEY")

    if not api_key:
        return "Brave API key not found in .env."

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }

    params = {
        "q": f"Premier League {query}",
        "count": 5,
    }

    try:
        response = requests.get(
            BRAVE_URL,
            headers=headers,
            params=params,
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("web", {}).get("results", [])

        if not results:
            return "No search results found."

        output = [
            "# Latest Premier League News",
            f"Search: {query}",
            "",
        ]

        seen = set()
        count = 0

        for result in results:

            title = result.get("title", "Unknown Title").strip()
            description = result.get("description", "").strip()
            url = result.get("url", "").strip()
            age = result.get("age", "Unknown")

            if not url or url in seen:
                continue

            seen.add(url)

            output.append(
                f"""
## {title}

**Published:** {age}

**Summary**

{description if description else "No summary available."}

**Source**

{url}

---
"""
            )

            count += 1

            if count >= 5:
                break

        if count == 0:
            return "No relevant search results found."

        return "\n".join(output)

    except requests.exceptions.Timeout:
        return "Search request timed out."

    except requests.exceptions.HTTPError as e:
        return f"Search failed (HTTP {response.status_code}): {e}"

    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"

    except Exception as e:
        return f"Unexpected search error: {e}"