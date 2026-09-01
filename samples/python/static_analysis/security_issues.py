"""Static test fixture for security vulnerabilities.

SAFETY INVARIANT:
This file is strictly a STATIC TEST FIXTURE for static analysis verification.
It must NEVER be executed.
"""

import os
import pickle
import subprocess

API_SECRET = "sk_live_abcdef1234567890abcdef123456"


def insecure_eval(user_payload: str):
    """RULE-001: Dangerous eval."""
    return eval(user_payload)


def insecure_exec(user_code: str):
    """RULE-002: Dangerous exec."""
    exec(user_code)


def insecure_system_call(cmd_arg: str):
    """RULE-004: os.system shell risk."""
    os.system("ls -la " + cmd_arg)


def insecure_subprocess(target_ip: str):
    """RULE-005: subprocess shell=True."""
    subprocess.run(f"ping -c 1 {target_ip}", shell=True)


def insecure_deserialization(raw_data: bytes):
    """RULE-006: pickle deserialization."""
    return pickle.loads(raw_data)


def insecure_sql_query(cursor, user_id: str):
    """RULE-014: SQL Injection."""
    cursor.execute("SELECT * FROM users WHERE id = '" + user_id + "'")
