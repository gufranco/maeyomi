"""Tests for the tool that writes Monster Maker's tables from its ROM.

No ROM is committed, so these build a blank image and plant each table where
the game keeps it, then check the tool reads each one from the bytes.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_monster_maker.py"
ROM_SIZE = 0x20000
BLANK_ROW = bytes([0xFE] * 8)
HAGEN = bytes([0xFE, 0xFE, 0xE3, 0xFE, 0xFE, 0xFE, 0xFE, 0xFE]) + bytes(
    [0xD5, 0xF0, 0xC4, 0xE9, 0xFE, 0xFE, 0xFE, 0xFE]
)
LORIEN = BLANK_ROW + bytes([0xE6, 0xB1, 0xBF, 0xF0, 0xE9, 0xFE, 0xFE, 0xFE])
DRAGON_KNIGHT = BLANK_ROW + bytes([0xB1, 0xBA, 0x8C, 0x90, 0x95, 0xFE, 0xFE, 0xFE])
LORIEN_FIRST_LEVEL = bytes([0x02, 0x3C, 0x00, 0x35, 0x96, 0x00])
HARPY = bytes([0x05, 0x46, 0x28, 0x00, 0x18, 0x01, 0x18, 0x01, 0x00, 0x30])


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("extract_monster_maker", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def planted(tool: ModuleType) -> bytes:
    rom = bytearray(ROM_SIZE)
    rom[tool.NAMES : tool.NAMES + 16] = HAGEN
    rom[tool.NAMES + 16 : tool.NAMES + 32] = LORIEN
    rom[tool.CLASS_NAMES + 32 : tool.CLASS_NAMES + 48] = DRAGON_KNIGHT
    rom[tool.CLASSES] = 3
    rom[tool.HERO_STATS : tool.HERO_STATS + 6] = LORIEN_FIRST_LEVEL
    rom[tool.MONSTER_STATS : tool.MONSTER_STATS + 10] = HARPY
    return bytes(rom)


def test_a_voicing_mark_above_a_letter_voices_it() -> None:
    tool = load()

    name = tool.text_at(planted(tool), tool.NAMES)

    assert name == "ハーゲン"


def test_the_shared_ri_tile_beside_katakana_is_katakana() -> None:
    tool = load()

    name = tool.text_at(planted(tool), tool.NAMES + 16)

    assert name == "ロリエーン"


def test_the_shared_ri_tile_among_hiragana_stays_hiragana() -> None:
    tool = load()

    name = tool.text_at(planted(tool), tool.CLASS_NAMES + 32)

    assert name == "りゅうきし"


def test_a_semi_voicing_mark_is_applied() -> None:
    assert load().voiced("ホ", 0xE8) == "ポ"


@pytest.mark.parametrize(
    ("byte", "expected"),
    [
        (0x80, "0"),
        (0x89, "9"),
        (0x8A, "あ"),
        (0xBB, "ょ"),
        (0xBC, "ア"),
        (0xDF, "ヤ"),
        (0xF0, "ー"),
    ],
)
def test_each_range_of_the_character_set_decodes(byte: int, expected: str) -> None:
    assert load().character(byte) == expected


def test_a_code_outside_the_character_set_is_shown_rather_than_guessed() -> None:
    assert load().character(0x05) == "?05"


def test_the_tables_are_read_from_the_bytes() -> None:
    tool = load()

    text = tool.render(planted(tool))

    assert "NAMES: Final = ('ハーゲン', 'ロリエーン', '?00" in text
    assert ", 'りゅうきし', '?00" in text
    assert "CLASSES: Final = (3, 0," in text
    assert "HERO_STATS: Final = (((2, 60, 0, 53, 150), (0, 0, 0, 0, 0)," in text
    assert "MONSTER_STATS: Final = ((5, 70, 40, 0, 280), (0, 0, 0, 0, 0)," in text
