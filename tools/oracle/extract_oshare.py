"""Write the tables Oshare Majo Love and Berry DS Collection reads a card with, from its ROM.

Usage: uv run python tools/oracle/extract_oshare.py --rompath DIR --out PATH

The game reads the Code 39 text of each card through four alphabets of 44
characters kept at $0209DFC0 in the ARM9 program, which is stored uncompressed.
An item is named by a category, a two-letter code from that category's table
and a number; the dress, footwear and special tables sit behind the pointers
at $0209DF10, $0209DEF4 and $0209DEDC, and the short form a card starting N
and ending A takes uses its own at $0209DF44, $0209DEE8 and $0209DF00. Every item the game can show has a card
image under game/card in the cartridge's file system, named by its code, so
the list of items is read from the file name table.
"""

import argparse
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

ARTIFACT: Final = "nds_oshare"
ROM_PATH: Final = "nds/oshare.nds"
FIELD_SIZE: Final = 4
SHORT_SIZE: Final = 2
ARM9_OFFSET_FIELD: Final = 0x20
ARM9_ADDRESS_FIELD: Final = 0x28
FNT_OFFSET_FIELD: Final = 0x40
ALPHABETS_ADDRESS: Final = 0x0209DFC0
ALPHABET_SIZE: Final = 44
ALPHABETS: Final = 4
CODE_TABLES: Final = {
    "dress": 0x0209DF10,
    "footwear": 0x0209DEF4,
    "special": 0x0209DEDC,
    "short_dress": 0x0209DF44,
    "short_footwear": 0x0209DEE8,
    "short_special": 0x0209DF00,
}
CODE_COUNTS: Final = {
    "dress": 7,
    "footwear": 7,
    "special": 6,
    "short_dress": 7,
    "short_footwear": 3,
    "short_special": 4,
}
CODE_SIZE: Final = 2
MAIN_ENTRY: Final = 8
DIRECTORY_FLAG: Final = 0x80
DIRECTORY_BASE: Final = 0xF000
CARD_FOLDER: Final = "card"
CARD_SUFFIX: Final = ".crd"
MAX_DEPTH: Final = 8


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(args.rompath, ARTIFACT, "place the game dumped from your cartridge there")
    rom = (args.rompath / ROM_PATH).read_bytes()
    args.out.write_text(render(rom), encoding="utf-8")


def render(rom: bytes) -> str:
    tables = {name: code_table(rom, name, CODE_COUNTS[name]) for name in CODE_TABLES}
    lines = [
        '"""The tables Oshare Majo Love and Berry DS Collection reads a card with.',
        "",
        "Written from the game's ROM by tools/oracle/extract_oshare.py; regenerate",
        "rather than edit. CARD_FILES is every card image the game keeps, by folder",
        "and item code.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"ALPHABETS: Final = {alphabets(rom)}",
        f"DRESS_CODES: Final = {tables['dress']}",
        f"FOOTWEAR_CODES: Final = {tables['footwear']}",
        f"SPECIAL_CODES: Final = {tables['special']}",
        f"SHORT_DRESS_CODES: Final = {tables['short_dress']}",
        f"SHORT_FOOTWEAR_CODES: Final = {tables['short_footwear']}",
        f"SHORT_SPECIAL_CODES: Final = {tables['short_special']}",
        f"CARD_FILES: Final[tuple[tuple[str, str], ...]] = {card_files(rom)}",
        "",
    ]
    return "\n".join(lines)


def _number(rom: bytes, place: int, size: int = FIELD_SIZE) -> int:
    return int.from_bytes(rom[place : place + size], "little")


def _offset(rom: bytes, address: int) -> int:
    return address - _number(rom, ARM9_ADDRESS_FIELD) + _number(rom, ARM9_OFFSET_FIELD)


def alphabets(rom: bytes) -> tuple[str, ...]:
    start = _offset(rom, ALPHABETS_ADDRESS)
    return tuple(
        rom[start + ALPHABET_SIZE * index : start + ALPHABET_SIZE * (index + 1)].decode("latin1")
        for index in range(ALPHABETS)
    )


def code_table(rom: bytes, name: str, count: int) -> tuple[str, ...]:
    table = _offset(rom, CODE_TABLES[name])
    pointers = (_number(rom, table + FIELD_SIZE * index) for index in range(count))
    return tuple(
        rom[_offset(rom, pointer) : _offset(rom, pointer) + CODE_SIZE]
        .split(b"\x00")[0]
        .decode("latin1")
        for pointer in pointers
    )


def _entries(rom: bytes, fnt: int, directory: int) -> list[tuple[str, int | None]]:
    """The names in one directory, each with its own directory number or None for a file."""
    place = fnt + _number(rom, fnt + MAIN_ENTRY * (directory - DIRECTORY_BASE))
    found: list[tuple[str, int | None]] = []
    while rom[place]:
        size = rom[place] & ~DIRECTORY_FLAG
        is_directory = bool(rom[place] & DIRECTORY_FLAG)
        name = rom[place + 1 : place + 1 + size].decode("latin1")
        place += 1 + size
        child = _number(rom, place, SHORT_SIZE) if is_directory else None
        place += SHORT_SIZE if is_directory else 0
        found = [*found, (name, child)]
    return found


def _walk(rom: bytes, fnt: int, directory: int, path: tuple[str, ...]) -> list[tuple[str, ...]]:
    """Every file path under a directory, depth first, in table order."""
    if len(path) > MAX_DEPTH:
        return []
    paths: list[tuple[str, ...]] = []
    for name, child in _entries(rom, fnt, directory):
        paths = paths + (
            [(*path, name)] if child is None else _walk(rom, fnt, child, (*path, name))
        )
    return paths


def card_files(rom: bytes) -> tuple[tuple[str, str], ...]:
    paths = _walk(rom, _number(rom, FNT_OFFSET_FIELD), DIRECTORY_BASE, ())
    return tuple(
        (path[-2], path[-1].removesuffix(CARD_SUFFIX))
        for path in paths
        if len(path) > 2 and path[-3] == CARD_FOLDER and path[-1].endswith(CARD_SUFFIX)
    )


if __name__ == "__main__":
    main()
