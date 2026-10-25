import ast
from pathlib import Path

from maeyomi.cli.main import app

TESTS_ROOT = Path(__file__).resolve().parents[1]


def _command_name(call: ast.Call) -> str | None:
    if not isinstance(call.func, ast.Attribute) or call.func.attr != "invoke":
        return None
    if len(call.args) < 2:
        return None
    argv = call.args[1]
    if not isinstance(argv, ast.List) or not argv.elts:
        return None
    first = argv.elts[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    return None


def _invoked_commands() -> set[str]:
    invoked: set[str] = set()
    for path in TESTS_ROOT.rglob("test_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = _command_name(node)
                if name is not None:
                    invoked.add(name)
    return invoked


def _registered_commands() -> set[str]:
    return {
        command.callback.__name__
        for command in app.registered_commands
        if command.callback is not None
    }


def test_every_cli_command_has_an_end_to_end_invocation() -> None:
    # Arrange
    registered = _registered_commands()

    # Act
    invoked = _invoked_commands()

    # Assert
    assert registered - invoked == set()
