from src.constants import MEMORY_COLOR, RESET


class SessionMemory:
    """Simple in-session memory for the agent."""

    def __init__(self):
        self.facts = []
        self.conversation_history = []

    def add_fact(self, fact: str):
        """Store a fact in memory."""
        self.facts.append(fact)
        print(f'{MEMORY_COLOR}[Memory] Stored: {fact}{RESET}')

    def get_facts(self) -> str:
        """Retrieve all stored facts as a string."""
        if not self.facts:
            return 'No facts stored yet.'
        return '\n'.join(f'- {fact}' for fact in self.facts)

    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append({'role': role, 'content': content})

    def get_history(self) -> list:
        """Get full conversation history."""
        return self.conversation_history

    def clear(self):
        """Clear all memory."""
        self.facts = []
        self.conversation_history = []
        print(f'{MEMORY_COLOR}[Memory] Cleared.{RESET}')
