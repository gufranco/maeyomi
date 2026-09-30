"""Record what Battle Space reads from a Barcode Boy, running the game in MAME.

Usage: uv run python tools/oracle/record_barcode_boy.py --rompath DIR --codes FILE --out FILE

MAME has no Barcode Boy, so barcode_boy.lua plays one: it answers the game's
handshake with FF FF 10 07 and then clocks in 02, the thirteen digits and 03,
twice, a byte a millisecond with two between the copies, which is the only
pacing the game's timers accept. It saves the machine at the "insert a card"
screen, and for each code reloads that state, scans the code and prints the
player record the game filled in and the status it wrote.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import HASH_PATH, HEADLESS, MAME_INI, MANIFEST, verify_artifact

HERE: Final = Path(__file__).parent
ARTIFACT: Final = "gameboy_bspace"
BOOT_ARTIFACTS: Final = ("gameboy_dmg_boot", "gameboy_dmg_v0")
SOFTWARE: Final = "bspace"
GAME: Final = "Battle Space"
SCRIPT: Final = HERE / "barcode_boy.lua"
EMULATOR: Final = (
    "MAME 0.289, gameboy with no link device; tools/oracle/barcode_boy.lua answers "
    "the serial port the way a Barcode Boy does"
)
SCREEN: Final = (
    "each code is scanned at the player 1 'insert a card' screen from one saved state; "
    "record is the 0x31-byte player record at $C99E and status the byte at $C834, 0 when "
    "both copies matched"
)
SESSION_SECONDS: Final = "3000"
TIMEOUT_SECONDS: Final = 1500
SCAN: Final = re.compile(r"^REC (\d{13}|\d{8}) ([0-9a-f]{2}) ([0-9a-f]+)$", re.MULTILINE)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(args.rompath, ARTIFACT, "place the bspace set dumped from your cartridge there")
    for boot in BOOT_ARTIFACTS:
        verify_artifact(args.rompath, boot, "place the boot ROM dumped from your Game Boy there")
    output = run_session(args.rompath, args.codes)
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    fixture_text = json.dumps(fixture(parse(output), stamp), indent=1, ensure_ascii=False)
    args.out.write_text(fixture_text + "\n", encoding="utf-8")


def run_session(rompath: Path, codes: Path) -> str:
    with tempfile.TemporaryDirectory() as scratch:
        (Path(scratch) / "mame.ini").write_text(MAME_INI)
        completed = subprocess.run(  # noqa: S603
            mame_command(rompath, Path(scratch) / "state"),
            cwd=scratch,
            env={**os.environ, **HEADLESS, "CODES": str(codes.resolve())},
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    return completed.stdout


def mame_command(rompath: Path, state: Path) -> list[str]:
    return [
        "mame",
        "gameboy",
        SOFTWARE,
        "-hashpath",
        HASH_PATH,
        "-rompath",
        str(rompath.resolve()),
        "-window",
        "-video",
        "none",
        "-sound",
        "none",
        "-nothrottle",
        "-skip_gameinfo",
        "-seconds_to_run",
        SESSION_SECONDS,
        "-state_directory",
        str(state),
        "-autoboot_script",
        str(SCRIPT),
    ]


def parse(output: str) -> list[dict[str, object]]:
    return [
        {"barcode": code, "status": int(status, 16), "record": record}
        for code, status, record in SCAN.findall(output)
    ]


def fixture(cards: list[dict[str, object]], recorded_utc: str) -> dict[str, object]:
    artifacts = json.loads(MANIFEST.read_text())["artifacts"]
    entry = next(item for item in artifacts if item["id"] == ARTIFACT)
    return {
        "game": GAME,
        "software": SOFTWARE,
        "rom": {"sha1": entry["sha1"], "size": entry["size"]},
        "emulator": EMULATOR,
        "screen": SCREEN,
        "recorded_utc": recorded_utc,
        "cards": cards,
    }


if __name__ == "__main__":
    main()
