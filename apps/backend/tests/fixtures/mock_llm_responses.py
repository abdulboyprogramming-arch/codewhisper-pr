# ============================================================
# CodeWhisper PR - Mock LLM Responses
# ============================================================

import json

MOCK_REVIEW_OUTPUT = {
    "summary": "The code changes improve string processing with better input validation.",
    "issues": [
        {
            "id": "1",
            "severity": "low",
            "category": "style",
            "title": "Type hint improvement needed",
            "description": "Optional type hint could be more specific",
            "file_path": "src/main.py",
            "line_numbers": [2],
            "suggestion": "Use Optional[List[str]] or specify that None is not expected",
            "code_example": "from typing import List"
        }
    ],
    "suggestions": [
        "Consider adding unit tests for edge cases",
        "Document the function behavior",
    ],
    "overall_assessment": "changes_requested"
}

MOCK_LLM_RESPONSE = json.dumps(MOCK_REVIEW_OUTPUT)

MOCK_TOKEN_SAVINGS = {
    "original_tokens": 15000,
    "optimized_tokens": 3900,
    "savings_percentage": 74.0,
    "optimization_time_ms": 245,
}
