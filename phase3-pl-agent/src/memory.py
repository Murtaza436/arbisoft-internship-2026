import json
import os

from src.constants import MEMORY_COLOR, RESET, BOLD


DEFAULT_MEMORY_FILE = os.path.join('logs', 'session_memory.json')


class SessionMemory:
    def __init__(self, memory_file: str = DEFAULT_MEMORY_FILE):
        self.memory_file = memory_file
        self.facts = []
        self.conversation_history = []
        self._load()

    def _load(self):
        if not os.path.exists(self.memory_file):
            return

        try:
            with open(self.memory_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            self.facts = data.get('facts', [])
            self.conversation_history = data.get('conversation_history', [])
        except Exception:
            self.facts = []
            self.conversation_history = []

    def _save(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w', encoding='utf-8') as file:
            json.dump(
                {
                    'facts': self.facts,
                    'conversation_history': self.conversation_history,
                },
                file,
                indent=2,
            )

    def add_fact(self, fact: str):
        if fact not in self.facts:
            self.facts.append(fact)
            self._save()
            print(f'{MEMORY_COLOR}[Memory] Stored: {fact}{RESET}')

    def get_facts(self) -> str:
        if not self.facts:
            return 'No facts stored yet.'
        return '\n'.join(f'- {fact}' for fact in self.facts)

    def add_message(self, role: str, content: str):
        self.conversation_history.append(
            {'role': role, 'content': content}
        )
        self._save()

    def get_history(self) -> list:
        return self.conversation_history

    def clear(self):
        self.facts = []
        self.conversation_history = []
        self._save()
        print(f'{MEMORY_COLOR}[Memory] Cleared.{RESET}')
