from src.constants import MEMORY_COLOR, RESET, BOLD


class SessionMemory:
    def __init__(self):
        self.facts = []
        self.conversation_history = []

    def add_fact(self, fact: str):
        if fact not in self.facts:
            self.facts.append(fact)
            print(f'{MEMORY_COLOR}[Memory] Stored: {fact}{RESET}')

    def get_facts(self) -> str:
        if not self.facts:
            return 'No facts stored yet.'
        return '\n'.join(f'- {fact}' for fact in self.facts)

    def add_message(self, role: str, content: str):
        self.conversation_history.append(
            {'role': role, 'content': content}
        )

    def get_history(self) -> list:
        return self.conversation_history

    def clear(self):
        self.facts = []
        self.conversation_history = []
        print(f'{MEMORY_COLOR}[Memory] Cleared.{RESET}')
