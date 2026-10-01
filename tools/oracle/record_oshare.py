"""Record what Oshare Majo Love and Berry DS Collection makes of a card, running its own decoder.

Usage: uv run --with unicorn python tools/oracle/record_oshare.py --rompath DIR --codes PATH --out PATH

The game hands the Code 39 text the HCV-1000 read, the part after its start
character with the stop kept, to the routine at $020022EC, which returns 1 for a card it takes
and leaves the item it names, such as DUP  CB004, at $020D6120. The ARM9
program is loaded at its address in the Unicorn engine and that routine is
run on each code, so what is recorded is the game's own answer rather than a
reading of its code. GBE+'s HCV-1000 notes give six cards that check it.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import verify_artifact

ARTIFACT: Final = "nds_oshare"
ROM_PATH: Final = "nds/oshare.nds"
GAME: Final = "Oshare Majo Love and Berry DS Collection"
FIELD_SIZE: Final = 4
ARM9_OFFSET_FIELD: Final = 0x20
ARM9_ADDRESS_FIELD: Final = 0x28
ARM9_SIZE_FIELD: Final = 0x2C
MAIN_RAM: Final = 0x2000000
MAIN_RAM_SIZE: Final = 0x400000
DECODER: Final = 0x020022EC
ITEM: Final = 0x020D6120
ITEM_SIZE: Final = 16
BUFFER: Final = 0x023E0000
BUFFER_SIZE: Final = 32
STOP: Final = "*"
STACK: Final = 0x023F0000
RETURN: Final = 0x023DFFF0
LOOP_FOREVER: Final = bytes.fromhex("feffffea")
STEP_LIMIT: Final = 2_000_000
EMULATOR: Final = (
    "Unicorn running the game's ARM9 program from its ROM; tools/oracle/record_oshare.py "
    "calls the decoder at $020022EC with the text after the start character"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(args.rompath, ARTIFACT, "place the game dumped from your cartridge there")
    arm9 = program((args.rompath / ROM_PATH).read_bytes())
    codes = [line.strip() for line in args.codes.read_text().splitlines() if line.strip()]
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    fixture = {
        "game": GAME,
        "emulator": EMULATOR,
        "recorded_utc": stamp,
        "cards": [{"barcode": code, "item": decoded(arm9, code)} for code in codes],
    }
    args.out.write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def _field(rom: bytes, place: int) -> int:
    return int.from_bytes(rom[place : place + FIELD_SIZE], "little")


def program(rom: bytes) -> bytes:
    start = _field(rom, ARM9_OFFSET_FIELD)
    return rom[start : start + _field(rom, ARM9_SIZE_FIELD)]


def handed(text: str) -> bytes:
    raw = (text.rstrip(STOP) + STOP).encode("ascii")
    return raw + bytes(BUFFER_SIZE - len(raw))


def item_of(accepted: int, memory: bytes) -> str:
    if not accepted:
        return ""
    return memory.split(b"\x00")[0].decode("latin1")


def decoded(arm9: bytes, text: str) -> str:
    from unicorn import UC_ARCH_ARM, UC_MODE_ARM, Uc  # noqa: PLC0415
    from unicorn.arm_const import (  # noqa: PLC0415
        UC_ARM_REG_LR,
        UC_ARM_REG_R0,
        UC_ARM_REG_SP,
    )

    engine = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    engine.mem_map(MAIN_RAM, MAIN_RAM_SIZE)
    engine.mem_write(MAIN_RAM, arm9)
    engine.mem_write(BUFFER, handed(text))
    engine.mem_write(RETURN, LOOP_FOREVER)
    engine.reg_write(UC_ARM_REG_SP, STACK)
    engine.reg_write(UC_ARM_REG_LR, RETURN)
    engine.reg_write(UC_ARM_REG_R0, BUFFER)
    engine.emu_start(DECODER, RETURN, count=STEP_LIMIT)
    accepted = engine.reg_read(UC_ARM_REG_R0)
    return item_of(accepted, bytes(engine.mem_read(ITEM, ITEM_SIZE)))


if __name__ == "__main__":
    main()
