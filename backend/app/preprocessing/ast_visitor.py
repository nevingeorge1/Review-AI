"""Single-pass AST Visitor extracting structural elements, control flow, and signals."""

import ast
from typing import Any, List, Optional

from backend.app.preprocessing.metrics import (
    calculate_function_metrics,
    estimate_node_cyclomatic_complexity,
)
from backend.app.preprocessing.models import (
    CallRecord,
    ClassRecord,
    ControlFlowSummary,
    FunctionRecord,
    ImportRecord,
    ParameterRecord,
    PotentiallyInterestingCall,
    VariableRecord,
)
from backend.app.preprocessing.signals import classify_interesting_call


def _resolve_attribute_chain(node: ast.AST) -> str:
    """Helper converting an AST Call func node to attribute chain string (e.g. 'os.path.join')."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        parent = _resolve_attribute_chain(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    elif isinstance(node, ast.Call):
        return _resolve_attribute_chain(node.func)
    return ""


def _extract_decorator_name(dec_node: ast.AST) -> str:
    """Extract string name from a decorator AST node."""
    if isinstance(dec_node, ast.Name):
        return dec_node.id
    elif isinstance(dec_node, ast.Attribute):
        return _resolve_attribute_chain(dec_node)
    elif isinstance(dec_node, ast.Call):
        return _resolve_attribute_chain(dec_node.func)
    return "decorator"


def _format_annotation(ann_node: Optional[ast.AST]) -> Optional[str]:
    """Convert AST type annotation node to human-readable string."""
    if ann_node is None:
        return None
    try:
        return ast.unparse(ann_node)
    except Exception:
        if isinstance(ann_node, ast.Name):
            return ann_node.id
        return None


class PythonASTVisitor(ast.NodeVisitor):
    """AST Visitor extracting comprehensive structural and semantic context in a single pass."""

    def __init__(self, source_code: str) -> None:
        self.source_code = source_code
        self.imports: List[ImportRecord] = []
        self.functions: List[FunctionRecord] = []
        self.classes: List[ClassRecord] = []
        self.variables: List[VariableRecord] = []
        self.calls: List[CallRecord] = []
        self.interesting_signals: List[PotentiallyInterestingCall] = []

        # Control flow counters
        self.if_count = 0
        self.for_count = 0
        self.while_count = 0
        self.try_count = 0
        self.except_count = 0
        self.with_count = 0
        self.return_count = 0
        self.raise_count = 0
        self.break_count = 0
        self.continue_count = 0
        self.comprehension_count = 0

        # Scope & Nesting tracking
        self.scope_stack: List[str] = ["module"]
        self.current_class: Optional[str] = None
        self.nesting_depth = 0
        self.max_nesting_depth = 0

    def _enter_nesting(self) -> None:
        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)

    def _exit_nesting(self) -> None:
        self.nesting_depth = max(0, self.nesting_depth - 1)

    # --- Imports ---

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                ImportRecord(
                    module=None,
                    name=alias.name,
                    alias=alias.asname,
                    is_from_import=False,
                    line_number=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module_name = node.module or ""
        for alias in node.names:
            self.imports.append(
                ImportRecord(
                    module=module_name,
                    name=alias.name,
                    alias=alias.asname,
                    is_from_import=True,
                    line_number=node.lineno,
                )
            )
        self.generic_visit(node)

    # --- Classes ---

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        prev_class = self.current_class
        self.current_class = node.name
        self.scope_stack.append(f"class:{node.name}")
        self._enter_nesting()

        base_classes: List[str] = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(_resolve_attribute_chain(base))

        decorators = [_extract_decorator_name(dec) for dec in node.decorator_list]
        docstring = ast.get_docstring(node)

        # Inspect immediate methods
        methods = [
            n.name
            for n in node.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        class_rec = ClassRecord(
            name=node.name,
            line_number=node.lineno,
            end_line_number=getattr(node, "end_lineno", node.lineno),
            base_classes=base_classes,
            decorators=decorators,
            methods=methods,
            method_count=len(methods),
            has_docstring=docstring is not None,
            docstring=docstring,
        )
        self.classes.append(class_rec)

        self.generic_visit(node)

        self._exit_nesting()
        self.scope_stack.pop()
        self.current_class = prev_class

    # --- Functions ---

    def _process_function(self, node: Any, is_async: bool) -> None:
        is_nested = len([s for s in self.scope_stack if s.startswith("func:")]) > 0
        self.scope_stack.append(f"func:{node.name}")
        self._enter_nesting()

        # Extract parameters
        parameters: List[ParameterRecord] = []
        args = node.args

        # Positional & Standard arguments
        for arg in args.posonlyargs + args.args:
            parameters.append(
                ParameterRecord(
                    name=arg.arg,
                    type_annotation=_format_annotation(arg.annotation),
                )
            )

        # *args
        if args.vararg:
            parameters.append(
                ParameterRecord(
                    name=args.vararg.arg,
                    type_annotation=_format_annotation(args.vararg.annotation),
                    is_args=True,
                )
            )

        # Keyword-only arguments
        for arg in args.kwonlyargs:
            parameters.append(
                ParameterRecord(
                    name=arg.arg,
                    type_annotation=_format_annotation(arg.annotation),
                    is_keyword_only=True,
                )
            )

        # **kwargs
        if args.kwarg:
            parameters.append(
                ParameterRecord(
                    name=args.kwarg.arg,
                    type_annotation=_format_annotation(args.kwarg.annotation),
                    is_kwargs=True,
                )
            )

        decorators = [_extract_decorator_name(dec) for dec in node.decorator_list]
        docstring = ast.get_docstring(node)
        return_ann = _format_annotation(getattr(node, "returns", None))
        metrics = calculate_function_metrics(node, self.source_code)

        func_rec = FunctionRecord(
            name=node.name,
            line_number=node.lineno,
            end_line_number=getattr(node, "end_lineno", node.lineno),
            is_async=is_async,
            parameters=parameters,
            parameter_count=len(parameters),
            return_annotation=return_ann,
            decorators=decorators,
            has_docstring=docstring is not None,
            docstring=docstring,
            is_nested=is_nested,
            parent_class=self.current_class,
            metrics=metrics,
        )
        self.functions.append(func_rec)

        self.generic_visit(node)

        self._exit_nesting()
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function(node, is_async=True)

    # --- Variables & Assignments ---

    def visit_Assign(self, node: ast.Assign) -> None:
        current_scope = self.scope_stack[-1].split(":")[0]
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append(
                    VariableRecord(
                        name=target.id,
                        line_number=node.lineno,
                        assignment_type="Assign",
                        scope=current_scope,
                    )
                )
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        current_scope = self.scope_stack[-1].split(":")[0]
        if isinstance(node.target, ast.Name):
            self.variables.append(
                VariableRecord(
                    name=node.target.id,
                    line_number=node.lineno,
                    assignment_type="AnnAssign",
                    type_annotation=_format_annotation(node.annotation),
                    scope=current_scope,
                )
            )
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        current_scope = self.scope_stack[-1].split(":")[0]
        if isinstance(node.target, ast.Name):
            self.variables.append(
                VariableRecord(
                    name=node.target.id,
                    line_number=node.lineno,
                    assignment_type="AugAssign",
                    scope=current_scope,
                )
            )
        self.generic_visit(node)

    # --- Calls & Interesting Signals ---

    def visit_Call(self, node: ast.Call) -> None:
        call_chain = _resolve_attribute_chain(node.func)
        short_name = call_chain.split(".")[-1] if call_chain else "call"
        kw_args = [kw.arg for kw in node.keywords if kw.arg]

        call_rec = CallRecord(
            name=short_name,
            full_attribute_chain=call_chain or short_name,
            line_number=node.lineno,
            arg_count=len(node.args),
            keyword_args=kw_args,
        )
        self.calls.append(call_rec)

        # Check against dangerous / interesting calls catalog
        signal_info = classify_interesting_call(call_chain or short_name)
        if signal_info:
            category, description = signal_info
            args_preview = None
            try:
                args_preview = ", ".join([ast.unparse(a) for a in node.args[:2]])
            except Exception:
                pass

            self.interesting_signals.append(
                PotentiallyInterestingCall(
                    name=call_chain or short_name,
                    category=category,
                    line_number=node.lineno,
                    description=description,
                    arguments_preview=args_preview,
                )
            )

        self.generic_visit(node)

    # --- Control Flow ---

    def visit_If(self, node: ast.If) -> None:
        self.if_count += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_For(self, node: ast.For) -> None:
        self.for_count += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.for_count += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_While(self, node: ast.While) -> None:
        self.while_count += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_Try(self, node: ast.Try) -> None:
        self.try_count += 1
        self.except_count += len(node.handlers)
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_With(self, node: ast.With) -> None:
        self.with_count += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self.with_count += 1
        self._enter_nesting()
        self.generic_visit(node)
        self._exit_nesting()

    def visit_Return(self, node: ast.Return) -> None:
        self.return_count += 1
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        self.raise_count += 1
        self.generic_visit(node)

    def visit_Break(self, node: ast.Break) -> None:
        self.break_count += 1
        self.generic_visit(node)

    def visit_Continue(self, node: ast.Continue) -> None:
        self.continue_count += 1
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self.comprehension_count += 1
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self.comprehension_count += 1
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self.comprehension_count += 1
        self.generic_visit(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self.comprehension_count += 1
        self.generic_visit(node)

    def get_control_flow_summary(self) -> ControlFlowSummary:
        """Return aggregate summary of control flow statements."""
        return ControlFlowSummary(
            if_count=self.if_count,
            for_count=self.for_count,
            while_count=self.while_count,
            try_count=self.try_count,
            except_count=self.except_count,
            with_count=self.with_count,
            return_count=self.return_count,
            raise_count=self.raise_count,
            break_count=self.break_count,
            continue_count=self.continue_count,
            comprehension_count=self.comprehension_count,
            max_nesting_depth=self.max_nesting_depth,
        )
