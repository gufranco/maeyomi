"""Write the card tables Wantame Music Channel reads a card against, from its ROM.

Usage: uv run python tools/oracle/extract_wantame.py --rompath DIR --out PATH

The game keeps five card tables in its ARM9 program, which is stored
uncompressed. A record starts with its kind and its place, then the card's six
Code 128 C pairs as BCD bytes, the last pair first, then pointers to the
card's name and its number. The routine at $020430B4 picks the table by the
second pair and takes a card only when all six pairs match. A record whose
pairs are all zero is a placeholder no card can reach.
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

ARTIFACT: Final = "nds_wantame"
ROM_PATH: Final = "nds/wantame.nds"
FIELD_SIZE: Final = 4
ARM9_OFFSET_FIELD: Final = 0x20
ARM9_ADDRESS_FIELD: Final = 0x28
PAIRS: Final = 6
NAME_LIMIT: Final = 80
LOW_WORD: Final = 2
NAME_WORD: Final = 4
NUMBER_WORD: Final = 5
ESCAPED: Final = frozenset({*range(0xFF01, 0xFF5F), 0xD7})


@dataclass(frozen=True, slots=True)
class Table:
    """One card table: the pair that selects it, where it sits and its record size."""

    key: int
    address: int
    count: int
    stride: int


TABLES: Final = (
    Table(0x11, 0x02094734, 52, 0x1EC),
    Table(0x21, 0x020AD7EC, 167, 0x1B8),
    Table(0x22, 0x0209AB24, 70, 0x1B0),
    Table(0x23, 0x02094634, 2, 0x20),
    Table(0x31, 0x02094674, 6, 0x20),
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
        '"""The cards Wantame Music Channel reads.',
        "",
        "Written from the game's ROM by tools/oracle/extract_wantame.py; regenerate",
        "rather than edit. Each card is its table's selecting pair, its place in the",
        "table, its twelve digits, its name and the number printed on it.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"CARDS: Final[tuple[tuple[int, int, str, str, str], ...]] = {escaped(repr(cards(rom)))}",
        "",
    ]
    return "\n".join(lines)


def escaped(text: str) -> str:
    """Python source with full-width signs written as escapes, as a linter wants them."""
    return "".join(
        f"\\u{ord(character):04x}" if ord(character) in ESCAPED else character for character in text
    )


def _number(rom: bytes, place: int) -> int:
    return int.from_bytes(rom[place : place + FIELD_SIZE], "little")


def _offset(rom: bytes, address: int) -> int:
    return address - _number(rom, ARM9_ADDRESS_FIELD) + _number(rom, ARM9_OFFSET_FIELD)


def _text(rom: bytes, address: int) -> str:
    start = _offset(rom, address)
    return rom[start : start + NAME_LIMIT].split(b"\x00")[0].decode("shift_jis")


def code_of(low: int, high: int) -> str:
    """The twelve digits a card prints, from the two words the game stores them in."""
    pairs = (low | high << 32).to_bytes(8, "little")[:PAIRS]
    return "".join(f"{pair:02x}" for pair in reversed(pairs))


def _words(rom: bytes, table: Table, index: int) -> tuple[int, ...]:
    start = _offset(rom, table.address) + table.stride * index
    return tuple(_number(rom, start + FIELD_SIZE * word) for word in range(NUMBER_WORD + 1))


def cards(rom: bytes) -> tuple[tuple[int, int, str, str, str], ...]:
    return tuple(
        (
            table.key,
            index,
            code_of(words[LOW_WORD], words[LOW_WORD + 1]),
            _text(rom, words[NAME_WORD]),
            _text(rom, words[NUMBER_WORD]),
        )
        for table in TABLES
        for index in range(table.count)
        for words in (_words(rom, table, index),)
        if words[LOW_WORD] or words[LOW_WORD + 1]
    )


if __name__ == "__main__":
    main()
