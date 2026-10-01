"""Tests for the tool that writes Barcode Taisen Bardigun's tables from its ROM.

No ROM is committed, so these build a blank image, plant a species table, a
name and a creature record where the game keeps them, and check the tool reads
them back.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_bardigun.py"
ROM_SIZE = 0x100000
TAKORA = bytes([0x90, 0x8A, 0xA4, 0x00])
CHIBISSHII = bytes([0x91, 0x01, 0x9B, 0xB6, 0x8C, 0xFC])


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("extract_bardigun", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def at(tool: ModuleType, bank: int, address: int) -> int:
    return bank * tool.BANK_SIZE + address - tool.BANK_START


def planted(tool: ModuleType) -> bytes:
    rom = bytearray(ROM_SIZE)
    table = at(tool, tool.SPECIES_BANK, tool.SPECIES_TABLES[4])
    rom[table : table + 10] = bytes([14, 40, 66, 94, 97, 14, 40, 66, 94, 97])
    pointers = at(tool, tool.NAME_BANK, tool.NAME_POINTERS)
    rom[pointers + 28 : pointers + 30] = (0x5000).to_bytes(2, "little")
    name = at(tool, tool.NAME_BANK, 0x5000)
    rom[name : name + len(TAKORA)] = TAKORA
    records = at(tool, tool.RECORD_BANK, tool.RECORD_POINTERS)
    rom[records + 28 : records + 30] = (0x6000).to_bytes(2, "little")
    record = at(tool, tool.RECORD_BANK, 0x6000)
    rom[record + tool.START_PLACE : record + tool.START_PLACE + 5] = bytes([7, 5, 5, 5, 90])
    return bytes(rom)


def test_a_species_table_is_read_as_ten_species() -> None:
    tool = load()

    tables = tool.species_tables(planted(tool))

    assert tables[4] == (14, 40, 66, 94, 97, 14, 40, 66, 94, 97)


def test_a_name_is_read_through_its_pointer() -> None:
    tool = load()

    assert tool.names(planted(tool))[14] == "タコラ"


def test_a_voiced_mark_and_a_small_kana_are_joined() -> None:
    assert load().decoded(CHIBISSHII) == "チビッシー"


def test_a_species_starts_with_the_numbers_its_record_holds() -> None:
    tool = load()

    assert tool.starts(planted(tool))[14] == (7, 5, 5, 5, 90)


def test_the_tables_file_holds_every_table() -> None:
    tool = load()

    text = tool.render(planted(tool))

    assert "SPECIES_TABLES: Final = " in text
    assert "NAMES: Final = " in text
    assert "ENGLISH: Final = " in text
    assert "STARTS: Final = " in text
    assert "RANDOM_POOL: Final = " in text
