"""Metrics and complexity calculations for Python AST analysis.

Formulas & Assumptions:
1. Cyclomatic Complexity (McCabe estimate):
   Base complexity = 1
   +1 for each branching point:
   - If / elif
   - For / async for
   - While
   - ExceptHandler
   - With / async with
   - Assert
   - BoolOp (And / Or: each additional operand adds a decision branch)
   - IfExp (Ternary expressions)
   - Comprehensions (ListComp, DictComp, SetComp, GeneratorExp)

2. Physical and Logical Line Classification:
   - Total lines: len(source.split('\n'))
   - Blank lines: Lines with only whitespace
   - Comment lines: Lines where the first non-whitespace character is '#'
   - Logical lines: Total lines - Blank lines - Comment lines
"""

import ast
from typing import Tuple
from backend.app.preprocessing.models import CodeMetrics, FunctionMetrics


def calculate_line_metrics(source_code: str) -> Tuple[int, int, int, int]:
    """
    Calculate physical, logical, comment, and blank line counts.

    Returns:
        Tuple of (total_lines, logical_lines, comment_lines, blank_lines)
    """
    if not source_code:
        return 0, 0, 0, 0

    lines = source_code.split("\n")
    total_lines = len(lines)
    blank_lines = 0
    comment_lines = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank_lines += 1
        elif stripped.startswith("#"):
            comment_lines += 1

    logical_lines = max(0, total_lines - blank_lines - comment_lines)
    return total_lines, logical_lines, comment_lines, blank_lines


def estimate_node_cyclomatic_complexity(node: ast.AST) -> int:
    """
    Estimate cyclomatic complexity for an AST subtree (e.g. a FunctionDef or Module).
    """
    complexity = 1

    for child in ast.walk(node):
        # Decision / Branch points
        if isinstance(child, (ast.If, ast.IfExp)):
            complexity += 1
        elif isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, (ast.With, ast.AsyncWith)):
            complexity += 1
        elif isinstance(child, ast.Assert):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            # BoolOp contains multiple values (e.g. 'a and b and c' -> 2 decision points)
            complexity += max(1, len(child.values) - 1)
        elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            complexity += len(child.generators)

    return complexity


def calculate_function_metrics(func_node: ast.AST, source_code: str) -> FunctionMetrics:
    """
    Compute detailed structural and complexity metrics for a function node.
    """
    # Line count spanned
    start_line = getattr(func_node, "lineno", 1)
    end_line = getattr(func_node, "end_lineno", start_line)
    line_count = max(1, end_line - start_line + 1)

    # Parameter count
    param_count = 0
    if hasattr(func_node, "args"):
        args = func_node.args
        param_count = (
            len(args.posonlyargs)
            + len(args.args)
            + len(args.kwonlyargs)
            + (1 if args.vararg else 0)
            + (1 if args.kwarg else 0)
        )

    # Branching, loop, and nesting counts
    branching_count = 0
    loop_count = 0
    max_nesting = 0

    def compute_internal_nesting(node: ast.AST, current_depth: int) -> None:
        nonlocal branching_count, loop_count, max_nesting
        max_nesting = max(max_nesting, current_depth)

        for child in ast.iter_child_nodes(node):
            is_branch = isinstance(child, (ast.If, ast.IfExp, ast.Try, ast.ExceptHandler))
            is_loop = isinstance(child, (ast.For, ast.AsyncFor, ast.While))

            if is_branch:
                branching_count += 1
            if is_loop:
                loop_count += 1

            next_depth = current_depth + 1 if (is_branch or is_loop) else current_depth
            compute_internal_nesting(child, next_depth)

    compute_internal_nesting(func_node, 0)
    complexity = estimate_node_cyclomatic_complexity(func_node)

    return FunctionMetrics(
        line_count=line_count,
        parameter_count=param_count,
        branching_count=branching_count,
        loop_count=loop_count,
        nesting_depth=max_nesting,
        cyclomatic_complexity=complexity,
    )
