"""Write the card codes Card de Asobu! Hajimete no DS checks a scan against, from its ROM.

Usage: uv run python tools/oracle/extract_cardasobu.py --rompath DIR --out FILE

The game keeps a table of pointers at $020871B0 in its ARM9 program, one for
each card in kana order, あ first, each pointing at the ten characters a scan
must start with. Slot 5, か, points at ZZZZZZZZZZ, a code no card carries; か's
own card is the last entry. The ARM9 program is stored uncompressed, so a RAM
address is found in the ROM by the program's offset and load address in the
cartridge header.
"""

import argparse
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

ARTIFACT: Final = "nds_cardasobu"
ROM_PATH: Final = "nds/cardasobu.nds"
ARM9_OFFSET_FIELD: Final = 0x20
ARM9_ADDRESS_FIELD: Final = 0x28
FIELD_SIZE: Final = 4
TABLE_ADDRESS: Final = 0x020871B0
ENTRY_SIZE: Final = 12
CODE_SIZE: Final = 10
MAX_CARDS: Final = 64


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
        '"""The card codes Card de Asobu! Hajimete no DS checks a scan against.',
        "",
        "Written from the game's ROM by tools/oracle/extract_cardasobu.py; regenerate",
        "rather than edit. Each code is the first ten characters of a card's Code 39",
        "text, in the game's own kana order.",
        '"""',
        "",
        "from typing import Final",
        "",
        f"CODES: Final = {codes(rom)}",
        "",
    ]
    return "\n".join(lines)


def _field(rom: bytes, place: int) -> int:
    return int.from_bytes(rom[place : place + FIELD_SIZE], "little")


def _offset(rom: bytes, address: int) -> int:
    return address - _field(rom, ARM9_ADDRESS_FIELD) + _field(rom, ARM9_OFFSET_FIELD)


def codes(rom: bytes) -> tuple[str, ...]:
    table = _offset(rom, TABLE_ADDRESS)
    pointers = (_field(rom, table + FIELD_SIZE * index) for index in range(MAX_CARDS))
    found: list[str] = []
    for pointer in pointers:
        if not pointer:
            break
        place = _offset(rom, pointer)
        found = [*found, rom[place : place + CODE_SIZE].decode("ascii")]
    return tuple(found)


if __name__ == "__main__":
    main()
