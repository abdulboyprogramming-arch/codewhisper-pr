# ============================================================
# CodeWhisper PR - Review Validators
# ============================================================

import re
from typing import Optional
from src.core.exceptions import ValidationError

GITHUB_URL_PATTERN = re.compile(
    r"^https?://(www\.)?github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)(/.*)?$"
)
GITLAB_URL_PATTERN = re.compile(
    r"^https?://(www\.)?gitlab\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)(/.*)?$"
)
BITBUCKET_URL_PATTERN = re.compile(
    r"^https?://(www\.)?bitbucket\.org/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)(/.*)?$"
)


def validate_repository_url(url: str) -> str:
    """Validate that the repository URL is well-formed and from a supported provider."""
    if not url or not isinstance(url, str):
        raise ValidationError("Repository URL is required")

    url = url.strip()

    supported_patterns = [
        ("GitHub", GITHUB_URL_PATTERN),
        ("GitLab", GITLAB_URL_PATTERN),
        ("Bitbucket", BITBUCKET_URL_PATTERN),
    ]

    for provider_name, pattern in supported_patterns:
        match = pattern.match(url)
        if match:
            return url

    raise ValidationError(
        "Invalid repository URL. Supported providers: GitHub, GitLab, Bitbucket. "
        "Example: https://github.com/owner/repo"
    )


def validate_pr_number(pr_number: int) -> int:
    """Validate the PR number is within valid range."""
    if not isinstance(pr_number, int):
        raise ValidationError("PR number must be an integer")
    if pr_number < 1:
        raise ValidationError("PR number must be a positive integer")
    if pr_number > 999999:
        raise ValidationError("PR number is out of valid range")
    return pr_number


def validate_branch_name(branch: Optional[str]) -> Optional[str]:
    """Validate the branch name if provided."""
    if branch is None:
        return None
    if not isinstance(branch, str):
        raise ValidationError("Branch name must be a string")
    if len(branch) > 256:
        raise ValidationError("Branch name exceeds maximum length of 256 characters")
    if not re.match(r"^[a-zA-Z0-9/._\-]+$", branch):
        raise ValidationError(
            "Branch name contains invalid characters. Only alphanumeric, /, ., _, and - are allowed"
        )
    return branch


def validate_review_settings(settings: Optional[dict]) -> Optional[dict]:
    """Validate review settings."""
    if settings is None:
        return None

    valid_keys = {"severity_threshold", "categories", "max_tokens", "temperature"}
    for key in settings:
        if key not in valid_keys:
            raise ValidationError(f"Invalid setting key: {key}")

    if "severity_threshold" in settings:
        valid_thresholds = {"low", "medium", "high"}
        if settings["severity_threshold"] not in valid_thresholds:
            raise ValidationError(f"Invalid severity threshold. Must be one of: {valid_thresholds}")

    if "max_tokens" in settings:
        max_t = settings["max_tokens"]
        if not isinstance(max_t, int) or max_t < 100 or max_t > 8000:
            raise ValidationError("max_tokens must be between 100 and 8000")

    if "temperature" in settings:
        temp = settings["temperature"]
        if not isinstance(temp, (int, float)) or temp < 0 or temp > 1:
            raise ValidationError("temperature must be between 0 and 1")

    if "categories" in settings:
        valid_categories = {"security", "performance", "maintainability", "correctness", "style"}
        for cat in settings["categories"]:
            if cat not in valid_categories:
                raise ValidationError(f"Invalid category: {cat}. Valid categories: {valid_categories}")

    return settings


def validate_review_request(
    repository_url: str,
    pr_number: int,
    branch: Optional[str] = None,
    settings: Optional[dict] = None,
) -> dict:
    """Validate all fields of a review creation request."""
    return {
        "repository_url": validate_repository_url(repository_url),
        "pr_number": validate_pr_number(pr_number),
        "branch": validate_branch_name(branch),
        "settings": validate_review_settings(settings),
    }
