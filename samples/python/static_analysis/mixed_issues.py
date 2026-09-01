"""Static test fixture containing mixed security, bug, style, and performance issues.

SAFETY INVARIANT:
This file is strictly a STATIC TEST FIXTURE for static analysis verification.
It must NEVER be executed.
"""

import os
import pickle

API_KEY = "sk_live_11223344556677889900aabbcc"


def process_data(items: list = [], secret_override: str = ""):
    """Mixed issues: mutable default, os.system, eval, broad exception, nested loops."""
    if secret_override:
        eval(secret_override)

    os.system("echo processing...")

    try:
        for a in items:
            for b in items:
                if a == b:
                    print(a)
    except:
        pass
