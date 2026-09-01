/**
 * Curated sample Python code snippets for quick evaluation and demonstration.
 * Invariant: These snippets are strictly sample text and are NEVER executed dynamically.
 */

export interface CodeSample {
  id: string;
  name: string;
  filename: string;
  description: string;
  badge: string;
  code: string;
}

export const CODE_SAMPLES: CodeSample[] = [
  {
    id: 'security_vulnerable',
    name: 'Security & Bug Hazards',
    filename: 'order_service.py',
    description: 'Dynamic eval execution, shell injection risks, and mutable defaults.',
    badge: 'Critical Risks',
    code: `import os
import pickle

API_SECRET = "sk_live_994827104928174928"

class OrderService:
    """Service handling e-commerce order submissions."""

    def __init__(self, db_conn=None):
        self.db = db_conn

    def process_order(self, order_id: str, tags: list = []):
        # Mutable default argument bug above!
        tags.append("processed")

        # Command injection hazard
        os.system(f"echo Processing order {order_id}")

        # Dangerous arbitrary expression execution
        result = eval(f"100 * len(tags)")

        return {"order_id": order_id, "result": result}

    def load_cached_payload(self, raw_bytes: bytes):
        # Insecure deserialization
        return pickle.loads(raw_bytes)
`,
  },
  {
    id: 'bug_patterns',
    name: 'Correctness & Exception Hazards',
    filename: 'calculator.py',
    description: 'Bare except clauses, division by zero edge cases, and high nesting.',
    badge: 'Bug Patterns',
    code: `def calculate_metrics(values, divisor):
    results = []
    try:
        for val in values:
            if val is not None:
                if divisor != 0:
                    for i in range(1):
                        results.append(val / divisor)
                else:
                    results.append(0)
    except:
        # Bare except masks critical errors like KeyboardInterrupt
        pass

    return results

def send_notification(user, message, retries=3, notify_sms=False, notify_email=True, priority=1, timeout=30):
    # Too many parameters (maintainability warning)
    pass
`,
  },
  {
    id: 'performance_loop',
    name: 'Performance & Inefficiencies',
    filename: 'data_analyzer.py',
    description: 'Inefficient O(N^2) nested iterations and non-pythonic list accumulation.',
    badge: 'Performance',
    code: `def find_common_elements(list_a: list, list_b: list) -> list:
    common = []
    # Quadratic nested loop with O(n^2) time complexity
    for a in list_a:
        for b in list_b:
            if a == b:
                if a not in common:
                    common.append(a)
    return common
`,
  },
  {
    id: 'clean_code',
    name: 'Clean Code Baseline',
    filename: 'user_repository.py',
    description: 'Properly typed, documented, and secure clean code.',
    badge: 'Clean Baseline',
    code: `from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    id: str
    username: str
    is_active: bool = True

class UserRepository:
    """In-memory user repository with type annotations."""

    def __init__(self) -> None:
        self._storage: Dict[str, User] = {}

    def get_user(self, user_id: str) -> Optional[User]:
        return self._storage.get(user_id)

    def add_user(self, user: User) -> None:
        self._storage[user.id] = user

    def list_active_users(self) -> List[User]:
        return [u for u in self._storage.values() if u.is_active]
`,
  },
];
