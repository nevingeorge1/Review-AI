"""Abstract preprocessor and input sanitization contracts."""

from abc import ABC, abstractmethod
from typing import Tuple
from backend.app.models.domain import CodeSubmission, SourceFile


class Preprocessor(ABC):
    """Abstract interface for source code preprocessing and sanitization pipeline."""

    @abstractmethod
    def preprocess(self, submission: CodeSubmission) -> SourceFile:
        """
        Sanitize and normalize a raw submission into an internal SourceFile.

        Performs:
        1. UTF-8 normalization and null-byte checks.
        2. Line count & byte size limit enforcement.
        3. Line ending normalization.
        4. Metadata calculation.
        """
        pass
