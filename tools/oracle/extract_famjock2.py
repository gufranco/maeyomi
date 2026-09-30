"""Write the tables Family Jockey 2 reads a barcode with, straight from its ROM.

Usage: uv run python tools/oracle/extract_famjock2.py --rompath DIR --out FILE

The game turns a code into a horse with one of three key tables in bank 2, one
per menu the card is read in: 10 rows of 7 keys, picked by the digit sum. It
also knows seven box codes of Namco's own games, stored complemented, first ten
digits only, which earn a bonus.
"""

import argparse
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

ARTIFACT: Final = "gameboy_famjock2"
ROM_PATH: Final = "gameboy/famjock2/dmg-fvj-0.u1"
BANK: Final = 2
BANK_SIZE: Final = 0x4000
BANK_START: Final = 0x4000
RACEHORSE_KEYS: Final = 0x5190
MARE_KEYS: Final = 0x521E
STALLION_KEYS: Final = 0x52AC
ROWS: Final = 10
ROW_SIZE: Final = 7
BOXES: Final = 0x50EF
BOX_COUNT: Final = 7
BOX_DIGITS: Final = 10
BYTE: Final = 0xFF


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(
        args.rompath, ARTIFACT, "place the famjock2 set dumped from your cartridge there"
    )
    rom = (args.rompath / ROM_PATH).read_bytes()
    args.out.write_text(render(rom), encoding="utf-8")


def render(rom: bytes) -> str:
    lines = [
        '"""The tables Family Jockey 2 reads a barcode with.',
        "",
        "Written from the game's ROM by tools/oracle/extract_famjock2.py; regenerate",
        "rather than edit. A key table is ten rows of seven, one row per digit sum;",
        "a box is the first ten digits of a Namco game's own barcode.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"RACEHORSE_KEYS: Final = {keys(rom, RACEHORSE_KEYS)}",
        f"MARE_KEYS: Final = {keys(rom, MARE_KEYS)}",
        f"STALLION_KEYS: Final = {keys(rom, STALLION_KEYS)}",
        f"BOXES: Final = {boxes(rom)}",
        "",
    ]
    return "\n".join(lines)


def at(rom: bytes, address: int) -> int:
    return rom[BANK * BANK_SIZE + address - BANK_START]


def keys(rom: bytes, address: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(at(rom, address + ROW_SIZE * row + index) for index in range(ROW_SIZE))
        for row in range(ROWS)
    )


def boxes(rom: bytes) -> tuple[str, ...]:
    return tuple(
        "".join(
            str(~at(rom, BOXES + BOX_DIGITS * box + index) & BYTE) for index in range(BOX_DIGITS)
        )
        for box in range(BOX_COUNT)
    )


if __name__ == "__main__":
    main()
