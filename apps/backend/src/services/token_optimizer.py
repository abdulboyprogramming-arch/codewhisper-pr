# ============================================================
# CodeWhisper PR - Token Optimizer Service
# ============================================================

from typing import Dict, Any, List, Tuple, Optional
from loguru import logger
import time

from src.services.paritok_service import ParitokService
from src.utils.token_counter import TokenCounter


# Minimum token savings ratio for optimization to be considered beneficial.
OPTIMIZATION_BENEFIT_THRESHOLD = 0.5


class TokenOptimizer:
    """Service for optimizing token usage with Paritok."""

    def __init__(self, paritok_service: Optional[ParitokService] = None):
        self.paritok_service = paritok_service
        self.token_counter = TokenCounter()

    # ------------------------------------------------------------------
    # Convenience helpers (used by tests and lightweight callers)
    # ------------------------------------------------------------------
    def estimate_tiktoken_count(self, text: str) -> int:
        """Estimate the token count for a piece of text."""
        return max(1, self.token_counter.count_tokens(text))

    def get_savings_stats(self, original_tokens: int, optimized_tokens: int) -> Dict[str, Any]:
        """Return summary statistics for a token optimization operation."""
        tokens_saved = max(0, original_tokens - optimized_tokens)
        savings_percentage = (
            round((tokens_saved / original_tokens) * 100, 2)
            if original_tokens > 0
            else 0.0
        )
        return {
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": tokens_saved,
            "savings_percentage": savings_percentage,
        }

    def is_optimization_beneficial(
        self, original_tokens: int, optimized_tokens: int
    ) -> bool:
        """Determine whether optimization yields worthwhile savings."""
        if original_tokens <= 0:
            return False
        savings = (original_tokens - optimized_tokens) / original_tokens
        return savings >= OPTIMIZATION_BENEFIT_THRESHOLD

    def optimize_content(self, content: str, max_tokens: int = 4000) -> Dict[str, Any]:
        """Optimize content to fit within a token budget, minimizing information loss."""
        original_tokens = self.token_counter.count_tokens(content)

        if original_tokens <= max_tokens:
            optimized_content = content
            optimized_tokens = original_tokens
        else:
            optimized_content = self.token_counter.truncate_text(content, max_tokens)
            optimized_tokens = self.token_counter.count_tokens(optimized_content)

        stats = self.get_savings_stats(original_tokens, optimized_tokens)
        return {
            "optimized_content": optimized_content,
            "original_tokens": stats["original_tokens"],
            "optimized_tokens": stats["optimized_tokens"],
            "savings_percentage": stats["savings_percentage"],
        }

    # ------------------------------------------------------------------
    # Diff-focused optimization (used by the review pipeline)
    # ------------------------------------------------------------------
    async def optimize_diff(
        self,
        diff_content: str,
        affected_files: List[Dict[str, Any]],
        ast_analysis: Dict[str, Any],
    ) -> Tuple[str, Dict[str, Any]]:
        """Optimize the diff content for token efficiency."""
        try:
            start_time = time.time()

            original_tokens = await self._get_token_count(diff_content)

            core_changes = await self._extract_core_changes(
                diff_content, affected_files, ast_analysis
            )
            optimized_context = await self._generate_optimized_context(
                core_changes, affected_files, ast_analysis
            )
            optimized_tokens = await self._get_token_count(optimized_context)

            optimization_time_ms = int((time.time() - start_time) * 1000)
            savings_percentage = (
                ((original_tokens - optimized_tokens) / original_tokens) * 100
                if original_tokens > 0
                else 0
            )

            metrics = {
                "original_tokens": original_tokens,
                "optimized_tokens": optimized_tokens,
                "savings_percentage": round(savings_percentage, 2),
                "optimization_time_ms": optimization_time_ms,
                "tokens_saved": original_tokens - optimized_tokens,
            }

            logger.info(
                f"Token optimization complete: {original_tokens} -> {optimized_tokens} "
                f"tokens ({savings_percentage:.1f}% savings)"
            )

            return optimized_context, metrics

        except Exception as e:
            logger.error(f"Token optimization failed: {str(e)}")
            return diff_content, {"error": str(e)}

    async def _get_token_count(self, text: str) -> int:
        """Get the token count, preferring the Paritok service and falling back locally."""
        if self.paritok_service and self.paritok_service.api_key:
            try:
                return await self.paritok_service.get_token_count(text)
            except Exception:
                pass
        return self.token_counter.count_tokens(text)

    async def _extract_core_changes(
        self,
        diff_content: str,
        affected_files: List[Dict[str, Any]],
        ast_analysis: Dict[str, Any],
    ) -> str:
        """Extract core changes from diff using AST analysis."""
        try:
            important_changes = ast_analysis.get("important_changes", [])

            lines = diff_content.splitlines()
            filtered_lines = []

            for line in lines:
                if line.startswith("diff --git") or line.startswith("index"):
                    filtered_lines.append(line)
                elif line.startswith("---") or line.startswith("+++"):
                    filtered_lines.append(line)
                elif line.startswith("@@"):
                    filtered_lines.append(line)
                elif line.startswith("+") or line.startswith("-"):
                    line_content = line[1:].strip()
                    is_important = False

                    for change in important_changes:
                        if line_content in change.get("content", ""):
                            is_important = True
                            break
                    keywords = [
                        "def", "class", "function", "import", "return",
                        "error", "bug", "fix", "security", "vulnerability",
                    ]
                    if any(kw in line_content.lower() for kw in keywords):
                        is_important = True
                    if is_important:
                        filtered_lines.append(line)

            if len(filtered_lines) < 10:
                result = await self.optimize_content(diff_content, max_tokens=1536)
                return result["optimized_content"]

            return "\n".join(filtered_lines)

        except Exception as e:
            logger.warning(f"Extract core changes failed: {str(e)}")
            return diff_content

    async def _generate_optimized_context(
        self,
        core_changes: str,
        affected_files: List[Dict[str, Any]],
        ast_analysis: Dict[str, Any],
    ) -> str:
        """Generate optimized context for LLM review."""
        context_parts = []

        summary = ast_analysis.get("summary", "Code changes detected")
        context_parts.append(f"=== Summary ===\n{summary}\n")

        context_parts.append("=== Affected Files ===")
        for file in affected_files[:10]:
            file_summary = f"- {file.get('path', 'unknown')}"
            if file.get("changes"):
                file_summary += f" ({len(file['changes'])} changes)"
            context_parts.append(file_summary)
        context_parts.append("")

        if ast_analysis.get("affected_symbols"):
            context_parts.append("=== Affected Symbols ===")
            for symbol in ast_analysis["affected_symbols"][:10]:
                context_parts.append(
                    f"- {symbol.get('name')} ({symbol.get('type')})"
                )
            context_parts.append("")

        context_parts.append("=== Code Changes ===")
        context_parts.append(core_changes[:3000])

        context_parts.append("\n=== Review Request ===")
        context_parts.append(
            "Please review this code change. Focus on:\n"
            "1. Security vulnerabilities\n"
            "2. Logic errors and edge cases\n"
            "3. Best practices and code quality\n"
            "4. Performance implications\n"
            "5. Potential side effects\n"
            "Provide specific line numbers and actionable feedback."
        )

        return "\n".join(context_parts)
