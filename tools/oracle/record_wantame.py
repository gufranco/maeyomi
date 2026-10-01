"""Record what Wantame Music Channel makes of a code, running its own checks.

Usage: uv run --with unicorn python tools/oracle/record_wantame.py --rompath DIR --codes PATH --out PATH

The scanner sends a code as 42 bits, six Code 128 C values with the first in
the highest bits, then the Code 128 checksum. Once the bits are in, the
routine at $020540F0 checks the checksum and hands the values to the routine
at $02054374, which stores them as BCD pairs. The routine at $020430B4 then
says whether a card has that code and $02042AA8 returns the card's record. The
ARM9 program is loaded into the Unicorn engine, the bits are placed where the
game gathers them and those routines are run in that order, so what is
recorded is the game's own answer: whether the checksum passed, whether a
wrong checksum was turned away, and the kind and place of the card found.
"""

import argparse
import json
import struct
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Protocol

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

ARTIFACT: Final = "nds_wantame"
ROM_PATH: Final = "nds/wantame.nds"
GAME: Final = "Wantame Music Channel Doko Demo Style"
FIELD_SIZE: Final = 4
ARM9_OFFSET_FIELD: Final = 0x20
ARM9_SIZE_FIELD: Final = 0x2C
MAIN_RAM: Final = 0x2000000
MAIN_RAM_SIZE: Final = 0x400000
SCANNER: Final = 0x020DB5A4
CALLBACK_FIELD: Final = 0x2C
BITS_FIELD: Final = 0x34
CHECK_FIELD: Final = 0x3C
RESTART_FIELD: Final = 0x50
RESULT: Final = 0x020DB5FC
FAILED_FIELD: Final = 8
VALUE_FIELD: Final = 0xC
VERIFY: Final = 0x020540F0
STORE: Final = 0x02054374
KNOWN: Final = 0x020430B4
LOOKUP: Final = 0x02042AA8
RECORD: Final = 0x023E0000
STACK: Final = 0x023F0000
RETURN: Final = 0x023DFFF0
LOOP_FOREVER: Final = bytes.fromhex("feffffea")
STEP_LIMIT: Final = 500_000
PAIR_BITS: Final = 7
PAIRS: Final = 6
PAIR_DIGITS: Final = 2
START_C: Final = 105
MODULUS: Final = 103
WORD_MASK: Final = 0xFFFFFFFF
EMULATOR: Final = (
    "Unicorn running the game's ARM9 program from its ROM; tools/oracle/record_wantame.py "
    "places the scanner's bits as $02053DB4 gathers them and runs $020540F0, $020430B4 and "
    "$02042AA8 in turn"
)


class Engine(Protocol):
    """The part of a Unicorn engine the recorder uses."""

    def mem_write(self, address: int, data: bytes) -> None: ...
    def mem_read(self, address: int, size: int) -> bytearray: ...
    def reg_write(self, register: int, value: int) -> None: ...
    def reg_read(self, register: int) -> int: ...
    def emu_start(self, begin: int, until: int, *, count: int) -> None: ...


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
        "cards": [reading(code, answers(rom, code)) for code in codes],
    }
    args.out.write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def _values(code: str) -> list[int]:
    return [int(code[place : place + PAIR_DIGITS]) for place in range(0, len(code), PAIR_DIGITS)]


def sent(code: str) -> int:
    """The 42 bits the scanner sends for a code."""
    return sum(
        value << PAIR_BITS * (PAIRS - 1 - place) for place, value in enumerate(_values(code))
    )


def check(code: str) -> int:
    """The Code 128 checksum the scanner sends after the code."""
    weighted = sum(value * (place + 1) for place, value in enumerate(_values(code)))
    return (START_C + weighted) % MODULUS


def wrong(code: str) -> int:
    """A checksum the code does not have."""
    return (check(code) + 1) % MODULUS


def reading(
    code: str, answer: tuple[bool, bool, tuple[int, int] | None]
) -> dict[str, str | bool | int]:
    checked, refused, card = answer
    kind, index = card or (0, -1)
    return {
        "barcode": code,
        "checked": checked,
        "wrong_check_refused": refused,
        "kind": kind,
        "index": index,
    }


def _field(rom: bytes, place: int) -> int:
    return int.from_bytes(rom[place : place + FIELD_SIZE], "little")


def _engine(rom: bytes) -> Engine:
    from unicorn import UC_ARCH_ARM, UC_MODE_ARM, Uc  # noqa: PLC0415

    engine = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    engine.mem_map(MAIN_RAM, MAIN_RAM_SIZE)
    start = _field(rom, ARM9_OFFSET_FIELD)
    engine.mem_write(MAIN_RAM, rom[start : start + _field(rom, ARM9_SIZE_FIELD)])
    engine.mem_write(RETURN, LOOP_FOREVER)
    return engine


def _call(engine: Engine, routine: int, arguments: tuple[int, ...]) -> int:
    from unicorn.arm_const import (  # noqa: PLC0415
        UC_ARM_REG_LR,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_SP,
    )

    registers = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2)
    for register, value in zip(registers, arguments, strict=False):
        engine.reg_write(register, value)
    engine.reg_write(UC_ARM_REG_SP, STACK)
    engine.reg_write(UC_ARM_REG_LR, RETURN)
    engine.emu_start(routine, RETURN, count=STEP_LIMIT)
    return int(engine.reg_read(UC_ARM_REG_R0))


def _scan(engine: Engine, code: str, checksum: int) -> tuple[bool, int, int]:
    bits = sent(code)
    words = struct.pack("<4I", bits & WORD_MASK, bits >> 32, checksum, 0)
    engine.mem_write(SCANNER + BITS_FIELD, words)
    engine.mem_write(SCANNER + CALLBACK_FIELD, struct.pack("<I", STORE))
    engine.mem_write(SCANNER + RESTART_FIELD, bytes(FIELD_SIZE))
    _call(engine, VERIFY, ())
    raw = bytes(engine.mem_read(RESULT, VALUE_FIELD + 2 * FIELD_SIZE))
    failed, low, high = struct.unpack_from("<I", raw, FAILED_FIELD) + struct.unpack_from(
        "<2I", raw, VALUE_FIELD
    )
    return failed == 0, low, high


def answers(rom: bytes, code: str) -> tuple[bool, bool, tuple[int, int] | None]:
    engine = _engine(rom)
    refused = not _scan(engine, code, wrong(code))[0]
    checked, low, high = _scan(engine, code, check(code))
    if not checked or not _call(engine, KNOWN, (low, high)):
        return checked, refused, None
    _call(engine, LOOKUP, (RECORD, low, high))
    pointer = struct.unpack("<I", bytes(engine.mem_read(RECORD, FIELD_SIZE)))[0]
    kind, index = struct.unpack("<2I", bytes(engine.mem_read(pointer, 2 * FIELD_SIZE)))
    return checked, refused, (kind, index)


if __name__ == "__main__":
    main()
