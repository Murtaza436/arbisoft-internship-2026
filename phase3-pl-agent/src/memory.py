from src.constants import MEMORY_COLOR, RESET


class SessionMemory:

    MAX_FACTS = 20
    MAX_HISTORY = 20

    def __init__(self):
        self.facts = []
        self.conversation_history = []

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