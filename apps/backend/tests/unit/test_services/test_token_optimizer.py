# ============================================================
# CodeWhisper PR - Token Optimizer Tests
# ============================================================

import pytest
from src.services.token_optimizer import TokenOptimizer
from src.models.review import Review


@pytest.mark.unit
class TestTokenOptimizer:

    def test_optimize_content_short(self):
        optimizer = TokenOptimizer()
        content = "print('hello world')"
        result = optimizer.optimize_content(content, max_tokens=100)

        assert result["optimized_content"] == content
        assert result["original_tokens"] <= 100
        assert result["optimized_tokens"] <= result["original_tokens"]
        assert result["savings_percentage"] >= 0

    def test_optimize_content_long(self):
        optimizer = TokenOptimizer()
        content = "def hello():\n    print('hello world')\n" * 500

        result = optimizer.optimize_content(content, max_tokens=4000)

        assert len(result["optimized_content"]) <= len(content)
        assert result["savings_percentage"] >= 0

    def test_get_savings_stats(self):
        optimizer = TokenOptimizer()
        stats = optimizer.get_savings_stats(15000, 3900)

        assert stats["original_tokens"] == 15000
        assert stats["optimized_tokens"] == 3900
        assert stats["tokens_saved"] == 11100
        assert stats["savings_percentage"] == 74.0

    def test_get_savings_stats_zero_original(self):
        optimizer = TokenOptimizer()
        stats = optimizer.get_savings_stats(0, 0)

        assert stats["tokens_saved"] == 0
        assert stats["savings_percentage"] == 0.0

    def test_estimate_tiktoken_count(self):
        optimizer = TokenOptimizer()
        text = "Hello, world!"
        count = optimizer.estimate_tiktoken_count(text)

        assert count > 0
        assert isinstance(count, int)

    def test_is_optimization_beneficial(self):
        optimizer = TokenOptimizer()
        assert optimizer.is_optimization_beneficial(15000, 3900) is True
        assert optimizer.is_optimization_beneficial(100, 90) is False
        assert optimizer.is_optimization_beneficial(100, 26) is True
