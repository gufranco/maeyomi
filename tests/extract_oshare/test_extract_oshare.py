"""Tests for the tool that writes Oshare Majo's card tables from its ROM.

No ROM is committed, so these build a blank image with a cartridge header,
plant the four alphabets, a category's code table and a small file name table
where the game keeps them, and check the tool reads them back.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "extract_oshare.py"
ROM_SIZE = 0x140000
ARM9_OFFSET = 0x4000
ARM9_ADDRESS = 0x2000000
FNT = 0x120000
STRINGS = 0x9F000


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("extract_oshare", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def at(address: int) -> int:
    return address - ARM9_ADDRESS + ARM9_OFFSET


def name_table() -> bytes:
    """A root holding one directory, card, which holds hair, which holds two cards."""
    main = b"".join(
        [
            (24).to_bytes(4, "little") + (0).to_bytes(2, "little") + (3).to_bytes(2, "little"),
            (32).to_bytes(4, "little") + (0).to_bytes(2, "little") + (0xF000).to_bytes(2, "little"),
            (40).to_bytes(4, "little") + (0).to_bytes(2, "little") + (0xF001).to_bytes(2, "little"),
        ]
    )
    root = bytes([0x84]) + b"card" + (0xF001).to_bytes(2, "little") + b"\x00"
    card = bytes([0x84]) + b"hair" + (0xF002).to_bytes(2, "little") + b"\x00"
    hair = bytes([9]) + b"Hr027.crd" + bytes([9]) + b"HR024.crd" + b"\x00"
    return main + root + card + hair


def planted(tool: ModuleType) -> bytes:
    rom = bytearray(ROM_SIZE)
    rom[0x20:0x24] = ARM9_OFFSET.to_bytes(4, "little")
    rom[0x28:0x2C] = ARM9_ADDRESS.to_bytes(4, "little")
    rom[0x40:0x44] = FNT.to_bytes(4, "little")
    table = name_table()
    rom[0x44:0x48] = len(table).to_bytes(4, "little")
    rom[FNT : FNT + len(table)] = table
    alphabets = bytes(range(0x21, 0x21 + 4 * tool.ALPHABET_SIZE))
    place = at(tool.ALPHABETS_ADDRESS)
    rom[place : place + len(alphabets)] = alphabets
    pointers = at(tool.CODE_TABLES["footwear"])
    for index, code in enumerate(("FS", "SS")):
        string = STRINGS + 8 * index
        rom[string : string + 3] = code.encode("ascii") + b"\x00"
        rom[pointers + 4 * index : pointers + 4 * index + 4] = (
            string - ARM9_OFFSET + ARM9_ADDRESS
        ).to_bytes(4, "little")
    return bytes(rom)


def test_the_four_alphabets_are_read_in_order() -> None:
    tool = load()

    alphabets = tool.alphabets(planted(tool))

    assert alphabets[1] == bytes(range(0x21 + 44, 0x21 + 88)).decode("latin1")


def test_a_category_code_table_is_read_through_its_pointers() -> None:
    tool = load()

    codes = tool.code_table(planted(tool), "footwear", 2)

    assert codes == ("FS", "SS")


def test_the_card_images_are_listed_from_the_file_name_table() -> None:
    tool = load()

    cards = tool.card_files(planted(tool))

    assert cards == (("hair", "Hr027"), ("hair", "HR024"))
