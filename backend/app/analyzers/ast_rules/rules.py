"""Concrete implementations of 15 high-value custom AST static analysis rules.

Safety & False-Positive Principles:
1. Rules inspect static AST structure and CodeContext.
2. Contextual evaluation is used to prevent false positives.
3. Every rule is independently testable for positive and negative cases.
"""

import ast
import re
from typing import List

from backend.app.analyzers.ast_rules.base import ASTRule
from backend.app.models.domain import SourceFile, StaticFinding
from backend.app.models.enums import Category, Severity
from backend.app.preprocessing.models import CodeContext


# ==============================================================================
# RULE-001: Dangerous dynamic execution: eval()
# ==============================================================================
class Rule001Eval(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-001"

    @property
    def title(self) -> str:
        return "Dangerous dynamic code execution via eval()"

    @property
    def category(self) -> Category:
        return Category.SECURITY

    @property
    def severity(self) -> Severity:
        return Severity.HIGH

    @property
    def description(self) -> str:
        return "The built-in eval() function parses and executes arbitrary Python code, creating severe code injection risks."

    @property
    def recommendation(self) -> str:
        return "Replace eval() with safe parsers such as ast.literal_eval() for data literals or dedicated parsing libraries."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        for call in context.calls:
            if call.name == "eval" and call.full_attribute_chain == "eval":
                findings.append(
                    self.create_finding(
                        message="Direct invocation of eval() detected.",
                        line_number=call.line_number,
                        code_evidence=f"eval(args={call.arg_count})",
                    )
                )
        return findings


# ==============================================================================
# RULE-002: Dangerous dynamic execution: exec()
# ==============================================================================
class Rule002Exec(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-002"

    @property
    def title(self) -> str:
        return "Dangerous dynamic statement execution via exec()"

    @property
    def category(self) -> Category:
        return Category.SECURITY

    @property
    def severity(self) -> Severity:
        return Severity.HIGH

    @property
    def description(self) -> str:
        return "The built-in exec() function executes arbitrary dynamic Python statements in current/global namespace."

    @property
    def recommendation(self) -> str:
        return "Refactor logic to use static dispatch, polymorphism, or predefined function mappings instead of dynamic exec()."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        for call in context.calls:
            if call.name == "exec" and call.full_attribute_chain == "exec":
                findings.append(
                    self.create_finding(
                        message="Direct invocation of exec() detected.",
                        line_number=call.line_number,
                        code_evidence=f"exec(args={call.arg_count})",
                    )
                )
        return findings


# ==============================================================================
# RULE-003: Dynamic module import: __import__()
# ==============================================================================
class Rule003DynamicImport(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-003"

    @property
    def title(self) -> str:
        return "Dynamic module import via __import__()"

    @property
    def category(self) -> Category:
        return Category.SECURITY

    @property
    def severity(self) -> Severity:
        return Severity.MEDIUM

    @property
    def description(self) -> str:
        return "Use of __import__() bypasses static dependency tracking and may enable arbitrary module loading."

    @property
    def recommendation(self) -> str:
        return "Use standard static import statements or importlib.import_module() with an explicit allowlist."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        for call in context.calls:
            if call.name == "__import__" and call.full_attribute_chain == "__import__":
                findings.append(
                    self.create_finding(
                        message="Direct use of __import__() dynamic module loader detected.",
                        line_number=call.line_number,
                        code_evidence=f"__import__(args={call.arg_count})",
                    )
                )
        return findings


# ==============================================================================
# RULE-004: Shell command construction risk: os.system()
# ==============================================================================
class Rule004OsSystem(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-004"

    @property
    def title(self) -> str:
        return "Potential command injection risk via os.system()"

    @property
    def category(self) -> Category:
        return Category.SECURITY

    @property
    def severity(self) -> Severity:
        return Severity.HIGH

    @property
    def description(self) -> str:
        return "os.system() spawns a shell process. Unvalidated parameters can lead to critical command injection vulnerabilities."

    @property
    def recommendation(self) -> str:
        return "Replace os.system() with subprocess.run() passing arguments as a list without shell=True."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        for call in context.calls:
            if call.full_attribute_chain == "os.system" or (call.name == "system" and "os" in call.full_attribute_chain):
                findings.append(
                    self.create_finding(
                        message="Invocation of os.system() detected. Shell commands should be avoided.",
                        line_number=call.line_number,
                        code_evidence="os.system(...)",
                    )
                )
        return findings


# ==============================================================================
# RULE-005: Potential unsafe subprocess shell execution
# ==============================================================================
class Rule005UnsafeSubprocess(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-005"

    @property
    def title(self) -> str:
        return "Potential command injection via subprocess shell=True"

    @property
    def category(self) -> Category:
        return Category.SECURITY

    @property
    def severity(self) -> Severity:
        return Severity.HIGH

    @property
    def description(self) -> str:
        return "Invoking subprocess methods with shell=True or string command lines enables shell metacharacter injection."

    @property
    def recommendation(self) -> str:
        return "Pass arguments as a list (e.g. ['executable', 'arg1']) and ensure shell=False (default)."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        try:
            tree = ast.parse(source_file.content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    chain = ""
                    if isinstance(node.func, ast.Attribute):
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                            chain = f"subprocess.{node.func.attr}"
                    elif isinstance(node.func, ast.Name) and node.func.id in ("Popen", "run", "call", "check_output"):
                        chain = f"subprocess.{node.func.id}"

                    if chain:
                        # Check keyword arguments for shell=True
                        has_shell_true = any(
                            kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True
                            for kw in node.keywords
                        )
                        # Check if first arg is a formatted string or BinOp (+)
                        first_arg_is_concatenation = (
                            len(node.args) > 0
                            and isinstance(node.args[0], (ast.BinOp, ast.JoinedStr))
                        )

                        if has_shell_true or first_arg_is_concatenation:
                            detail = "with shell=True" if has_shell_true else "with dynamically concatenated command string"
                            findings.append(
                                self.create_finding(
                                    message=f"Subprocess call '{chain}' executed {detail}.",
                                    line_number=node.lineno,
                                    code_evidence=f"{chain}(...)",
                                    severity_override=Severity.HIGH if has_shell_true else Severity.MEDIUM,
                                )
                            )
        except Exception:
            pass
        return findings


# ==============================================================================
# RULE-006: Unsafe pickle deserialization
# ==============================================================================
class Rule006UnsafePickle(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-006"

    @property
    def title(self) -> str:
        return "Potential unsafe deserialization via pickle"

    @property
    def category(self) -> Category:
        return Category.SECURITY

    @property
    def severity(self) -> Severity:
        return Severity.HIGH

    @property
    def description(self) -> str:
        return "Pickle deserialization allows arbitrary bytecode execution during unpickling if the payload is untrusted."

    @property
    def recommendation(self) -> str:
        return "Use safe serialization formats such as JSON, Protocol Buffers, or msgpack for untrusted inputs."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        for call in context.calls:
            if call.full_attribute_chain in ("pickle.loads", "pickle.load", "_pickle.loads", "_pickle.load"):
                findings.append(
                    self.create_finding(
                        message=f"Deserialization using '{call.full_attribute_chain}' detected.",
                        line_number=call.line_number,
                        code_evidence=f"{call.full_attribute_chain}(...)",
                    )
                )
        return findings


# ==============================================================================
# RULE-007: Broad exception handling
# ==============================================================================
class Rule007BroadException(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-007"

    @property
    def title(self) -> str:
        return "Broad exception handling (except Exception:)"

    @property
    def category(self) -> Category:
        return Category.MAINTAINABILITY

    @property
    def severity(self) -> Severity:
        return Severity.LOW

    @property
    def description(self) -> str:
        return "Catching broad 'Exception' can mask unexpected bugs, programming errors, and systemic failures."

    @property
    def recommendation(self) -> str:
        return "Catch specific exceptions (e.g. ValueError, KeyError, FileNotFoundError) whenever possible."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        try:
            tree = ast.parse(source_file.content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is not None:
                    if isinstance(node.type, ast.Name) and node.type.id == "Exception":
                        findings.append(
                            self.create_finding(
                                message="Catching generic 'Exception' masks specific error conditions.",
                                line_number=node.lineno,
                                code_evidence="except Exception:",
                            )
                        )
        except Exception:
            pass
        return findings


# ==============================================================================
# RULE-008: Mutable default function arguments
# ==============================================================================
class Rule008MutableDefaultArg(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-008"

    @property
    def title(self) -> str:
        return "Mutable default argument in function definition"

    @property
    def category(self) -> Category:
        return Category.BUG

    @property
    def severity(self) -> Severity:
        return Severity.HIGH

    @property
    def description(self) -> str:
        return "Default argument values are evaluated once at function definition time. Mutable defaults (lists, dicts, sets) retain state across calls."

    @property
    def recommendation(self) -> str:
        return "Use None as default value and initialize the mutable object inside the function body (e.g. `items = items or []`)."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        try:
            tree = ast.parse(source_file.content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for default in node.args.defaults + node.args.kw_defaults:
                        if default is not None and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            kind = type(default).__name__.lower()
                            findings.append(
                                self.create_finding(
                                    message=f"Function '{node.name}' defines a mutable default {kind} argument.",
                                    line_number=default.lineno if hasattr(default, "lineno") else node.lineno,
                                    code_evidence=f"def {node.name}(...)",
                                )
                            )
        except Exception:
            pass
        return findings


# ==============================================================================
# RULE-009: Bare except statement
# ==============================================================================
class Rule009BareExcept(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-009"

    @property
    def title(self) -> str:
        return "Bare except statement (except:)"

    @property
    def category(self) -> Category:
        return Category.MAINTAINABILITY

    @property
    def severity(self) -> Severity:
        return Severity.MEDIUM

    @property
    def description(self) -> str:
        return "A bare 'except:' clause catches BaseException including KeyboardInterrupt and SystemExit, preventing normal program termination."

    @property
    def recommendation(self) -> str:
        return "Specify the exact exception type or at minimum use 'except Exception:'."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        try:
            tree = ast.parse(source_file.content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    findings.append(
                        self.create_finding(
                            message="Bare except: clause caught. Catches BaseException and prevents process signals.",
                            line_number=node.lineno,
                            code_evidence="except:",
                        )
                    )
        except Exception:
            pass
        return findings


# ==============================================================================
# RULE-010: Excessive function cyclomatic complexity
# ==============================================================================
class Rule010ExcessiveComplexity(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-010"

    @property
    def title(self) -> str:
        return "Excessive function cyclomatic complexity"

    @property
    def category(self) -> Category:
        return Category.MAINTAINABILITY

    @property
    def severity(self) -> Severity:
        return Severity.MEDIUM

    @property
    def description(self) -> str:
        return "Functions with high cyclomatic complexity are difficult to test, reason about, and maintain."

    @property
    def recommendation(self) -> str:
        return "Decompose the function into smaller, single-responsibility helper functions."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        threshold = self.settings.MAX_FUNCTION_COMPLEXITY
        for fn in context.functions:
            if fn.metrics.cyclomatic_complexity > threshold:
                findings.append(
                    self.create_finding(
                        message=f"Function '{fn.name}' has cyclomatic complexity of {fn.metrics.cyclomatic_complexity} (threshold is {threshold}).",
                        line_number=fn.line_number,
                        end_line=fn.end_line_number,
                        code_evidence=f"def {fn.name}(...)",
                    )
                )
        return findings


# ==============================================================================
# RULE-011: Excessive nesting depth
# ==============================================================================
class Rule011ExcessiveNesting(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-011"

    @property
    def title(self) -> str:
        return "Excessive control-flow nesting depth"

    @property
    def category(self) -> Category:
        return Category.MAINTAINABILITY

    @property
    def severity(self) -> Severity:
        return Severity.LOW

    @property
    def description(self) -> str:
        return "Deeply nested control structures (if/for/while/try) impair readability and indicate complex branching."

    @property
    def recommendation(self) -> str:
        return "Use guard clauses, early returns, or extract nested blocks into helper functions."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        threshold = self.settings.MAX_NESTING_DEPTH
        for fn in context.functions:
            if fn.metrics.nesting_depth > threshold:
                findings.append(
                    self.create_finding(
                        message=f"Function '{fn.name}' exceeds maximum nesting depth ({fn.metrics.nesting_depth} > {threshold}).",
                        line_number=fn.line_number,
                        end_line=fn.end_line_number,
                        code_evidence=f"def {fn.name}(...)",
                    )
                )
        return findings


# ==============================================================================
# RULE-012: Too many function parameters
# ==============================================================================
class Rule012TooManyParameters(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-012"

    @property
    def title(self) -> str:
        return "Too many function parameters"

    @property
    def category(self) -> Category:
        return Category.MAINTAINABILITY

    @property
    def severity(self) -> Severity:
        return Severity.LOW

    @property
    def description(self) -> str:
        return "Functions taking a large number of parameters indicate high coupling and are error-prone for callers."

    @property
    def recommendation(self) -> str:
        return "Group related parameters into a dataclass, Pydantic model, or parameter object."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        threshold = self.settings.MAX_FUNCTION_PARAMETERS
        for fn in context.functions:
            if fn.parameter_count > threshold:
                findings.append(
                    self.create_finding(
                        message=f"Function '{fn.name}' has {fn.parameter_count} parameters (threshold is {threshold}).",
                        line_number=fn.line_number,
                        end_line=fn.end_line_number,
                        code_evidence=f"def {fn.name}(...)",
                    )
                )
        return findings


# ==============================================================================
# RULE-013: Potential hard-coded credential/token pattern
# ==============================================================================
class Rule013HardcodedCredentials(ASTRule):
    SUSPICIOUS_NAMES = re.compile(
        r"^(api_key|apikey|secret_key|secret|password|auth_token|access_token|private_key)$",
        re.IGNORECASE,
    )
    TOKEN_REGEX = re.compile(r"^(sk_live_|ghp_|xoxb-|AIzaSy)[A-Za-z0-9_\-]{16,}")

    @property
    def rule_id(self) -> str:
        return "RULE-013"

    @property
    def title(self) -> str:
        return "Potential hard-coded credential or secret token"

    @property
    def category(self) -> Category:
        return Category.SECURITY

    @property
    def severity(self) -> Severity:
        return Severity.HIGH

    @property
    def description(self) -> str:
        return "Hardcoded passwords, API keys, or secret tokens committed to source code risk credential leakage."

    @property
    def recommendation(self) -> str:
        return "Store secrets in environment variables or a secret management service and access via os.getenv()."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        try:
            tree = ast.parse(source_file.content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    # Check target variable name
                    target_name = ""
                    if isinstance(node, ast.Assign) and len(node.targets) > 0 and isinstance(node.targets[0], ast.Name):
                        target_name = node.targets[0].id
                    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                        target_name = node.target.id

                    val_node = getattr(node, "value", None)
                    if target_name and isinstance(val_node, ast.Constant) and isinstance(val_node.value, str):
                        str_val = val_node.value
                        # Flag if variable name matches secret naming AND value is a non-empty string (>5 chars, not a placeholder)
                        is_suspicious_var = bool(self.SUSPICIOUS_NAMES.match(target_name))
                        is_known_token = bool(self.TOKEN_REGEX.match(str_val))
                        is_trivial_placeholder = str_val.lower() in ("placeholder", "none", "env", "test", "your_api_key_here", "dummy", "xxx")

                        if (is_suspicious_var and len(str_val) >= 8 and not is_trivial_placeholder) or is_known_token:
                            findings.append(
                                self.create_finding(
                                    message=f"Variable '{target_name}' appears to contain a hardcoded credential or secret token.",
                                    line_number=node.lineno,
                                    code_evidence=f"{target_name} = '***'",
                                )
                            )
        except Exception:
            pass
        return findings


# ==============================================================================
# RULE-014: Potential SQL injection signal
# ==============================================================================
class Rule014SqlInjectionSignal(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-014"

    @property
    def title(self) -> str:
        return "Potential SQL injection in database query construction"

    @property
    def category(self) -> Category:
        return Category.SECURITY

    @property
    def severity(self) -> Severity:
        return Severity.HIGH

    @property
    def description(self) -> str:
        return "Dynamically concatenating variables or formatting f-strings into SQL execution calls risks SQL injection."

    @property
    def recommendation(self) -> str:
        return "Use parameterized queries (e.g. cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))) instead of string formatting."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        try:
            tree = ast.parse(source_file.content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check for cursor.execute or connection.execute
                    is_sql_call = False
                    if isinstance(node.func, ast.Attribute) and node.func.attr in ("execute", "executemany"):
                        is_sql_call = True

                    if is_sql_call and len(node.args) > 0:
                        first_arg = node.args[0]
                        # Check if first argument is a BinOp string concatenation or an f-string (JoinedStr)
                        has_concatenation = isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Add)
                        has_fstring = isinstance(first_arg, ast.JoinedStr)

                        if has_concatenation or has_fstring:
                            findings.append(
                                self.create_finding(
                                    message="Database execution call uses dynamic string formatting or concatenation.",
                                    line_number=node.lineno,
                                    code_evidence="cursor.execute(...)",
                                )
                            )
        except Exception:
            pass
        return findings


# ==============================================================================
# RULE-015: Potential inefficient nested loop iteration
# ==============================================================================
class Rule015NestedLoopPerformance(ASTRule):
    @property
    def rule_id(self) -> str:
        return "RULE-015"

    @property
    def title(self) -> str:
        return "Potentially expensive nested iteration pattern"

    @property
    def category(self) -> Category:
        return Category.PERFORMANCE

    @property
    def severity(self) -> Severity:
        return Severity.MEDIUM

    @property
    def description(self) -> str:
        return "Nested loops operating over dynamic collections yield O(n²) or worse time complexity for large datasets."

    @property
    def recommendation(self) -> str:
        return "Consider using sets, hash maps, or vectorized lookup structures to reduce nested lookup complexity from O(n²) to O(n)."

    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        findings = []
        try:
            tree = ast.parse(source_file.content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                    # Inspect inner body for another loop
                    for inner in node.body:
                        if isinstance(inner, (ast.For, ast.AsyncFor, ast.While)):
                            findings.append(
                                self.create_finding(
                                    message="Nested loop construct detected. May cause quadratic O(n²) performance bottlenecks.",
                                    line_number=inner.lineno,
                                    code_evidence="for ...: for ...:",
                                )
                            )
        except Exception:
            pass
        return findings


def get_all_ast_rules(settings: Settings) -> List[ASTRule]:
    """Factory returning instances of all 15 custom AST rules."""
    return [
        Rule001Eval(settings=settings),
        Rule002Exec(settings=settings),
        Rule003DynamicImport(settings=settings),
        Rule004OsSystem(settings=settings),
        Rule005UnsafeSubprocess(settings=settings),
        Rule006UnsafePickle(settings=settings),
        Rule007BroadException(settings=settings),
        Rule008MutableDefaultArg(settings=settings),
        Rule009BareExcept(settings=settings),
        Rule010ExcessiveComplexity(settings=settings),
        Rule011ExcessiveNesting(settings=settings),
        Rule012TooManyParameters(settings=settings),
        Rule013HardcodedCredentials(settings=settings),
        Rule014SqlInjectionSignal(settings=settings),
        Rule015NestedLoopPerformance(settings=settings),
    ]
