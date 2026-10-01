"""Tests for the reader of a DS cartridge's file system.

No ROM is committed, so these build a blank image holding a small file name
table and allocation table, and check every path and file comes back.
"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "nitro_fs.py"
ROM_SIZE = 0x2000
FNT = 0x1000
FAT = 0x1800
FIRST_FILE = 0x1C00
SECOND_FILE = 0x1D00


def load() -> ModuleType:
    sys.path.insert(0, str(TOOL.parent))
    spec = importlib.util.spec_from_file_location("nitro_fs", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def image() -> bytes:
    """A root holding a.bin and a directory data, which holds b.bin."""
    rom = bytearray(ROM_SIZE)
    main = (16).to_bytes(4, "little") + (0).to_bytes(2, "little") + (2).to_bytes(2, "little")
    main += (30).to_bytes(4, "little") + (1).to_bytes(2, "little") + (0xF000).to_bytes(2, "little")
    root = (
        bytes([5]) + b"a.bin" + bytes([0x84]) + b"data" + (0xF001).to_bytes(2, "little") + b"\x00"
    )
    data = bytes([5]) + b"b.bin" + b"\x00"
    table = main + root + data
    rom[FNT : FNT + len(table)] = table
    rom[0x40:0x44] = FNT.to_bytes(4, "little")
    rom[0x44:0x48] = len(table).to_bytes(4, "little")
    rom[0x48:0x4C] = FAT.to_bytes(4, "little")
    rom[0x4C:0x50] = (16).to_bytes(4, "little")
    for index, (start, contents) in enumerate(((FIRST_FILE, b"first"), (SECOND_FILE, b"second"))):
        entry = FAT + 8 * index
        rom[entry : entry + 4] = start.to_bytes(4, "little")
        rom[entry + 4 : entry + 8] = (start + len(contents)).to_bytes(4, "little")
        rom[start : start + len(contents)] = contents
    return bytes(rom)


def test_every_path_comes_with_its_file_number() -> None:
    files = load().files(image())

    assert files == ((("a.bin",), 0), (("data", "b.bin"), 1))


def test_a_file_is_read_by_its_path() -> None:
    contents = load().read_file(image(), ("data", "b.bin"))

    assert contents == b"second"


def test_a_missing_path_is_refused() -> None:
    with pytest.raises(KeyError, match=r"c\.bin"):
        load().read_file(image(), ("data", "c.bin"))
