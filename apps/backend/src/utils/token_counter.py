# ============================================================
# CodeWhisper PR - Token Counter Utility
# ============================================================

from typing import List, Dict, Any
from loguru import logger

try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False
    logger.warning("Tiktoken not available, using approximate token counting")


class TokenCounter:
    """Utility for counting tokens in text."""

    def __init__(self, model: str = "gpt-4"):
        self.model = model
        if _TIKTOKEN_AVAILABLE:
            try:
                self.encoder = tiktoken.encoding_for_model(model)
            except Exception:
                self.encoder = tiktoken.get_encoding("cl100k_base")
        else:
            self.encoder = None

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        if self.encoder:
            try:
                return len(self.encoder.encode(text))
            except Exception as e:
                logger.warning(f"Token counting failed: {str(e)}")
        return len(text) // 4

    def count_messages(self, messages: List[Dict[str, Any]]) -> int:
        """Count tokens in a list of messages."""
        if not self.encoder:
            return sum(len(msg.get("content", "")) // 4 for msg in messages)

        total = 0
        for msg in messages:
            if msg.get("content"):
                total += len(self.encoder.encode(msg["content"]))
            total += 2
            if msg.get("name"):
                total += len(self.encoder.encode(msg["name"]))

        total += 4
        return total

    def truncate_text(self, text: str, max_tokens: int, preserve_ends: bool = True) -> str:
        """Truncate text to fit within max tokens."""
        if not self.encoder:
            max_chars = max_tokens * 4
            if len(text) <= max_chars:
                return text
            return text[:max_chars]

        tokens = self.encoder.encode(text)

        if len(tokens) <= max_tokens:
            return text

        if preserve_ends:
            keep_start = int(max_tokens * 0.6)
            keep_end = max_tokens - keep_start
            truncated_tokens = tokens[:keep_start] + tokens[-keep_end:]
        else:
            truncated_tokens = tokens[:max_tokens]

        return self.encoder.decode(truncated_tokens)

    def estimate_cost(self, tokens: int, cost_per_million: float = 3.0) -> float:
        """Estimate cost for token usage."""
        return (tokens / 1_000_000) * cost_per_million
