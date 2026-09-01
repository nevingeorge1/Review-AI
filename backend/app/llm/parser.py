"""Robust parser and defensive validator for LLM structured JSON output."""

import json
import re
import uuid
from typing import List, Optional, Tuple

from backend.app.core.errors import InvalidStructuredOutputError
from backend.app.core.logging import logger
from backend.app.llm.models import LLMRawFinding, LLMRawResponsePayload
from backend.app.models.domain import ReviewFinding, SuggestedFix
from backend.app.models.enums import DetectionSource


class LLMOutputParser:
    """Parses raw text from LLMs into validated, type-safe domain ReviewFinding records."""

    @staticmethod
    def extract_json_string(raw_text: str) -> str:
        """
        Extract JSON payload from markdown fences or surrounding conversational text.
        """
        if not raw_text or not raw_text.strip():
            raise InvalidStructuredOutputError(provider="llm", message="LLM returned an empty response")

        text = raw_text.strip()

        # 1. Match ```json ... ``` or ``` ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if fence_match:
            candidate = fence_match.group(1).strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return candidate

        # 2. Match outermost balanced { ... }
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return text[start_idx : end_idx + 1].strip()

        return text

    def parse_and_validate(
        self,
        raw_text: str,
        total_source_lines: int = 500,
    ) -> Tuple[str, List[ReviewFinding]]:
        """
        Parse raw LLM output and convert into validated domain ReviewFinding instances.

        Args:
            raw_text: Raw output string from the LLM provider.
            total_source_lines: Total lines in original source code for line-bounds validation.

        Returns:
            Tuple of (executive_summary, List[ReviewFinding]).

        Raises:
            InvalidStructuredOutputError: If JSON decoding or schema parsing fails fatally.
        """
        json_str = self.extract_json_string(raw_text)

        try:
            parsed_data = json.loads(json_str)
        except json.JSONDecodeError as err:
            logger.warning("LLM response is not valid JSON: %s (first 100 chars: %s)", err, repr(json_str[:100]))
            raise InvalidStructuredOutputError(
                provider="llm",
                message=f"Failed to parse JSON from LLM output: {err.msg} at line {err.lineno}, col {err.colno}",
            ) from err

        if not isinstance(parsed_data, dict):
            raise InvalidStructuredOutputError(
                provider="llm",
                message=f"Expected JSON object at top level, received {type(parsed_data).__name__}",
            )

        try:
            payload = LLMRawResponsePayload.model_validate(parsed_data)
        except Exception as err:
            logger.warning("LLM JSON payload failed schema validation: %s", err)
            raise InvalidStructuredOutputError(
                provider="llm",
                message=f"LLM JSON response violated required schema: {err}",
            ) from err

        executive_summary = payload.executive_summary or "LLM code review completed."
        validated_findings: List[ReviewFinding] = []

        for raw_finding in payload.findings:
            try:
                finding = self._convert_and_validate_finding(raw_finding, total_source_lines)
                if finding:
                    validated_findings.append(finding)
            except Exception as err:
                logger.warning("Skipping malformed LLM finding item: %s", err)

        return executive_summary, validated_findings

    def _convert_and_validate_finding(
        self,
        raw: LLMRawFinding,
        total_source_lines: int,
    ) -> Optional[ReviewFinding]:
        """
        Validate line bounds, convert suggested fixes, and construct pure domain ReviewFinding.
        """
        # Defensive Line Number Validation & Clamping
        line_no = raw.line_number
        end_line = raw.end_line

        if line_no is not None:
            if line_no < 1 or line_no > total_source_lines:
                logger.debug("Omitted invalid LLM line number %d (file has %d lines)", line_no, total_source_lines)
                line_no = None
                end_line = None
            elif end_line is not None:
                if end_line < line_no:
                    end_line = line_no
                if end_line > total_source_lines:
                    end_line = total_source_lines

        # Suggested Fix conversion
        suggested_fix = None
        if raw.suggested_fix:
            suggested_fix = SuggestedFix(
                original_snippet=raw.suggested_fix.original_snippet,
                replacement_snippet=raw.suggested_fix.replacement_snippet,
                explanation=raw.suggested_fix.explanation,
                diff=raw.suggested_fix.diff,
            )

        # Title and description sanity
        title = raw.title.strip() if raw.title else "Code Review Insight"
        description = raw.description.strip() if raw.description else "No detailed description provided."

        return ReviewFinding(
            id=str(uuid.uuid4()),
            category=raw.category,
            severity=raw.severity,
            title=title[:150],
            description=description,
            line_number=line_no,
            end_line=end_line,
            code_evidence=raw.code_evidence,
            explanation=raw.explanation or raw.reasoning or "Identified through LLM semantic code reasoning.",
            recommendation=raw.recommendation or "Consider reviewing this section against best practices.",
            suggested_fix=suggested_fix,
            confidence=raw.confidence,
            detection_source=DetectionSource.LLM,
            rule_id=None,
            supporting_evidence=[],
        )
