"""Static test fixture for bug patterns and mutable defaults.

SAFETY INVARIANT:
This file is strictly a STATIC TEST FIXTURE for static analysis verification.
It must NEVER be executed.
"""


def add_item_to_cart(item_id: str, cart: list = []):
    """RULE-008: Mutable default list argument."""
    cart.append(item_id)
    return cart


def set_user_config(key: str, val: str, options: dict = {}):
    """RULE-008: Mutable default dict argument."""
    options[key] = val
    return options


def dangerous_bare_except(filename: str):
    """RULE-009: Bare except clause."""
    try:
        f = open(filename, "r")
        data = f.read()
        f.close()
        return data
    except:
        return None
