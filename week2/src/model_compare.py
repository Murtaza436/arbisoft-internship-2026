from openai import OpenAI
import time


def compare_models(client, models, prompt):
    results = []
    for model in models:
        print(f'Querying {model}...')
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
        )
        elapsed = time.time() - start
        text = response.choices[0].message.content
        results.append({'model': model, 'response': text, 'time': elapsed})
    return results
