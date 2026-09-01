"""Sample containing security-sensitive call patterns as static test fixtures.

IMPORTANT SAFETY INVARIANT:
This file is strictly a STATIC TEST FIXTURE for parser and signal verification.
It must NEVER be executed.
"""

import os
import pickle
import subprocess
import yaml


def trigger_dynamic_eval(user_code: str):
    """Dynamic code evaluation signal."""
    return eval(user_code)


def trigger_exec(command_payload: str):
    """Dynamic exec signal."""
    exec(command_payload)


def trigger_os_system(cmd: str):
    """Shell execution signal."""
    os.system("echo " + cmd)


def trigger_subprocess(args_list: list):
    """Subprocess signal."""
    subprocess.run(args_list, check=True)


def trigger_unsafe_deserialization(raw_bytes: bytes):
    """Pickle deserialization signal."""
    return pickle.loads(raw_bytes)


def trigger_yaml_load(yaml_text: str):
    """YAML load signal."""
    return yaml.load(yaml_text, Loader=yaml.Loader)
