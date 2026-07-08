import os
from openai import OpenAI
from dotenv import load_dotenv
from src.retriever import retrieve

load_dotenv()


def get_client():
    return OpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=os.getenv('OPENROUTER_API_KEY'),
    )


def rag_answer(query, collection, model='tencent/hy3:free'):
    chunks, sources = retrieve(query, collection)

    context = '\n\n'.join(chunks)

    prompt = f'''Use the following context to answer the question.
If the answer is not in the context, say I do not know.

Context:
{context}

Question: {query}

Answer:'''

    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
    )

    answer = response.choices[0].message.content
    return answer, sources, chunks
