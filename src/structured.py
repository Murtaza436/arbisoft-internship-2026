import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()


class MovieReview(BaseModel):
    title: str
    genre: str
    rating: float
    summary: str
    recommended: bool


def get_client():
    return OpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=os.getenv('OPENROUTER_API_KEY'),
    )


def generate_structured_output(movie_description, model='nvidia/nemotron-3-ultra-550b-a55b:free'):
    """Ask LLM to return structured JSON and validate with Pydantic."""
    client = get_client()

    prompt = f'''Analyze this movie and return a JSON object with exactly these fields:
- title: string
- genre: string
- rating: float between 0 and 10
- summary: string of one sentence
- recommended: boolean

Movie: {movie_description}

Return ONLY the JSON object, no extra text, no markdown, no backticks.'''

    response = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
        validated = MovieReview(**data)
        return validated, raw, None
    except (json.JSONDecodeError, ValidationError) as e:
        return None, raw, str(e)
