"""Tests for the tool that writes Card de Asobu's card codes from its ROM.

No ROM is committed, so these build a blank image with an ARM9 header, plant a
pointer table and the codes it points at where the game keeps them, and check
the tool reads them back.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_cardasobu.py"
ROM_SIZE = 0x100000
ARM9_OFFSET = 0x4000
ARM9_ADDRESS = 0x2000000
STRINGS = 0x83000
PLANTED = ("AA01C0RD00", "ZZZZZZZZZZ", "AA47CKRC00")


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("extract_cardasobu", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def planted(tool: ModuleType) -> bytes:
    rom = bytearray(ROM_SIZE)
    rom[0x20:0x24] = ARM9_OFFSET.to_bytes(4, "little")
    rom[0x28:0x2C] = ARM9_ADDRESS.to_bytes(4, "little")
    table = tool.TABLE_ADDRESS - ARM9_ADDRESS + ARM9_OFFSET
    for index, code in enumerate(PLANTED):
        place = STRINGS + index * tool.ENTRY_SIZE
        rom[place : place + len(code)] = code.encode("ascii")
        pointer = place - ARM9_OFFSET + ARM9_ADDRESS
        rom[table + 4 * index : table + 4 * index + 4] = pointer.to_bytes(4, "little")
    return bytes(rom)


def test_every_code_is_read_through_its_pointer_in_table_order() -> None:
    tool = load()

    codes = tool.codes(planted(tool))

    assert codes == PLANTED


def test_the_table_ends_at_the_first_empty_pointer() -> None:
    tool = load()

    assert len(tool.codes(planted(tool))) == len(PLANTED)


def test_the_tables_module_lists_the_codes() -> None:
    tool = load()

    text = tool.render(planted(tool))

    assert "CODES: Final = ('AA01C0RD00', 'ZZZZZZZZZZ', 'AA47CKRC00')" in text
