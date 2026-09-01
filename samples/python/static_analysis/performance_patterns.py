"""Static test fixture for performance patterns and nested loops.

SAFETY INVARIANT:
This file is strictly a STATIC TEST FIXTURE for static analysis verification.
It must NEVER be executed.
"""

from typing import List


def find_common_elements_slow(list1: List[int], list2: List[int]) -> List[int]:
    """RULE-015: Inefficient O(n^2) nested loop."""
    common = []
    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                common.append(item1)
    return common
