"""Write the tables Monster Maker: Barcode Saga reads a barcode with, straight from its ROM.

Usage: uv run python tools/oracle/extract_monster_maker.py --rompath DIR --out FILE

The addresses are where the game keeps each table, found by following the code
that runs after a scan and the code that draws the status screen. Every table
is read from the bytes, never typed. A name is two rows of tiles: the letters,
and above them the voicing marks, so each mark is applied to the letter under
it. The game draws リ and ヘ with the hiragana tiles, so either one beside a
katakana letter is written as katakana.
"""

import argparse
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

ARTIFACT: Final = "gameboy_monstmkb"
ROM_PATH: Final = "gameboy/monstmkb/dmg-qnj-0.u1"
NAMES: Final = 0x4CC5
CLASS_NAMES: Final = 0x4286
TEXT_SIZE: Final = 16
ROW: Final = 8
CHARACTER_COUNT: Final = 35
CLASS_COUNT: Final = 5
CLASSES: Final = 0x6D66
HERO_STATS: Final = 0x4F4A
HERO_COUNT: Final = 17
LEVELS: Final = 9
HERO_ENTRY: Final = 6
MONSTER_STATS: Final = 0x7359
MONSTER_ENTRY: Final = 10
DIGIT_FIRST: Final = 0x80
DIGITS: Final = 10
HIRAGANA_FIRST: Final = 0x8A
KATAKANA_FIRST: Final = 0xBC
HIRAGANA: Final = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんっゃゅょ"
KATAKANA: Final = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤ"
OTHERS: Final = {
    0xE0: "ユ",
    0xE1: "ヨ",
    0xE2: "ラ",
    0xE4: "ル",
    0xE5: "レ",
    0xE6: "ロ",
    0xE7: "ワ",
    0xE9: "ン",
    0xEB: "ィ",
    0xEC: "ッ",
    0xED: "ャ",
    0xEE: "ュ",
    0xF0: "ー",
    0xF3: "ェ",
    0xF4: "ォ",
    0xFE: " ",
}
VOICED: Final = 0xE3
SEMI_VOICED: Final = 0xE8
SHARED: Final = str.maketrans("りへ", "リヘ")
KATAKANA_BLOCK: Final = ("ァ", "ー")
VOICING: Final = str.maketrans(
    "かきくけこさしすせそたちつてとはひふへほカキクケコサシスセソタチツテトハヒフヘホウ",
    "がぎぐげござじずぜぞだぢづでどばびぶべぼガギグゲゴザジズゼゾダヂヅデドバビブベボヴ",
)
SEMI_VOICING: Final = str.maketrans("はひふへほハヒフヘホ", "ぱぴぷぺぽパピプペポ")

type Stats = tuple[int, int, int, int, int]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(
        args.rompath, ARTIFACT, "place the monstmkb set dumped from your cartridge there"
    )
    rom = (args.rompath / ROM_PATH).read_bytes()
    args.out.write_text(render(rom), encoding="utf-8")


def render(rom: bytes) -> str:
    lines = [
        '"""The tables Monster Maker: Barcode Saga reads a barcode with.',
        "",
        "Written from the game's ROM by tools/oracle/extract_monster_maker.py;",
        "regenerate rather than edit. A hero's stats are one entry per level,",
        "anyone else's one entry, each as move, DP, MP, AP and HP.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"NAMES: Final = {texts(rom, NAMES, CHARACTER_COUNT)}",
        f"CLASS_NAMES: Final = {texts(rom, CLASS_NAMES, CLASS_COUNT)}",
        f"CLASSES: Final = {tuple(rom[CLASSES : CLASSES + CHARACTER_COUNT])}",
        f"HERO_STATS: Final = {hero_stats(rom)}",
        f"MONSTER_STATS: Final = {monster_stats(rom)}",
        "",
    ]
    return "\n".join(lines)


def texts(rom: bytes, address: int, count: int) -> tuple[str, ...]:
    return tuple(text_at(rom, address + TEXT_SIZE * index) for index in range(count))


def text_at(rom: bytes, address: int) -> str:
    marks = rom[address : address + ROW]
    letters = "".join(character(byte) for byte in rom[address + ROW : address + TEXT_SIZE])
    shared = "".join(
        letter.translate(SHARED) if _beside_katakana(letters, index) else letter
        for index, letter in enumerate(letters)
    )
    return "".join(
        voiced(letter, mark) for letter, mark in zip(shared, marks, strict=False)
    ).strip()


def _beside_katakana(letters: str, index: int) -> bool:
    neighbours = letters[max(0, index - 1) : index] + letters[index + 1 : index + 2]
    first, last = KATAKANA_BLOCK
    return any(first <= letter <= last for letter in neighbours)


def voiced(letter: str, mark: int) -> str:
    if mark == VOICED:
        return letter.translate(VOICING)
    if mark == SEMI_VOICED:
        return letter.translate(SEMI_VOICING)
    return letter


def character(byte: int) -> str:
    if DIGIT_FIRST <= byte < DIGIT_FIRST + DIGITS:
        return str(byte - DIGIT_FIRST)
    if HIRAGANA_FIRST <= byte < HIRAGANA_FIRST + len(HIRAGANA):
        return HIRAGANA[byte - HIRAGANA_FIRST]
    if KATAKANA_FIRST <= byte < KATAKANA_FIRST + len(KATAKANA):
        return KATAKANA[byte - KATAKANA_FIRST]
    return OTHERS.get(byte) or f"?{byte:02x}"


def stats_at(rom: bytes, address: int) -> Stats:
    move, dp, mp, ap, low, high = rom[address : address + HERO_ENTRY]
    return move, dp, mp, ap, low | high << 8


def hero_stats(rom: bytes) -> tuple[tuple[Stats, ...], ...]:
    return tuple(
        tuple(
            stats_at(rom, HERO_STATS + (hero * LEVELS + level) * HERO_ENTRY)
            for level in range(LEVELS)
        )
        for hero in range(HERO_COUNT)
    )


def monster_stats(rom: bytes) -> tuple[Stats, ...]:
    count = CHARACTER_COUNT - HERO_COUNT
    return tuple(stats_at(rom, MONSTER_STATS + MONSTER_ENTRY * index) for index in range(count))


if __name__ == "__main__":
    main()
