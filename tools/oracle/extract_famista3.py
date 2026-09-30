"""Write the player tables Famista 3 reads a barcode with, straight from its ROM.

Usage: uv run python tools/oracle/extract_famista3.py --rompath DIR --out FILE

A scanned code points into the player data in bank $0A: one of four bases for
batters or four for pitchers, chosen by a digit through tables in bank 8, plus a
step of 9 bytes for a batter or 14 for a pitcher. Every place a code can point
is read here, keeping what the game shows: a batter's side, average in
thousandths, home runs and speed, a pitcher's side, ERA in hundredths, pitch
speed and stamina.
"""

import argparse
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

ARTIFACT: Final = "gameboy_famista3"
ROM_PATH: Final = "gameboy/famista3/dmg-n3j-0.u1"
BANK_SIZE: Final = 0x4000
BANK_START: Final = 0x4000
CODE_BANK: Final = 8
DATA_BANK: Final = 0x0A
KINDS: Final = 0x456F
SIZES: Final = 0x459B
DIGITS: Final = 10
STEPS: Final = 256
BATTER_KIND: Final = 0
PITCHER_KIND: Final = 1
SIDE: Final = 4
FIRST_NUMBER: Final = 5
BATTER_FIELDS: Final = (7, 8)
PITCHER_FIELDS: Final = (9, 13)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(
        args.rompath, ARTIFACT, "place the famista3 set dumped from your cartridge there"
    )
    rom = (args.rompath / ROM_PATH).read_bytes()
    args.out.write_text(render(rom), encoding="utf-8")


def render(rom: bytes) -> str:
    sizes = (at(rom, CODE_BANK, SIZES), at(rom, CODE_BANK, SIZES + 1))
    batter_bases, batter_groups = groups(rom, BATTER_KIND)
    pitcher_bases, pitcher_groups = groups(rom, PITCHER_KIND)
    batters = tuple(
        tuple(player(rom, base + sizes[0] * step, batter=True) for step in range(STEPS))
        for base in batter_bases
    )
    pitchers = tuple(
        tuple(player(rom, base + sizes[1] * step, batter=False) for step in range(STEPS))
        for base in pitcher_bases
    )
    lines = [
        '"""The player tables Famista 3 reads a barcode with.',
        "",
        "Written from the game's ROM by tools/oracle/extract_famista3.py; regenerate",
        "rather than edit. A group is every player one base can reach, one per step:",
        "a batter as side, average in thousandths, home runs and speed, a pitcher as",
        "side, ERA in hundredths, pitch speed in km/h and stamina.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"SIZES: Final = {sizes}",
        f"BATTER_GROUPS: Final = {batter_groups}",
        f"PITCHER_GROUPS: Final = {pitcher_groups}",
        f"BATTERS: Final = {batters}",
        f"PITCHERS: Final = {pitchers}",
        "",
    ]
    return "\n".join(lines)


def at(rom: bytes, bank: int, address: int) -> int:
    return rom[bank * BANK_SIZE + address - BANK_START]


def word(rom: bytes, bank: int, address: int) -> int:
    return at(rom, bank, address) | at(rom, bank, address + 1) << 8


def groups(rom: bytes, kind: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    table = word(rom, CODE_BANK, KINDS + 2 * kind)
    bases = [word(rom, CODE_BANK, table + 2 * digit) for digit in range(DIGITS)]
    unique = tuple(dict.fromkeys(bases))
    return unique, tuple(unique.index(base) for base in bases)


def player(rom: bytes, address: int, *, batter: bool) -> tuple[int, int, int, int]:
    first, second = BATTER_FIELDS if batter else PITCHER_FIELDS
    return (
        at(rom, DATA_BANK, address + SIDE),
        word(rom, DATA_BANK, address + FIRST_NUMBER),
        at(rom, DATA_BANK, address + first),
        at(rom, DATA_BANK, address + second),
    )


if __name__ == "__main__":
    main()
