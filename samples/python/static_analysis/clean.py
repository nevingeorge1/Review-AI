"""Clean, high-quality Python module demonstrating zero static findings baseline.

SAFETY INVARIANT:
This file is strictly a STATIC TEST FIXTURE for static analysis verification.
It must NEVER be executed.
"""

from typing import List, Optional, Set


def add_item_to_cart(item_id: str, cart: Optional[List[str]] = None) -> List[str]:
    """Clean function using None for default argument."""
    active_cart = list(cart) if cart is not None else []
    active_cart.append(item_id)
    return active_cart


def find_common_elements_fast(list1: List[int], list2: List[int]) -> List[int]:
    """Clean set-based O(n) intersection."""
    set2: Set[int] = set(list2)
    return [item for item in list1 if item in set2]


def safe_exception_handling(filepath: str) -> Optional[str]:
    """Catch specific FileNotFoundError rather than bare except."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None
