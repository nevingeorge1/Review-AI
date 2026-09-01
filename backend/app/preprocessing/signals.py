"""Catalog of potentially interesting or security-sensitive call patterns.

Fundamental Architecture Principle:
These signals are NOT automatic vulnerability verdicts.
They provide structured factual signals to guide Module 4 static analyzers (Bandit/AST rules)
and Module 5 LLM reasoning.
"""

from typing import Dict, Optional, Tuple


# Mapping of call names/attribute chains to (category, description)
INTERESTING_CALL_PATTERNS: Dict[str, Tuple[str, str]] = {
    # Code execution / Dynamic evaluation
    "eval": ("code_execution", "Dynamic code evaluation via eval()"),
    "exec": ("code_execution", "Dynamic code execution via exec()"),
    "compile": ("code_execution", "Dynamic compilation via compile()"),
    "__import__": ("code_execution", "Dynamic module import via __import__()"),

    # Operating system / Process execution
    "os.system": ("process_execution", "Shell command execution via os.system()"),
    "os.popen": ("process_execution", "Shell command pipe via os.popen()"),
    "os.spawn": ("process_execution", "Process spawning via os.spawn()"),
    "os.spawnl": ("process_execution", "Process spawning via os.spawnl()"),
    "os.spawnv": ("process_execution", "Process spawning via os.spawnv()"),
    "subprocess.run": ("process_execution", "Subprocess invocation via subprocess.run()"),
    "subprocess.Popen": ("process_execution", "Subprocess pipeline via subprocess.Popen()"),
    "subprocess.call": ("process_execution", "Subprocess execution via subprocess.call()"),
    "subprocess.check_output": ("process_execution", "Subprocess output capture via subprocess.check_output()"),
    "subprocess.check_call": ("process_execution", "Subprocess execution via subprocess.check_call()"),

    # Deserialization / Object loading
    "pickle.loads": ("deserialization", "Insecure object deserialization via pickle.loads()"),
    "pickle.load": ("deserialization", "Insecure object deserialization via pickle.load()"),
    "_pickle.loads": ("deserialization", "Insecure object deserialization via _pickle.loads()"),
    "_pickle.load": ("deserialization", "Insecure object deserialization via _pickle.load()"),
    "yaml.load": ("deserialization", "YAML loading via yaml.load() (potential arbitrary code execution if Loader is unsafe)"),
    "yaml.unsafe_load": ("deserialization", "Explicit unsafe YAML loading via yaml.unsafe_load()"),
    "marshal.loads": ("deserialization", "Deserialization via marshal.loads()"),
    "marshal.load": ("deserialization", "Deserialization via marshal.load()"),
    "shelve.open": ("deserialization", "Persistent object storage via shelve.open()"),

    # Filesystem I/O
    "open": ("io_filesystem", "File I/O stream via open()"),
    "os.remove": ("io_filesystem", "File deletion via os.remove()"),
    "os.unlink": ("io_filesystem", "File unlinking via os.unlink()"),
    "shutil.rmtree": ("io_filesystem", "Directory tree removal via shutil.rmtree()"),
    "tempfile.mktemp": ("io_filesystem", "Insecure temporary file creation via tempfile.mktemp()"),

    # Networking & Web requests
    "requests.get": ("network", "HTTP GET request via requests.get()"),
    "requests.post": ("network", "HTTP POST request via requests.post()"),
    "requests.put": ("network", "HTTP PUT request via requests.put()"),
    "requests.delete": ("network", "HTTP DELETE request via requests.delete()"),
    "urllib.request.urlopen": ("network", "URL opening via urllib.request.urlopen()"),
    "http.client.HTTPConnection": ("network", "Raw HTTP connection"),
    "socket.socket": ("network", "Low-level socket creation via socket.socket()"),

    # Database / SQL queries
    "cursor.execute": ("database", "SQL query execution via cursor.execute()"),
    "connection.execute": ("database", "SQL query execution via connection.execute()"),
    "session.execute": ("database", "Database session execution via session.execute()"),

    # User input
    "input": ("input", "Standard user input via input()"),
    "raw_input": ("input", "Legacy user input via raw_input()"),
}


def classify_interesting_call(call_chain: str) -> Optional[Tuple[str, str]]:
    """
    Check if a call expression matches known interesting pattern categories.

    Returns:
        Tuple of (category, description) or None if not flagged.
    """
    # Exact match
    if call_chain in INTERESTING_CALL_PATTERNS:
        return INTERESTING_CALL_PATTERNS[call_chain]

    # Suffix match (e.g. self.cursor.execute -> cursor.execute)
    for pattern, info in INTERESTING_CALL_PATTERNS.items():
        if call_chain.endswith("." + pattern) or call_chain.endswith(pattern):
            return info

    return None
