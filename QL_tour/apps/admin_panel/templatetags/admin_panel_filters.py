from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


@register.filter(name="get_item")
def get_item(value: Any, key: Any) -> Any:
    """
    Safe access helper for Django templates.
    Enables: {{ my_dict|get_item:some_key }}
    """
    if value is None:
        return None
    try:
        # Dict-like
        if hasattr(value, "get"):
            return value.get(key)
        # Fallback to __getitem__
        return value[key]
    except Exception:
        return None

