"""Record which card Kouchuu Ouja Mushiking Super Collection takes a code as, running its own comparison.

Usage: uv run --with unicorn python tools/oracle/record_mushiking.py --rompath DIR --codes PATH --out PATH

After a swipe the routine at $0201ECAC tries five lists with $0201FBCC, then a
list of three with $0201FE78 and one of eight with $0201FEB8, and takes the
first card that matches. Its loader fills a table at $021291FC with where each
list sits in data/barcode/m_barcode.bin. The ARM9 program and that file are
loaded into the Unicorn engine, the table is filled the same way, and the
comparisons are run in the game's order on each code, so what is recorded is
the game's own answer: the list, the card, and the variant the comparison
leaves for a card whose code ends in a suffix it reads.
"""

import argparse
import json
import struct
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from extract_mushiking import BARCODE_FILE, LISTS, SPECIAL_ADDRESSES, SPECIAL_COUNTS
from extract_mushiking import SPECIAL_STRIDE as STRIDE
from nitro_fs import read_file
from record_game import verify_artifact

ARTIFACT: Final = "nds_mushiking"
ROM_PATH: Final = "nds/mushiking.nds"
GAME: Final = "Kouchuu Ouja Mushiking Super Collection"
FIELD_SIZE: Final = 4
ARM9_OFFSET_FIELD: Final = 0x20
ARM9_SIZE_FIELD: Final = 0x2C
MAIN_RAM: Final = 0x2000000
MAIN_RAM_SIZE: Final = 0x400000
TABLE: Final = 0x021291FC
FILE_ADDRESS: Final = 0x02300000
SIXTH_ADDRESS: Final = 0x02380000
SEVENTH_ADDRESS: Final = 0x02381000
BUFFER: Final = 0x023E0000
BUFFER_SIZE: Final = 16
VARIANT: Final = 0x023E0100
STACK: Final = 0x023F0000
RETURN: Final = 0x023DFFF0
LOOP_FOREVER: Final = bytes.fromhex("feffffea")
STEP_LIMIT: Final = 500_000
COMPARE: Final = 0x0201FBCC
COMPARE_SIXTH: Final = 0x0201FE78
COMPARE_SEVENTH: Final = 0x0201FEB8
CODE_SIZE: Final = 13
EMULATOR: Final = (
    "Unicorn running the game's ARM9 program from its ROM with m_barcode.bin loaded and the "
    "table at $021291FC filled as its loader does; tools/oracle/record_mushiking.py tries the "
    "comparisons in the order $0201ECAC does"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(args.rompath, ARTIFACT, "place the game dumped from your cartridge there")
    rom = (args.rompath / ROM_PATH).read_bytes()
    codes = [line.strip() for line in args.codes.read_text().splitlines() if line.strip()]
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    fixture = {
        "game": GAME,
        "emulator": EMULATOR,
        "recorded_utc": stamp,
        "cards": [{"barcode": code, **matched(rom, code)} for code in codes],
    }
    args.out.write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def _field(rom: bytes, place: int) -> int:
    return int.from_bytes(rom[place : place + FIELD_SIZE], "little")


def table() -> bytes:
    words = [
        value
        for card in LISTS
        for value in (FILE_ADDRESS + card.codes, FILE_ADDRESS + card.data, card.count)
    ]
    return struct.pack("<17I", *words, SIXTH_ADDRESS, SEVENTH_ADDRESS)


def attempts() -> list[tuple[int, int, int]]:
    filed = [
        (COMPARE, number, index) for number, card in enumerate(LISTS) for index in range(card.count)
    ]
    kept = [
        (routine, len(LISTS) + place, index)
        for place, (routine, count) in enumerate(
            zip((COMPARE_SIXTH, COMPARE_SEVENTH), SPECIAL_COUNTS, strict=True)
        )
        for index in range(count)
    ]
    return filed + kept


def handed(text: str) -> bytes:
    raw = text.encode("ascii")
    return raw + bytes(BUFFER_SIZE - len(raw))


def reading(match: tuple[int, int] | None, variant: int) -> dict[str, int]:
    if match is None:
        return {"list": -1, "index": -1, "variant": 0}
    return {"list": match[0], "index": match[1], "variant": variant}


def matched(rom: bytes, text: str) -> dict[str, int]:
    from unicorn import UC_ARCH_ARM, UC_MODE_ARM, Uc  # noqa: PLC0415
    from unicorn.arm_const import (  # noqa: PLC0415
        UC_ARM_REG_LR,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_R3,
        UC_ARM_REG_SP,
    )

    engine = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    engine.mem_map(MAIN_RAM, MAIN_RAM_SIZE)
    start = _field(rom, ARM9_OFFSET_FIELD)
    engine.mem_write(MAIN_RAM, rom[start : start + _field(rom, ARM9_SIZE_FIELD)])
    engine.mem_write(FILE_ADDRESS, read_file(rom, BARCODE_FILE))
    for target, source, count in zip(
        (SIXTH_ADDRESS, SEVENTH_ADDRESS), SPECIAL_ADDRESSES, SPECIAL_COUNTS, strict=True
    ):
        kept = b"".join(
            bytes(engine.mem_read(source + STRIDE * index, CODE_SIZE)) for index in range(count)
        )
        engine.mem_write(target, kept)
    engine.mem_write(TABLE, table())
    engine.mem_write(RETURN, LOOP_FOREVER)
    engine.mem_write(BUFFER, handed(text))
    for routine, number, index in attempts():
        engine.mem_write(VARIANT, bytes(2))
        for register, value in zip(
            (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3),
            (number, index, BUFFER, VARIANT),
            strict=True,
        ):
            engine.reg_write(register, value)
        engine.reg_write(UC_ARM_REG_SP, STACK)
        engine.reg_write(UC_ARM_REG_LR, RETURN)
        engine.emu_start(routine, RETURN, count=STEP_LIMIT)
        if engine.reg_read(UC_ARM_REG_R0):
            variant = struct.unpack("<h", bytes(engine.mem_read(VARIANT, 2)))[0]
            return reading((number, index), variant)
    return reading(None, 0)


if __name__ == "__main__":
    main()
