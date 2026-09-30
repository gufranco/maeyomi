"""Write the car tables Kattobi Road reads a barcode with, straight from its ROM.

Usage: uv run python tools/oracle/extract_kattobi.py --rompath DIR --out FILE

The game keeps 256 car models of 32 bytes in bank 3 from $6000, and a scanned
code picks one. Each starts with an 8-byte name in JIS X 0201 half-width
katakana and ASCII, then its category, a byte, and its power, torque and weight
as little-endian words. The category names are ASCII in bank 0. The English
names are this project's romanisation, made by rule from the game's own.
"""

import argparse
import sys
import unicodedata
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

from maeyomi.romaji import romanised

ARTIFACT: Final = "gameboy_kattobi"
ROM_PATH: Final = "gameboy/kattobi/dmg-k5j-0.u1"
MODELS: Final = 0xE000
MODEL_SIZE: Final = 32
MODEL_COUNT: Final = 256
NAME_SIZE: Final = 8
CATEGORY_BYTE: Final = 8
POWER: Final = 10
TORQUE: Final = 12
WEIGHT: Final = 14
CATEGORY_NAMES: Final = 0x39F9
CATEGORY_SIZE: Final = 9
CATEGORY_COUNT: Final = 5


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(
        args.rompath, ARTIFACT, "place the kattobi set dumped from your cartridge there"
    )
    rom = (args.rompath / ROM_PATH).read_bytes()
    args.out.write_text(render(rom), encoding="utf-8")


def render(rom: bytes) -> str:
    records = [
        rom[MODELS + MODEL_SIZE * index : MODELS + MODEL_SIZE * (index + 1)]
        for index in range(MODEL_COUNT)
    ]
    names = tuple(name_of(record[:NAME_SIZE]) for record in records)
    lines = [
        '"""The car tables Kattobi Road reads a barcode with.',
        "",
        "Written from the game's ROM by tools/oracle/extract_kattobi.py; regenerate",
        "rather than edit. A model is its category, power in PS, torque in tenths of",
        "a kg-m and weight in kg; the English names are romanised by rule.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"NAMES: Final = {names}",
        f"ENGLISH: Final = {tuple(romanised(name) for name in names)}",
        f"MODELS: Final = {tuple(model_of(record) for record in records)}",
        f"CATEGORIES: Final = {categories(rom)}",
        "",
    ]
    return "\n".join(lines)


def name_of(raw: bytes) -> str:
    return unicodedata.normalize("NFKC", raw.decode("shift_jis")).strip()


def model_of(record: bytes) -> tuple[int, int, int, int]:
    word = lambda offset: record[offset] | record[offset + 1] << 8  # noqa: E731
    return record[CATEGORY_BYTE], word(POWER), word(TORQUE), word(WEIGHT)


def categories(rom: bytes) -> tuple[str, ...]:
    return tuple(
        rom[CATEGORY_NAMES + CATEGORY_SIZE * index : CATEGORY_NAMES + CATEGORY_SIZE * (index + 1)]
        .rstrip(b"\x00")
        .decode("ascii")
        .strip()
        for index in range(CATEGORY_COUNT)
    )


if __name__ == "__main__":
    main()
