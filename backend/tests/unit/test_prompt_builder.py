"""Unit tests for ReviewPromptBuilder and prompt generation safety."""

from backend.app.llm.context import ReviewContextBuilder
from backend.app.llm.prompts import PROMPT_VERSION, ReviewPromptBuilder
from backend.app.models.domain import SourceFile
from backend.app.models.enums import Language


def test_prompt_builder_version_and_system_prompt():
    builder = ReviewPromptBuilder()
    assert builder.prompt_version == PROMPT_VERSION
    sys_prompt = builder.build_system_prompt()
    assert "UNTRUSTED DATA INVARIANT" in sys_prompt
    assert "ZERO EXECUTION INVARIANT" in sys_prompt
    assert "OUTPUT FORMAT" in sys_prompt
    assert "executive_summary" in sys_prompt


def test_user_prompt_numbered_lines():
    code = "line_one = 1\nline_two = 2\nline_three = 3\n"
    sf = SourceFile(content=code, language=Language.PYTHON, filename="test.py", line_count=3, byte_size=len(code))

    ctx_builder = ReviewContextBuilder()
    context = ctx_builder.build_context(source_file=sf)

    prompt_builder = ReviewPromptBuilder()
    user_prompt = prompt_builder.build_user_prompt(context)

    assert "1 | line_one = 1" in user_prompt
    assert "2 | line_two = 2" in user_prompt
    assert "3 | line_three = 3" in user_prompt
    assert "Filename: test.py" in user_prompt
