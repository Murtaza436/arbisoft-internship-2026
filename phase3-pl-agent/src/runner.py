from dotenv import load_dotenv
from src.agent import run_agent
from src.memory import SessionMemory
from src.constants import (
    AGENT_COLOR,
    USER_COLOR,
    ERROR_COLOR,
    INFO_COLOR,
    BOLD,
    RESET,
    CYAN,
)

load_dotenv()


def print_banner():
    print(f"{CYAN}{BOLD}")
    print("+-----------------------------------------------------------+")
    print("|        Premier League Research Agent v2.0                 |")
    print("|   OpenFootball + Football-Data.org + Brave + OpenRouter   |")
    print("+-----------------------------------------------------------+")
    print(RESET)

    print(f"{INFO_COLOR}Ask me anything about the Premier League.")
    print("Historical data: 2015-16 to 2025-26")
    print("Live data: Football-Data.org API")
    print("News & transfers: Brave Search")
    print("LLM: OpenRouter")
    print("Commands: exit | clear | memory")
    print(RESET)


def main():
    load_dotenv()

    memory = SessionMemory()

    print_banner()

    while True:
        print(f"{USER_COLOR}{BOLD}You:{RESET} ", end="")
        user_input = input().strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print(f"{CYAN}Goodbye!{RESET}")
            break

        if user_input.lower() == "clear":
            memory.clear()
            print(f"{CYAN}Memory cleared.{RESET}\n")
            continue

        if user_input.lower() == "memory":
            print(f"{CYAN}[Memory]\n{memory.get_facts()}{RESET}\n")
            continue

        try:
            answer = run_agent(user_input, memory)
            print(f"\n{AGENT_COLOR}{BOLD}Agent:{RESET} {answer}\n")
        except Exception as e:
            print(f"{ERROR_COLOR}Error: {e}{RESET}\n")


if __name__ == "__main__":
    main()