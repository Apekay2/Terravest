"""
String utilities for log processing.
"""


def truncate_middle(text: str, max_length: int = 1000, edge_chars: int = 400) -> str:
    """Truncate a string from the middle, keeping the beginning and end.

    This preserves context by showing both the start and end of long strings,
    which is useful for large tool results or outputs.

    Args:
        text: The string to truncate.
        max_length: Maximum length before truncation kicks in (default: 1000).
        edge_chars: Number of characters to keep from each end (default: 400).

    Returns:
        Truncated string with format: "start... [truncated N chars] ...end"
    """
    if not text or len(text) <= max_length:
        return text

    truncated_count = len(text) - (2 * edge_chars)
    middle_message = f"... [truncated {truncated_count} chars] ..."

    start = text[:edge_chars]
    end = text[-edge_chars:]

    return f"{start}{middle_message}{end}"
