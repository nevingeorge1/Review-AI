"""Sample clean, idiomatic Python module demonstrating high-quality code baseline."""

from pathlib import Path
import subprocess
from typing import List, Optional


def process_user_records(record_id: str, tags: Optional[List[str]] = None) -> List[str]:
    """Correctly initialize default argument to prevent mutable state retention."""
    active_tags = list(tags) if tags is not None else []
    active_tags.append(record_id)
    return active_tags


def execute_maintenance(subcommand: str) -> None:
    """Safely execute command using list arguments to avoid shell injection."""
    subprocess.run(["echo", f"Running maintenance: {subcommand}"], check=True)


def load_configuration_file(filepath: Path) -> str:
    """Safely read file using context manager to ensure descriptor closure."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
