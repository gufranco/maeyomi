"""Tests for the tool that writes Mushiking's card lists from its ROM.

No ROM is committed, so these build a blank image holding the barcode file in
a one-file cartridge file system, the names the game keeps and the two lists
it keeps in its program, and check the tool reads them back.
"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_mushiking.py"
ROM_SIZE = 0x140000
ARM9_OFFSET = 0x4000
ARM9_ADDRESS = 0x2000000
FNT = 0x120000
FAT = 0x121000
FILE = 0x122000
NAMES = 0x10E000


def load() -> ModuleType:
    sys.path.insert(0, str(TOOL.parent))
    spec = importlib.util.spec_from_file_location("extract_mushiking", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def at(address: int) -> int:
    return address - ARM9_ADDRESS + ARM9_OFFSET


def barcode_file(tool: ModuleType) -> bytes:
    contents = bytearray(b"0" * tool.FILE_SIZE)
    first = tool.LISTS[0]
    contents[first.codes : first.codes + 26] = b"GRFCT20K03W02ME1KAFKUSZFFF"
    contents[first.data : first.data + 32] = b"00100200100100010020020780020001"
    return bytes(contents)


def name_table() -> bytes:
    root = bytes([0x84]) + b"data" + (0xF001).to_bytes(2, "little") + b"\x00"
    data = bytes([0x87]) + b"barcode" + (0xF002).to_bytes(2, "little") + b"\x00"
    barcode = bytes([13]) + b"m_barcode.bin" + b"\x00"
    offsets = [24, 24 + len(root), 24 + len(root) + len(data)]
    entries = b"".join(
        offset.to_bytes(4, "little") + (0).to_bytes(2, "little") + (0xF000).to_bytes(2, "little")
        for offset in offsets
    )
    return entries + root + data + barcode


def planted(tool: ModuleType) -> bytes:
    rom = bytearray(ROM_SIZE)
    rom[0x20:0x24] = ARM9_OFFSET.to_bytes(4, "little")
    rom[0x28:0x2C] = ARM9_ADDRESS.to_bytes(4, "little")
    table = name_table()
    rom[FNT : FNT + len(table)] = table
    rom[0x40:0x44] = FNT.to_bytes(4, "little")
    rom[0x48:0x4C] = FAT.to_bytes(4, "little")
    contents = barcode_file(tool)
    rom[FAT : FAT + 4] = FILE.to_bytes(4, "little")
    rom[FAT + 4 : FAT + 8] = (FILE + len(contents)).to_bytes(4, "little")
    rom[FILE : FILE + len(contents)] = contents
    names = {10: "ギラファノコギリクワガタ", 87: "ムシキング"}
    for index, name in names.items():
        string = NAMES + 64 * index
        raw = name.encode("shift_jis") + b"\x00"
        rom[string : string + len(raw)] = raw
        pointer = at(tool.NAMES_ADDRESS) + 4 * index
        rom[pointer : pointer + 4] = (string - ARM9_OFFSET + ARM9_ADDRESS).to_bytes(4, "little")
    special = at(tool.SPECIAL_ADDRESSES[0])
    rom[special : special + 13] = b"MDXY9CY4F6DS1"
    return bytes(rom)


def test_a_list_is_read_as_thirteen_character_codes() -> None:
    tool = load()

    codes = tool.codes(planted(tool))

    assert codes[0][:2] == ("GRFCT20K03W02", "ME1KAFKUSZFFF")


def test_a_beetle_card_is_named_through_its_data_record() -> None:
    tool = load()

    names = tool.names(planted(tool))

    assert names[0][:2] == ("ギラファノコギリクワガタ", "ムシキング")


def test_a_list_kept_in_the_program_is_read_from_it() -> None:
    tool = load()

    assert tool.codes(planted(tool))[5][0] == "MDXY9CY4F6DS1"


def test_the_tables_module_lists_codes_and_names() -> None:
    tool = load()

    text = tool.render(planted(tool))

    assert "CODES: Final[tuple[tuple[str, ...], ...]] = (" in text
    assert "NAMES: Final[tuple[tuple[str, ...], ...]] = (" in text
    assert "SERIES: Final[tuple[str, ...]] = (" in text


def test_the_first_list_keeps_each_cards_series() -> None:
    tool = load()

    assert tool.series(planted(tool))[:2] == ("002", "002")


def test_a_full_width_letter_is_written_as_an_escape() -> None:
    assert load().escaped("チャン・Ｇ") == "チャン・\\uff27"
