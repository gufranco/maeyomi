from pathlib import Path

from importlinter import configuration
from importlinter.application import use_cases

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def test_the_architecture_contracts_hold() -> None:
    # Arrange
    configuration.configure()

    # Act
    passed = use_cases.lint_imports(config_filename=str(PYPROJECT), no_logo=True)

    # Assert
    assert passed is True
