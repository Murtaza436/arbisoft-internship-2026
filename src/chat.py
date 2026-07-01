from openai import OpenAI


def create_client(api_key, base_url='https://openrouter.ai/api/v1'):
    return OpenAI(base_url=base_url, api_key=api_key)


def chat_turn(client, model, conversation_history, user_input):
    conversation_history.append({'role': 'user', 'content': user_input})
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            *conversation_history,
        ],
    )
    reply = response.choices[0].message.content
    conversation_history.append({'role': 'assistant', 'content': reply})
    return reply, conversation_history
