import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from src.tools import web_search, read_file, TOOLS
from src.memory import SessionMemory
from src.hooks import pre_tool_hook, post_tool_hook
from src.constants import AGENT_COLOR, TOOL_COLOR, RESET, BOLD, DIM

load_dotenv()


def get_client():
    return OpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=os.getenv('OPENROUTER_API_KEY'),
    )


TOOL_MAP = {
    'web_search': web_search,
    'read_file': read_file,
}

SYSTEM_PROMPT = '''You are a helpful research agent. You have access to these tools:
1. web_search - search the web for current information
2. read_file - read content from .txt or .pdf files

When answering questions:
- Use web_search for current events or facts you need to verify
- Use read_file when the user mentions a specific file
- You can use multiple tools in sequence for complex questions
- Always cite your sources

Previously stored facts from memory will be provided to you.
Use them when relevant to answer questions.'''


def run_agent(user_message: str, memory: SessionMemory, model: str = 'openai/gpt-oss-120b:free') -> str:
    """Run one turn of the agent."""
    client = get_client()

    facts = memory.get_facts()
    system_with_memory = SYSTEM_PROMPT
    if facts != 'No facts stored yet.':
        system_with_memory += f'\n\nFacts from memory:\n{facts}'

    memory.add_message('user', user_message)

    messages = [
        {'role': 'system', 'content': system_with_memory},
        *memory.get_history(),
    ]

    print(f'{DIM}Agent thinking...{RESET}')

    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice='auto',
        )

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        if finish_reason == 'tool_calls' and message.tool_calls:
            messages.append({
                'role': 'assistant',
                'content': message.content or '',
                'tool_calls': [
                    {
                        'id': tc.id,
                        'type': 'function',
                        'function': {
                            'name': tc.function.name,
                            'arguments': tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                pre_tool_hook(tool_name, tool_args)
                tool_fn = TOOL_MAP.get(tool_name)
                if tool_fn:
                    result = tool_fn(**tool_args)
                else:
                    result = f'Unknown tool: {tool_name}'
                post_tool_hook(tool_name, result)

                if tool_name == 'web_search':
                    memory.add_fact(f"Searched for: {tool_args.get('query')} - found results")

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': result,
                })

        else:
            final_answer = message.content
            memory.add_message('assistant', final_answer)
            return final_answer

    return 'Agent reached maximum iterations without a final answer.'
