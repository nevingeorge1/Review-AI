"""Sample Python script containing intentional flaws for testing ReviewAI detection engines.

Intentional Flaws:
1. Security: Hardcoded API token (Bandit B105 / Security)
2. Security: Insecure shell command execution with string concatenation (Bandit B605 / Security)
3. Bug: Mutable default argument in function signature
4. Bug: Resource leak / unclosed file handler
5. Style: Wildcard import and unused variables
"""

import os
import sys

API_SECRET_KEY = "sk_live_99887766554433221100aabbccddeeff"


def process_user_records(record_id: str, tags: list = []):
    """Bug: mutable default argument 'tags' retains state across invocations."""
    tags.append(record_id)
    return tags


def execute_maintenance(subcommand: str):
    """Security: Command injection via unvalidated shell string concatenation."""
    os.system("echo 'Running maintenance: ' " + subcommand)


def load_configuration_file(filepath: str) -> str:
    """Bug: Unclosed file descriptor without context manager."""
    f = open(filepath, "r")
    content = f.read()
    return content
