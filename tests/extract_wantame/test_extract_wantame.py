"""Tests for the tool that writes Wantame Music Channel's card tables from its ROM.

No ROM is committed, so these build a blank image holding one card record in
the first table, an empty record after it and the strings the record points
at, and check the tool reads them back.
"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_wantame.py"
ROM_SIZE = 0xD0000
ARM9_OFFSET = 0x4000
ARM9_ADDRESS = 0x2000000
STRINGS = 0x2080000


def load() -> ModuleType:
    sys.path.insert(0, str(TOOL.parent))
    spec = importlib.util.spec_from_file_location("extract_wantame", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def at(address: int) -> int:
    return address - ARM9_ADDRESS + ARM9_OFFSET


def planted(tool: ModuleType) -> bytes:
    rom = bytearray(ROM_SIZE)
    rom[0x20:0x24] = ARM9_OFFSET.to_bytes(4, "little")
    rom[0x28:0x2C] = ARM9_ADDRESS.to_bytes(4, "little")
    rom[0x2C:0x30] = (ROM_SIZE - ARM9_OFFSET).to_bytes(4, "little")
    strings = {STRINGS: "チワワ", STRINGS + 0x40: "002"}
    for address, text in strings.items():
        raw = text.encode("shift_jis") + b"\x00"
        rom[at(address) : at(address) + len(raw)] = raw
    first = tool.TABLES[0]
    record = b"".join(
        value.to_bytes(4, "little") for value in (1, 0, 0x12884427, 0x111, STRINGS, STRINGS + 0x40)
    )
    rom[at(first.address) : at(first.address) + len(record)] = record
    return bytes(rom)


def test_a_record_is_read_with_its_code_name_and_number() -> None:
    tool = load()

    cards = tool.cards(planted(tool))

    assert cards[0] == (0x11, 0, "011112884427", "チワワ", "002")


def test_a_record_with_no_code_is_left_out() -> None:
    tool = load()

    cards = tool.cards(planted(tool))

    assert len(cards) == 1


def test_a_code_prints_its_first_pair_from_the_highest_bits() -> None:
    assert load().code_of(0x28531729, 0x0111) == "011128531729"


def test_the_tables_module_lists_the_cards() -> None:
    tool = load()

    text = tool.render(planted(tool))

    assert "CARDS: Final[tuple[tuple[int, int, str, str, str], ...]] = (" in text
    assert "チワワ" in text


def test_a_full_width_sign_is_written_as_an_escape() -> None:
    assert load().escaped("しばいぬ（くろ）×") == "しばいぬ\\uff08くろ\\uff09\\u00d7"
