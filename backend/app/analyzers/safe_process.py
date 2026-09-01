"""Safe subprocess execution adapter for invoking static analysis binaries.

Security Invariants:
1. NEVER executes submitted source code.
2. NEVER uses shell=True.
3. Passes CLI arguments as explicit sanitized lists.
4. Uses isolated temporary files with restricted permissions (0600) and guaranteed cleanup.
5. Enforces deterministic process timeouts.
"""

import asyncio
import os
import shutil
import tempfile
import time
from typing import List, Optional, Tuple

from backend.app.core.logging import logger


class SafeProcessResult:
    """Standardized output of a safe subprocess invocation."""

    def __init__(
        self,
        exit_code: int,
        stdout: str,
        stderr: str,
        duration_ms: float,
        timed_out: bool = False,
    ) -> None:
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.timed_out = timed_out


async def run_tool_safely(
    command_args: List[str],
    source_content: str,
    filename_hint: str = "submission.py",
    timeout_seconds: int = 15,
) -> Tuple[SafeProcessResult, Optional[str]]:
    """
    Safely write source code to an isolated temporary file, invoke a tool binary,
    and guarantee deterministic cleanup.

    Args:
        command_args: Command list where '{file}' is replaced with temp file path.
        source_content: Source code text to write into the isolated temp file.
        filename_hint: Filename extension hint for tool parser (e.g. 'submission.py').
        timeout_seconds: Process timeout limit.

    Returns:
        Tuple of (SafeProcessResult, temp_dir_path_cleaned)
    """
    temp_dir = tempfile.mkdtemp(prefix="reviewai_static_")
    temp_file_path = os.path.join(temp_dir, os.path.basename(filename_hint))

    # Write source with restricted permissions (0600)
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(source_content)

    # Set restricted file permissions on Unix-like systems if available
    try:
        os.chmod(temp_file_path, 0o600)
    except Exception:
        pass

    # Build sanitized argument list replacing placeholder with actual file path
    final_args = [
        temp_file_path if arg == "{file}" else arg
        for arg in command_args
    ]

    start_time = time.perf_counter()
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *final_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout_seconds,
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")

            return SafeProcessResult(
                exit_code=proc.returncode if proc.returncode is not None else 0,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration_ms,
                timed_out=False,
            ), temp_file_path

        except asyncio.TimeoutError:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning("Tool execution timed out: command=%s, timeout=%ds", final_args[0], timeout_seconds)
            if proc:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
            return SafeProcessResult(
                exit_code=-1,
                stdout="",
                stderr=f"Process timed out after {timeout_seconds} seconds",
                duration_ms=duration_ms,
                timed_out=True,
            ), temp_file_path

    except FileNotFoundError:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        return SafeProcessResult(
            exit_code=-1,
            stdout="",
            stderr=f"Executable '{final_args[0]}' not found on host system",
            duration_ms=duration_ms,
            timed_out=False,
        ), temp_file_path

    finally:
        # Guarantee deterministic deletion of temporary directory and source file
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as err:
            logger.warning("Failed to clean temp directory %s: %s", temp_dir, err)
