"""Tests for the tool that writes Kattobi Road's car tables from its ROM.

No ROM is committed, so these build a blank image and plant a car where the
game keeps its models, then check the tool reads it from the bytes.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_kattobi.py"
ROM_SIZE = 0x20000
TRUCK = bytes.fromhex("ccabdcb0d9c4de20" + "0326" + "fa00" + "bc02" + "320f") + bytes(16)
CATEGORIES = b"FORMULA \x00 K-CAR  \x00 NORMAL \x00 TRUCK  \x00SPECIAL \x00"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("extract_kattobi", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def planted(tool: ModuleType) -> bytes:
    rom = bytearray(ROM_SIZE)
    rom[tool.MODELS : tool.MODELS + 32] = TRUCK
    rom[tool.CATEGORY_NAMES : tool.CATEGORY_NAMES + len(CATEGORIES)] = CATEGORIES
    return bytes(rom)


def test_a_half_width_name_is_read_with_its_voicing_mark_joined() -> None:
    assert load().name_of(TRUCK[:8]) == "フォワールド"


def test_a_name_with_letters_keeps_them() -> None:
    assert load().name_of(b"\xcb\xde\xc3\xde\xb5RXR") == "ビデオRXR"


@pytest.mark.parametrize(
    ("japanese", "english"),
    [
        ("フォワールド", "Fowaarudo"),
        ("ガウディ", "Gaudi"),
        ("ミイラターボ", "Miirataabo"),
        ("ビデオRXR", "Bideo RXR"),
        ("ABZ-11", "ABZ-11"),
        ("パックマンカー", "Pakkumankaa"),
        ("マッチ", "Matchi"),
        ("シェリーサボレ", "Sheriisabore"),
        ("ヴィナ", "Vina"),
        ("キャラメル", "Kyarameru"),
        ("ァ", "A"),
    ],
)
def test_a_name_is_romanised_by_rule(japanese: str, english: str) -> None:
    assert load().romanised(japanese) == english


def test_the_categories_are_read_from_the_rom() -> None:
    tool = load()

    categories = tool.categories(planted(tool))

    assert categories == ("FORMULA", "K-CAR", "NORMAL", "TRUCK", "SPECIAL")


def test_the_tables_are_read_from_the_bytes() -> None:
    tool = load()

    text = tool.render(planted(tool))

    assert "NAMES: Final = ('フォワールド'," in text
    assert "ENGLISH: Final = ('Fowaarudo'," in text
    assert "MODELS: Final = ((3, 250, 700, 3890), (0, 0, 0, 0)," in text
    assert "CATEGORIES: Final = ('FORMULA', 'K-CAR', 'NORMAL', 'TRUCK', 'SPECIAL')" in text
