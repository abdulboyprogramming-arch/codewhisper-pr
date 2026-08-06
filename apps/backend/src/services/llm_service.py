# ============================================================
# CodeWhisper PR - LLM Service
# ============================================================

import json
import re
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import settings
from src.core.exceptions import LLMError


class LLMService:
    """Service for interacting with LLM providers."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE

        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL or "https://api.openai.com/v1",
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_review(
        self,
        context: str,
        review_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a code review using LLM."""
        try:
            prompt = self._build_review_prompt(context, review_settings)

            response = await self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=review_settings.get("temperature", self.temperature) if review_settings else self.temperature,
                max_tokens=review_settings.get("max_tokens", self.max_tokens) if review_settings else self.max_tokens,
            )

            content = response.choices[0].message.content

            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {
                        "summary": content[:500],
                        "issues": [],
                        "suggestions": [],
                        "overall_assessment": "comment",
                    }

            return result

        except Exception as e:
            logger.error(f"LLM request failed: {str(e)}")
            raise LLMError(f"LLM request failed: {str(e)}")

    def _get_system_prompt(self) -> str:
        return """You are an expert code reviewer. Analyze the provided code changes and provide:
1. A brief summary of the changes
2. A list of issues found (with severity, category, description, and suggestions)
3. Overall assessment (approved, changes_requested, or comment)

Format your response as JSON with the following structure:
{
    "summary": "Brief summary of changes",
    "issues": [
        {
            "id": "1",
            "severity": "low|medium|high|critical",
            "category": "security|performance|logic|style|best_practices",
            "title": "Issue title",
            "description": "Detailed description",
            "file_path": "path/to/file",
            "line_numbers": [10, 15],
            "suggestion": "How to fix it",
            "code_example": "Example fix (optional)"
        }
    ],
    "suggestions": ["Suggestion 1", "Suggestion 2"],
    "overall_assessment": "approved|changes_requested|comment"
}"""

    def _build_review_prompt(self, context: str, review_settings: Optional[Dict[str, Any]] = None) -> str:
        prompt_parts = [
            "Please review the following code changes:\n",
            "```\n",
            context,
            "\n```\n",
        ]

        if review_settings and review_settings.get("categories"):
            categories = review_settings["categories"]
            prompt_parts.append(f"\nPlease focus on these categories: {', '.join(categories)}\n")

        if review_settings and review_settings.get("severity_threshold"):
            threshold = review_settings["severity_threshold"]
            prompt_parts.append(f"\nOnly report issues with severity level: {threshold} or higher\n")

        return "".join(prompt_parts)
