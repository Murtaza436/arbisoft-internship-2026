import re
from openai import OpenAI
from src.constants import (
    ASSISTANT_COLOR,
    USER_COLOR,
    SYSTEM_COLOR,
    ERROR_COLOR,
    INFO_COLOR,
    MODEL_COLOR,
    BOLD,
    DIM,
    RESET,
    HEADING_COLOR,
    BOLD_COLOR
)


def create_client(api_key, base_url='https://openrouter.ai/api/v1'):
    return OpenAI(base_url=base_url, api_key=api_key)


def print_banner(model):
    print(f'{SYSTEM_COLOR}{BOLD}')
    print('╔══════════════════════════════════════╗')
    print('║          AI Chat Assistant           ║')
    print('╚══════════════════════════════════════╝')
    print(RESET)
    print(f'{MODEL_COLOR}{DIM}Model: {model}{RESET}')
    print(f'{INFO_COLOR}Type "exit" to quit, "clear" to reset conversation.{RESET}')
    print()


def colorize_markdown(text):
    """Parses markdown syntax, removes the symbols, and injects ANSI color codes."""
    
    # 1. Colorize Headings and remove the '#' symbols
    # Matches 1-6 '#' chars, a space, and captures the rest of the line (\2)
    text = re.sub(
        r'^(#{1,6})\s+(.*)$', 
        f'{HEADING_COLOR}{BOLD}\\2{RESET}{ASSISTANT_COLOR}', 
        text, 
        flags=re.MULTILINE
    )
    
    # 2. Colorize Bold text and remove the '**' symbols
    # Captures the text inside the asterisks (\1)
    text = re.sub(
        r'\*\*(.*?)\*\*', 
        f'{BOLD_COLOR}{BOLD}\\1{RESET}{ASSISTANT_COLOR}', 
        text
    )
    
    return text


def chat_turn(client, model, conversation_history, user_input):
    conversation_history.append({'role': 'user', 'content': user_input})
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                *conversation_history,
            ],
        )
        reply = response.choices[0].message.content
        conversation_history.append({'role': 'assistant', 'content': reply})
        return reply, conversation_history, None
    except Exception as e:
        return None, conversation_history, str(e)


def run_chat(client, model):
    print_banner(model)
    history = []

    while True:
        print(f'{USER_COLOR}{BOLD}You: {RESET}', end='')
        user_input = input().strip()

        if user_input.lower() == 'exit':
            print(f'{SYSTEM_COLOR}Goodbye!{RESET}')
            break
        if user_input.lower() == 'clear':
            history = []
            print(f'{INFO_COLOR}Conversation cleared.{RESET}\n')
            continue
        if not user_input:
            continue

        print(f'{DIM}Thinking...{RESET}')
        reply, history, error = chat_turn(client, model, history, user_input)

        if error:
            print(f'{ERROR_COLOR}Error: {error}{RESET}\n')
        else:
            formatted_reply = colorize_markdown(reply)
            print(f'{ASSISTANT_COLOR}{BOLD}Assistant:{RESET}\n{ASSISTANT_COLOR}{formatted_reply}{RESET}\n')
