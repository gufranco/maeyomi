"""Tests for the tool that writes Ryuusei no Rockman's Wave Card list from GBE+'s notes."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_rockman.py"
NOTES = """Standard Cards
------------------------------------------------------------
Card ID\t| Barcode\t| English Name\t\t\t| Japanese Name
------------------------------------------------------------
S-001\t| 040000060019\t| Canon\t\t\t\t| キャノン
S-002\t| 400000060026\t| Plus Canon\t\t\t| プラスキャノン
------------------------------------------------------------

Character Cards
------------------------------------------------------------
C-11\t| 040000240032\t| Harp Note\t\t\t| ハープ・ノート
------------------------------------------------------------
"""


def load() -> ModuleType:
    sys.path.insert(0, str(TOOL.parent))
    spec = importlib.util.spec_from_file_location("extract_rockman", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_listed_card_is_read_with_its_number_code_and_names() -> None:
    cards = load().cards(NOTES)

    assert cards == (
        ("S-001", "060019", "Canon", "キャノン"),
        ("S-002", "060026", "Plus Canon", "プラスキャノン"),
        ("C-11", "240032", "Harp Note", "ハープ・ノート"),
    )


def test_a_line_outside_the_tables_is_ignored() -> None:
    assert load().cards("Card ID\t| Barcode\t| English Name\t| Japanese Name\n") == ()


def test_the_tables_module_lists_the_cards() -> None:
    text = load().render(NOTES)

    assert "CARDS: Final[tuple[tuple[str, str, str, str], ...]] = (" in text
    assert "ハープ・ノート" in text


def test_a_full_width_sign_is_written_as_an_escape() -> None:
    assert load().escaped("アクア＋50") == "アクア\\uff0b50"
