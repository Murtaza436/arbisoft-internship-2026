from dotenv import load_dotenv
from src.agent import run_agent
from src.memory import SessionMemory
from src.constants import (
    AGENT_COLOR, USER_COLOR, SYSTEM_COLOR,
    ERROR_COLOR, INFO_COLOR, BOLD, RESET, CYAN
)

load_dotenv()


def print_banner():
    print(f'{CYAN}{BOLD}')
    print('+--------------------------------------+')
    print('¦         Research Agent v1.0          ¦')
    print('+--------------------------------------+')
    print(RESET)
    print(f'{INFO_COLOR}Commands: "exit" to quit, "clear" to reset memory, "memory" to see stored facts{RESET}')
    print()


def main():
    load_dotenv()
    memory = SessionMemory()
    print_banner()

    while True:
        print(f'{USER_COLOR}{BOLD}You: {RESET}', end='')
        user_input = input().strip()

        if not user_input:
            continue
        if user_input.lower() == 'exit':
            print(f'{CYAN}Goodbye!{RESET}')
            break
        if user_input.lower() == 'clear':
            memory.clear()
            continue
        if user_input.lower() == 'memory':
            print(f'{CYAN}[Memory] Stored facts:\n{memory.get_facts()}{RESET}\n')
            continue

        try:
            answer = run_agent(user_input, memory)
            print(f'{AGENT_COLOR}{BOLD}Agent:{RESET} {answer}\n')
        except Exception as e:
            print(f'{ERROR_COLOR}Error: {e}{RESET}\n')


if __name__ == '__main__':
    main()
