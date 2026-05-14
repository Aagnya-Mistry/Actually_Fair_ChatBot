import re


class GuardrailService:
    def __init__(self):
        self.injection_patterns = [
            r"ignore.*instructions",
            r"system prompt",
            r"reveal.*prompt",
            r"developer message",
            r"act as",
            r"pretend to be",
            r"write python",
            r"write code",
            r"solve this",
            r"quantum physics",
            r"leetcode"
        ]

    def is_blocked(self, message: str) -> bool:
        text = message.lower()

        for pattern in self.injection_patterns:
            if re.search(pattern, text):
                return True

        return False

    def get_blocked_response(self) -> str:
        return (
            "I'm here to help you explore Actually Fair products and pricing. "
            "I can't assist with unrelated requests."
        )


guardrail_service = GuardrailService()