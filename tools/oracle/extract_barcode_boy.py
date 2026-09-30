"""Write the tables Battle Space reads a barcode with, straight from its ROM.

Usage: uv run python tools/oracle/extract_barcode_boy.py --rompath DIR --out FILE

The addresses are where the game keeps each table, found by following the code
that runs after a scan. Every table is read from the bytes, never typed, so a
transposed entry cannot slip in, and the names are decoded with the game's own
character set.
"""

import argparse
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

ARTIFACT: Final = "gameboy_bspace"
ROM_PATH: Final = "gameboy/bspace/dmg-nxj-0.u1"
FIRST_THRESHOLDS: Final = 0x346C
STEPS: Final = 0x2F64
STEP_COUNT: Final = 6
ROWS: Final = 0x3474
ROW_COUNT: Final = 6
ROW_SIZE: Final = 8
CLASS_MAP: Final = 0x34A4
CLASS_MAP_SIZE: Final = 256
CLASS_DATA: Final = 0x35A4
CLASS_DATA_SIZE: Final = 9
CLASS_COUNT: Final = 98
MAGIC_BYTE: Final = 7
MAGIC_SHIFT: Final = 6
SPECIAL_BYTE: Final = 8
SPECIAL_SHIFT: Final = 4
NAME_POINTERS: Final = 0x4105
NAME_COUNT: Final = 256
SPELL_FIRST: Final = CLASS_COUNT + 4
SPELL_COUNT: Final = 14
SPECIAL_FIRST: Final = CLASS_COUNT + 31
SPECIAL_COUNT: Final = 8
STATS: Final = 4
BANK_START: Final = 0x4000
BANK_END: Final = 0x8000
END: Final = 0xFF
DIGITS: Final = 10
HIRAGANA_FIRST: Final = 0x0A
KATAKANA_FIRST: Final = 0x49
HIRAGANA: Final = (
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
)
KATAKANA: Final = (
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
)
SMALL: Final = {
    0x38: "っ",
    0x39: "ょ",
    0x3A: "ゅ",
    0x3B: "ゃ",
    0x3C: "ぃ",
    0x77: "ァ",
    0x78: "ィ",
    0x7A: "ォ",
    0x7B: "ッ",
    0x7C: "ャ",
    0x7D: "ュ",
    0x7E: "ョ",
}
MARKS: Final = {0x40: "ー", 0x3F: " "}
VOICED: Final = 0x3E
SEMI_VOICED: Final = 0x3D
VOICING: Final = str.maketrans(
    "かきくけこさしすせそたちつてとはひふへほカキクケコサシスセソタチツテトハヒフヘホウ",
    "がぎぐげござじずぜぞだぢづでどばびぶべぼガギグゲゴザジズゼゾダヂヅデドバビブベボヴ",
)
SEMI_VOICING: Final = str.maketrans("はひふへほハヒフヘホ", "ぱぴぷぺぽパピプペポ")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(args.rompath, ARTIFACT, "place the bspace set dumped from your cartridge there")
    rom = (args.rompath / ROM_PATH).read_bytes()
    args.out.write_text(render(rom), encoding="utf-8")


def render(rom: bytes) -> str:
    names = [name_at(rom, word(rom, NAME_POINTERS + 2 * index)) for index in range(NAME_COUNT)]
    classes = [class_data(rom, number) for number in range(CLASS_COUNT)]
    rows = tuple(words(rom, ROWS + ROW_SIZE * row, STATS) for row in range(ROW_COUNT))
    lines = [
        '"""The tables Battle Space reads a barcode with.',
        "",
        "Written from the game's ROM by tools/oracle/extract_barcode_boy.py;",
        "regenerate rather than edit.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"FIRST_THRESHOLDS: Final = {words(rom, FIRST_THRESHOLDS, STATS)}",
        f"STEPS: Final = {tuple(rom[STEPS : STEPS + STEP_COUNT])}",
        f"ROWS: Final = {rows}",
        f"CLASS_MAP: Final = {tuple(rom[CLASS_MAP : CLASS_MAP + CLASS_MAP_SIZE])}",
        f"MAGIC_GROUPS: Final = {tuple(data[MAGIC_BYTE] >> MAGIC_SHIFT for data in classes)}",
        f"SPECIALS: Final = {tuple((data[SPECIAL_BYTE] >> SPECIAL_SHIFT) - 1 for data in classes)}",
        f"CLASS_NAMES: Final = {tuple(names[:CLASS_COUNT])}",
        f"SPELL_NAMES: Final = {tuple(names[SPELL_FIRST : SPELL_FIRST + SPELL_COUNT])}",
        f"SPECIAL_NAMES: Final = {tuple(names[SPECIAL_FIRST : SPECIAL_FIRST + SPECIAL_COUNT])}",
        "",
    ]
    return "\n".join(lines)


def class_data(rom: bytes, number: int) -> bytes:
    start = CLASS_DATA + CLASS_DATA_SIZE * number
    return rom[start : start + CLASS_DATA_SIZE]


def word(rom: bytes, address: int) -> int:
    return rom[address] | rom[address + 1] << 8


def words(rom: bytes, address: int, count: int) -> tuple[int, ...]:
    return tuple(word(rom, address + 2 * index) for index in range(count))


def name_at(rom: bytes, address: int) -> str:
    if not BANK_START <= address < BANK_END:
        return ""
    text = ""
    for byte in rom[address : rom.index(END, address)]:
        text = with_byte(text, byte)
    return text


def with_byte(text: str, byte: int) -> str:
    if byte == VOICED:
        return text[:-1] + text[-1:].translate(VOICING)
    if byte == SEMI_VOICED:
        return text[:-1] + text[-1:].translate(SEMI_VOICING)
    return text + character(byte)


def character(byte: int) -> str:
    if byte < DIGITS:
        return str(byte)
    if HIRAGANA_FIRST <= byte < HIRAGANA_FIRST + len(HIRAGANA):
        return HIRAGANA[byte - HIRAGANA_FIRST]
    if KATAKANA_FIRST <= byte < KATAKANA_FIRST + len(KATAKANA):
        return KATAKANA[byte - KATAKANA_FIRST]
    return SMALL.get(byte) or MARKS.get(byte) or f"?{byte:02x}"


if __name__ == "__main__":
    main()
