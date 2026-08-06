# ============================================================
# CodeWhisper PR - Paritok Service
# ============================================================

import httpx
from typing import Dict, Any, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import settings
from src.core.exceptions import ParitokError


class ParitokService:
    """Service for interacting with Paritok API."""

    def __init__(self):
        self.api_key = settings.PARITOK_API_KEY
        self.base_url = settings.PARITOK_BASE_URL.rstrip('/')
        self.model = settings.PARITOK_MODEL

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=120.0,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def optimize_context(
        self,
        context: str,
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """Use Paritok to optimize and summarize context."""
        try:
            response = await self.client.post(
                "/optimize",
                json={
                    "context": context,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "model": self.model,
                },
            )

            if response.status_code != 200:
                logger.error(f"Paritok optimization failed: {response.status_code}")
                raise ParitokError(f"Optimization failed: {response.status_code}")

            data = response.json()

            original_tokens = data.get("original_tokens", 0)
            optimized_tokens = data.get("optimized_tokens", 0)
            savings_percentage = data.get("savings_percentage", 0)

            logger.info(
                f"Paritok optimization: {original_tokens} -> {optimized_tokens} "
                f"tokens ({savings_percentage:.1f}% savings)"
            )

            return data

        except httpx.RequestError as e:
            logger.error(f"Paritok request failed: {str(e)}")
            raise ParitokError(f"Request failed: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_code_snippet(
        self,
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """Use Paritok to analyze a code snippet."""
        try:
            response = await self.client.post(
                "/analyze",
                json={"code": code, "language": language, "model": self.model},
            )

            if response.status_code != 200:
                raise ParitokError(f"Analysis failed: {response.status_code}")

            return response.json()

        except httpx.RequestError as e:
            logger.error(f"Paritok analysis failed: {str(e)}")
            raise ParitokError(f"Analysis failed: {str(e)}")

    async def get_token_count(self, text: str) -> int:
        """Get token count for a piece of text."""
        try:
            response = await self.client.post(
                "/token-count",
                json={"text": text},
            )

            if response.status_code != 200:
                return len(text) // 4

            return response.json().get("token_count", len(text) // 4)

        except httpx.RequestError as e:
            logger.warning(f"Token count request failed: {str(e)}")
            return len(text) // 4

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
