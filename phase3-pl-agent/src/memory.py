from src.constants import MEMORY_COLOR, RESET


DEFAULT_MEMORY_FILE = os.path.join('logs', 'session_memory.json')


class SessionMemory:

    MAX_FACTS = 20
    MAX_HISTORY = 20

    def __init__(self):
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

        if not fact:
            return

        fact = fact.strip()

        if len(fact) > 300:
            fact = fact[:300] + "..."

        if fact in self.facts:
            return

        self.facts.append(fact)

        if len(self.facts) > self.MAX_FACTS:
            self.facts.pop(0)

        print(f"{MEMORY_COLOR}[Memory] Stored: {fact}{RESET}")

    def get_facts(self) -> str:

        if not self.facts:
            return "No facts stored yet."

        return "\n".join(f"- {fact}" for fact in self.facts)

    def add_message(self, role: str, content: str):

        if not content:
            return

        self.conversation_history.append(
            {
                "role": role,
                "content": content,
            }
        )
        self._save()

        if len(self.conversation_history) > self.MAX_HISTORY:
            self.conversation_history.pop(0)

    def get_history(self) -> list:
        return self.conversation_history

    def get_last_messages(self, n: int = 5):
        return self.conversation_history[-n:]

    def clear(self):
        self.facts.clear()
        self.conversation_history.clear()
        print(f"{MEMORY_COLOR}[Memory] Cleared.{RESET}")