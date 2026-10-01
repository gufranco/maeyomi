"""Write the tables Barcode Taisen Bardigun reads a barcode with, straight from its ROM.

Usage: uv run python tools/oracle/extract_bardigun.py --rompath DIR --out FILE

Bank 4 $6B26 picks the creature an egg hatches into: the eleventh digit, 1 to
7, chooses one of seven tables of ten, and the check digit the entry; 0 draws
at random from the first thirty entries. Each creature's record, through the
pointer table at bank $0D $4000, ends with the four numbers and the HP it
hatches with, and its name sits behind the pointer table at bank 9 $4006, in
the game's own katakana. The English names are this project's romanisation.
"""

import argparse
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

from maeyomi.romaji import romanised

ARTIFACT: Final = "gameboy_bardigun"
ROM_PATH: Final = "gbcolor/barcode/dmg-abej-0.u1"
BANK_SIZE: Final = 0x4000
BANK_START: Final = 0x4000
SPECIES_BANK: Final = 4
SPECIES_TABLES: Final = {
    1: 0x6BD4,
    2: 0x6BDE,
    3: 0x6BE8,
    4: 0x6BF2,
    5: 0x6C10,
    6: 0x6BFC,
    7: 0x6C06,
}
TABLE_SIZE: Final = 10
RANDOM_SIZE: Final = 30
RECORD_BANK: Final = 0x0D
RECORD_POINTERS: Final = 0x4000
NAME_BANK: Final = 9
NAME_POINTERS: Final = 0x4006
SPECIES: Final = 161
START_PLACE: Final = 17
START_SIZE: Final = 5
KATAKANA: Final = (
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモラリルレロワヤユヨン"
)
FIRST_KANA: Final = 0x81
SMALL: Final = dict(zip(range(0xAE, 0xB7), "ァィゥェォャュョッ", strict=True))
LONG: Final = 0xFC
VOICED: Final = 0x01
SEMI_VOICED: Final = 0x02
END: Final = 0x00
VOICE: Final = dict(
    zip(
        "カキクケコサシスセソタチツテトハヒフヘホウ",
        "ガギグゲゴザジズゼゾダヂヅデドバビブベボヴ",
        strict=True,
    )
)
SEMI: Final = dict(zip("ハヒフヘホ", "パピプペポ", strict=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(
        args.rompath, ARTIFACT, "place the barcode set dumped from your cartridge there"
    )
    rom = (args.rompath / ROM_PATH).read_bytes()
    args.out.write_text(render(rom), encoding="utf-8")


def render(rom: bytes) -> str:
    names_found = names(rom)
    lines = [
        '"""The tables Barcode Taisen Bardigun reads a barcode with.',
        "",
        "Written from the game's ROM by tools/oracle/extract_bardigun.py; regenerate",
        "rather than edit. A species table is ten creatures picked by the check digit;",
        "a start is power, smarts, toughness, speed and HP at level 1.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"SPECIES_TABLES: Final = {species_tables(rom)}",
        f"RANDOM_POOL: Final = {random_pool(rom)}",
        f"NAMES: Final = {names_found}",
        f"ENGLISH: Final = {tuple(romanised(name) for name in names_found)}",
        f"STARTS: Final = {starts(rom)}",
        "",
    ]
    return "\n".join(lines)


def offset(bank: int, address: int) -> int:
    return bank * BANK_SIZE + address - BANK_START


def word(rom: bytes, bank: int, address: int) -> int:
    place = offset(bank, address)
    return rom[place] | rom[place + 1] << 8


def species_tables(rom: bytes) -> dict[int, tuple[int, ...]]:
    return {
        digit: tuple(
            rom[offset(SPECIES_BANK, address) : offset(SPECIES_BANK, address) + TABLE_SIZE]
        )
        for digit, address in SPECIES_TABLES.items()
    }


def random_pool(rom: bytes) -> tuple[int, ...]:
    start = offset(SPECIES_BANK, SPECIES_TABLES[1])
    return tuple(rom[start : start + RANDOM_SIZE])


def names(rom: bytes) -> tuple[str, ...]:
    return tuple(
        decoded(_string(rom, word(rom, NAME_BANK, NAME_POINTERS + 2 * species)))
        for species in range(SPECIES)
    )


def _string(rom: bytes, address: int) -> bytes:
    start = offset(NAME_BANK, address)
    return rom[start : rom.index(END, start)]


def decoded(raw: bytes) -> str:
    text, mark = "", 0
    for byte in raw:
        if byte in {VOICED, SEMI_VOICED}:
            mark = byte
            continue
        character = _character(byte)
        table = VOICE if mark == VOICED else SEMI if mark == SEMI_VOICED else {}
        text += table.get(character, character)
        mark = 0
    return text


def _character(byte: int) -> str:
    if byte == LONG:
        return "ー"
    if byte in SMALL:
        return SMALL[byte]
    return KATAKANA[byte - FIRST_KANA]


def starts(rom: bytes) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(
            rom[
                offset(RECORD_BANK, word(rom, RECORD_BANK, RECORD_POINTERS + 2 * species))
                + START_PLACE : offset(
                    RECORD_BANK, word(rom, RECORD_BANK, RECORD_POINTERS + 2 * species)
                )
                + START_PLACE
                + START_SIZE
            ]
        )
        for species in range(SPECIES)
    )


if __name__ == "__main__":
    main()
