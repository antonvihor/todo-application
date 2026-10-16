"""Reject blank code lines in functions while preserving multiline strings."""

import argparse
import ast
import sys
from pathlib import Path


def find_blank_lines(source: str) -> list[int]:
    """Find blank lines inside synchronous and asynchronous functions.

    Parameters
    ----------
    source : str
        Python source code to inspect.

    Returns
    -------
    list of int
        Sorted one-based line numbers, excluding multiline string contents.
    """
    tree = ast.parse(source)
    nodes = list(ast.walk(tree))
    string_lines = {
        line
        for node in nodes
        if isinstance(node, ast.JoinedStr) or (isinstance(node, ast.Constant) and isinstance(node.value, str))
        for line in range(node.lineno, (node.end_lineno or node.lineno) + 1)
    }
    function_lines = {
        line
        for node in nodes
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        for line in range(node.lineno, (node.end_lineno or node.lineno) + 1)
    }
    return [
        number
        for number, line in enumerate(source.splitlines(), start=1)
        if number in function_lines and number not in string_lines and not line.strip()
    ]


def check_file(path: Path) -> list[str]:
    """Read a Python file and report spacing or parsing errors.

    Parameters
    ----------
    path : Path
        Source file to inspect.

    Returns
    -------
    list of str
        Diagnostics suitable for pre-commit output.
    """
    try:
        return [
            f"{path}:{line}: blank lines inside functions are not allowed"
            for line in find_blank_lines(path.read_text(encoding="utf-8"))
        ]
    except (OSError, SyntaxError, UnicodeError) as error:
        return [f"{path}: {error}"]


def main(paths: list[str]) -> int:
    """Check the Python files supplied on the command line.

    Parameters
    ----------
    paths : list[str]
        Command-line arguments containing the files to inspect.

    Returns
    -------
    int
        Zero on success and one when a file fails validation.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filenames", nargs="+", help="Python files to check")
    errors = [error for filename in parser.parse_args(paths).filenames for error in check_file(Path(filename))]
    for error in errors:
        print(error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
