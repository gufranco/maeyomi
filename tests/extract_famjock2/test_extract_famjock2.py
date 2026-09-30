"""Tests for the tool that writes Family Jockey 2's barcode tables from its ROM.

No ROM is committed, so these build a blank image, plant a key table and a
Namco box pattern where the game keeps them, and check the tool reads them.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_famjock2.py"
ROM_SIZE = 0x20000
FAMICOM_BOX = "4907892000"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("extract_famjock2", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def planted(tool: ModuleType) -> bytes:
    rom = bytearray(ROM_SIZE)
    start = tool.BANK * tool.BANK_SIZE - tool.BANK_START
    rows = bytes(value for row in range(10) for value in range(row, row + 7))
    rom[start + tool.RACEHORSE_KEYS : start + tool.RACEHORSE_KEYS + 70] = rows
    pattern = bytes(~int(digit) & 0xFF for digit in FAMICOM_BOX)
    rom[start + tool.BOXES : start + tool.BOXES + 10] = pattern
    return bytes(rom)


def test_a_key_table_is_read_as_ten_rows_of_seven() -> None:
    tool = load()

    keys = tool.keys(planted(tool), tool.RACEHORSE_KEYS)

    assert keys[0] == (0, 1, 2, 3, 4, 5, 6)
    assert keys[9] == (9, 10, 11, 12, 13, 14, 15)
    assert len(keys) == 10


def test_a_box_pattern_is_read_back_as_its_digits() -> None:
    tool = load()

    boxes = tool.boxes(planted(tool))

    assert boxes[0] == FAMICOM_BOX
    assert len(boxes) == 7


def test_the_tables_are_read_from_the_bytes() -> None:
    tool = load()

    text = tool.render(planted(tool))

    assert "RACEHORSE_KEYS: Final = ((0, 1, 2, 3, 4, 5, 6)," in text
    assert "MARE_KEYS: Final = ((0, 0, 0, 0, 0, 0, 0)," in text
    assert "BOXES: Final = ('4907892000'," in text
