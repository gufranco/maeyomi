"""Tests for the tool that writes Battle Space's tables from its ROM.

No ROM is committed, so these build a blank image and plant each table where
the game keeps it, then check the tool reads each one from the bytes.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_barcode_boy.py"
BANK_SIZE = 0x10000


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("extract_barcode_boy", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def planted(tool: ModuleType) -> bytearray:
    rom = bytearray(BANK_SIZE)
    rom[tool.FIRST_THRESHOLDS : tool.FIRST_THRESHOLDS + 8] = bytes.fromhex("8813f401f401f401")
    rom[tool.STEPS : tool.STEPS + 6] = bytes([1, 2, 7, 8, 12, 255])
    rom[tool.CLASS_MAP] = 5
    rom[tool.CLASS_DATA + tool.MAGIC_BYTE] = 0x80
    rom[tool.CLASS_DATA + tool.SPECIAL_BYTE] = 0x30
    name = 0x5000
    rom[name : name + 8] = bytes([0x62, 0x3E, 0x40, 0x53, 0x40, 0x4E, 0x40, 0xFF])
    rom[tool.NAME_POINTERS : tool.NAME_POINTERS + 2] = name.to_bytes(2, "little")
    return rom


def test_a_name_is_decoded_with_the_voicing_mark_on_the_letter_before() -> None:
    tool = load()

    text = tool.name_at(bytes(planted(tool)), 0x5000)

    assert text == "バーサーカー"


@pytest.mark.parametrize(
    ("byte", "expected"),
    [
        (0x00, "0"),
        (0x0A, "あ"),
        (0x37, "ん"),
        (0x49, "ア"),
        (0x76, "ン"),
        (0x7D, "ュ"),
        (0x40, "ー"),
    ],
)
def test_each_range_of_the_character_set_decodes(byte: int, expected: str) -> None:
    assert load().character(byte) == expected


def test_a_code_outside_the_character_set_is_shown_rather_than_guessed() -> None:
    assert load().character(0x79) == "?79"


def test_a_pointer_outside_the_bank_names_nothing() -> None:
    assert load().name_at(bytes(BANK_SIZE), 0x0100) == ""


def test_a_voicing_mark_with_no_letter_before_it_is_dropped() -> None:
    rom = bytearray(BANK_SIZE)
    rom[0x5000:0x5003] = bytes([0x3E, 0x49, 0xFF])

    text = load().name_at(bytes(rom), 0x5000)

    assert text == "ア"


def test_the_tables_are_read_from_the_bytes() -> None:
    tool = load()

    text = tool.render(bytes(planted(tool)))

    assert "FIRST_THRESHOLDS: Final = (5000, 500, 500, 500)" in text
    assert "STEPS: Final = (1, 2, 7, 8, 12, 255)" in text
    assert "CLASS_MAP: Final = (5, 0," in text
    assert "MAGIC_GROUPS: Final = (2, 0," in text
    assert "SPECIALS: Final = (2, -1," in text
    assert "CLASS_NAMES: Final = ('バーサーカー', ''," in text
