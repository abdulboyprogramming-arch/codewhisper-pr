# ============================================================
# CodeWhisper PR - Helpers Utility
# ============================================================

import uuid
import json
from datetime import datetime
from typing import Any, Optional, Dict


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def safe_json_loads(data: str) -> Optional[Dict[str, Any]]:
    """Safely load JSON data."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to maximum length."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"


def calculate_percentage(part: float, whole: float) -> float:
    """Calculate percentage."""
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 2)
