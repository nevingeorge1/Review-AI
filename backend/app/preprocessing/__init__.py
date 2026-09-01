"""Preprocessing and AST intelligence package for ReviewAI."""

from backend.app.preprocessing.base import Preprocessor
from backend.app.preprocessing.models import (
    CallRecord,
    ClassRecord,
    CodeContext,
    CodeMetrics,
    ControlFlowSummary,
    FunctionMetrics,
    FunctionRecord,
    ImportRecord,
    ParameterRecord,
    PotentiallyInterestingCall,
    PreprocessingResult,
    SyntaxErrorInfo,
    VariableRecord,
)
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor

__all__ = [
    # Contracts & Preprocessors
    "Preprocessor",
    "PythonPreprocessor",
    # Data Models
    "CallRecord",
    "ClassRecord",
    "CodeContext",
    "CodeMetrics",
    "ControlFlowSummary",
    "FunctionMetrics",
    "FunctionRecord",
    "ImportRecord",
    "ParameterRecord",
    "PotentiallyInterestingCall",
    "PreprocessingResult",
    "SyntaxErrorInfo",
    "VariableRecord",
]
