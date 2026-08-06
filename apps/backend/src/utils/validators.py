# ============================================================
# CodeWhisper PR - Validators Utility
# ============================================================

import re
from urllib.parse import urlparse
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_username(username: str) -> bool:
    """Validate username format."""
    pattern = r'^[a-zA-Z0-9_-]{3,50}$'
    return bool(re.match(pattern, username))


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True


def validate_repository_url(url: str) -> bool:
    """Validate GitHub repository URL."""
    if not validate_url(url):
        return False
    parsed = urlparse(url)
    if 'github.com' not in parsed.netloc:
        return False
    return True


def validate_pr_number(pr_number: int) -> bool:
    """Validate pull request number."""
    return pr_number > 0


def validate_file_path(file_path: str) -> bool:
    """Validate file path (prevent path traversal)."""
    if not file_path:
        return False
    if '..' in file_path:
        return False
    if any(c in file_path for c in [';', '|', '&', '$', '`']):
        return False
    return True


def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    if not text:
        return ""
    text = re.sub(r'[<>]', '', text)
    return text[:5000]
