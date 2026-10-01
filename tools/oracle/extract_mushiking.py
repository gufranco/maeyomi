"""Write the card lists Kouchuu Ouja Mushiking Super Collection reads a card against, from its ROM.

Usage: uv run python tools/oracle/extract_mushiking.py --rompath DIR --out PATH

The game keeps five lists in data/barcode/m_barcode.bin, a text file its
loader at $0201F7EC cuts at fixed offsets into thirteen-character codes and a
data record per code, and two more lists of thirteen-character codes in its
ARM9 program, which is stored uncompressed. Characters 6 to 8 of a data record
in the first three lists number the beetle or character on the card; the game
names it from the pointer array at $0210F488, nine entries past that number.
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from nitro_fs import read_file
from record_game import verify_artifact

ARTIFACT: Final = "nds_mushiking"
ROM_PATH: Final = "nds/mushiking.nds"
BARCODE_FILE: Final = ("data", "barcode", "m_barcode.bin")
FILE_SIZE: Final = 16399
CODE_SIZE: Final = 13
FIELD_SIZE: Final = 4
ARM9_OFFSET_FIELD: Final = 0x20
ARM9_ADDRESS_FIELD: Final = 0x28
NAMES_ADDRESS: Final = 0x0210F488
NAME_SHIFT: Final = 9
NAMED_LISTS: Final = 3
NAME_FIELD: Final = slice(6, 9)
SERIES_FIELD: Final = slice(3, 6)
NAME_LIMIT: Final = 64
SPECIAL_ADDRESSES: Final = (0x0210BBA4, 0x0210BBD4)
SPECIAL_COUNTS: Final = (3, 8)
SPECIAL_STRIDE: Final = 16
FULL_WIDTH_LATIN: Final = range(0xFF21, 0xFF5B)


@dataclass(frozen=True, slots=True)
class CardList:
    """Where one list's codes and data records sit in the barcode file."""

    codes: int
    data: int
    count: int
    record: int


LISTS: Final = (
    CardList(0x3667, 0, 190, 16),
    CardList(0x2F97, 0x32A5, 60, 16),
    CardList(0xBE2, 0xD5D, 29, 16),
    CardList(0xFD5, 0x1BFA, 239, 21),
    CardList(0xF2F, 0xF7F, 6, 14),
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(args.rompath, ARTIFACT, "place the game dumped from your cartridge there")
    rom = (args.rompath / ROM_PATH).read_bytes()
    args.out.write_text(render(rom), encoding="utf-8")


def render(rom: bytes) -> str:
    lines = [
        '"""The card lists Kouchuu Ouja Mushiking Super Collection reads a card against.',
        "",
        "Written from the game's ROM by tools/oracle/extract_mushiking.py; regenerate",
        "rather than edit. CODES holds the seven lists in the game's order; NAMES holds",
        "the beetle or character each card of the first three lists shows; SERIES holds",
        "the series field of each data record in the first list.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"CODES: Final[tuple[tuple[str, ...], ...]] = {codes(rom)}",
        f"NAMES: Final[tuple[tuple[str, ...], ...]] = {escaped(repr(names(rom)))}",
        f"SERIES: Final[tuple[str, ...]] = {series(rom)}",
        "",
    ]
    return "\n".join(lines)


def escaped(text: str) -> str:
    """Python source with full-width Latin letters written as escapes, as a linter wants them."""
    return "".join(
        f"\\u{ord(character):04x}" if ord(character) in FULL_WIDTH_LATIN else character
        for character in text
    )


def _number(rom: bytes, place: int) -> int:
    return int.from_bytes(rom[place : place + FIELD_SIZE], "little")


def _offset(rom: bytes, address: int) -> int:
    return address - _number(rom, ARM9_ADDRESS_FIELD) + _number(rom, ARM9_OFFSET_FIELD)


def _cut(text: bytes, start: int, count: int, size: int) -> tuple[str, ...]:
    return tuple(
        text[start + size * index : start + size * (index + 1)].decode("ascii")
        for index in range(count)
    )


def codes(rom: bytes) -> tuple[tuple[str, ...], ...]:
    contents = read_file(rom, BARCODE_FILE)
    filed = tuple(_cut(contents, card.codes, card.count, CODE_SIZE) for card in LISTS)
    kept = tuple(
        _cut(rom, _offset(rom, address), count, SPECIAL_STRIDE)
        for address, count in zip(SPECIAL_ADDRESSES, SPECIAL_COUNTS, strict=True)
    )
    return filed + tuple(tuple(code[:CODE_SIZE] for code in group) for group in kept)


def _name(rom: bytes, index: int) -> str:
    pointer = _number(rom, _offset(rom, NAMES_ADDRESS) + FIELD_SIZE * index)
    start = _offset(rom, pointer)
    return rom[start : start + NAME_LIMIT].split(b"\x00")[0].decode("shift_jis")


def names(rom: bytes) -> tuple[tuple[str, ...], ...]:
    contents = read_file(rom, BARCODE_FILE)
    return tuple(
        tuple(
            _name(rom, int(record[NAME_FIELD]) + NAME_SHIFT)
            for record in _cut(contents, card.data, card.count, card.record)
        )
        for card in LISTS[:NAMED_LISTS]
    )


def series(rom: bytes) -> tuple[str, ...]:
    contents = read_file(rom, BARCODE_FILE)
    first = LISTS[0]
    return tuple(
        record[SERIES_FIELD] for record in _cut(contents, first.data, first.count, first.record)
    )


if __name__ == "__main__":
    main()
