"""Verify that the custom hook distinguishes Python code from string contents."""

from pathlib import Path

import pytest
from scripts.check_function_spacing import check_file, find_blank_lines, main


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("def task():\n    first = 1\n\n    return first\n", [3]),
        ("async def task():\n    first = 1\n    \n    return first\n", [3]),
        ("class Task:\n    def run(self):\n        first = 1\n\n        return first\n", [4]),
        ("def first():\n    return 1\n\n\ndef second():\n    return 2\n", []),
        (
            'def task():\n    """Summary.\n\n'
            '    Returns\n    -------\n    int\n        Value.\n    """\n    return 1\n',
            [],
        ),
        ('def task():\n    text = """first\n\nlast"""\n    return text\n', []),
        ('def task():\n    text = f"""first\n\n{1}"""\n    return text\n', []),
        ('def task():\n    """Summary.\n\n    Details.\n    """\n\n    return 1\n', [6]),
        ("def outer():\n    def inner():\n        first = 1\n\n        return first\n    return inner()\n", [4]),
        ("# A comment\n\nvalue = 1\n", []),
    ],
)
def test_find_blank_lines(source: str, expected: list[int]) -> None:
    """Find blank code lines and preserve separators inside text literals."""
    assert find_blank_lines(source) == expected


def test_report_invalid_python(tmp_path: Path) -> None:
    """Return a useful diagnostic when a file cannot be parsed."""
    path = tmp_path / "invalid.py"
    path.write_text("def broken(:\n", encoding="utf-8")
    diagnostics = check_file(path)
    assert len(diagnostics) == 1
    assert str(path) in diagnostics[0]
    assert "invalid syntax" in diagnostics[0]


def test_report_missing_file(tmp_path: Path) -> None:
    """Report unreadable files instead of silently skipping them."""
    assert check_file(tmp_path / "missing.py")


def test_hook_fails_and_reports_line(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Return a failing status with the exact offending source line."""
    path = tmp_path / "bad.py"
    path.write_text("def task():\n    first = 1\n\n    return first\n", encoding="utf-8")
    assert main([str(path)]) == 1
    assert f"{path}:3:" in capsys.readouterr().out


def test_hook_accepts_valid_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Return success without diagnostics for a valid function."""
    path = tmp_path / "good.py"
    path.write_text("def task():\n    return 1\n", encoding="utf-8")
    assert main([str(path)]) == 0
    assert capsys.readouterr().out == ""
