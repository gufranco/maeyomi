"""Record what Barcode Taisen Bardigun hatches from a barcode, running the game in MAME.

Usage: uv run python tools/oracle/record_bardigun.py --rompath DIR --codes FILE --out FILE

Each code runs in a fresh game from an empty save: a new game, the clock, the
hero, the name and the uncle's talk, then the barcode prompt. bardigun_reader.lua
plays the reader on the link port, answering 0x00 until it is ready and then
the bars as bits, and once the egg hatches prints the species byte at $CAAC
and the record the game copied to $CAE4. A scan the game never read is left
out. Codes run several at once, each in its own MAME.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import HEADLESS, MAME_INI, verify_artifact

HERE: Final = Path(__file__).parent
ARTIFACT: Final = "gameboy_bardigun"
BOOT_ARTIFACTS: Final = ("gameboy_dmg_boot", "gameboy_dmg_v0")
ROM_PATH: Final = "gbcolor/barcode/dmg-abej-0.u1"
SCRIPT: Final = HERE / "bardigun_reader.lua"
GAME: Final = "Barcode Taisen Bardigun"
SOFTWARE: Final = "barcode"
SECONDS: Final = "110"
TIMEOUT_SECONDS: Final = 600
WORKERS: Final = 6
STEPS: Final = ",".join(
    [
        *(f"{frame}:Start" for frame in (1300, 1450, 1600)),
        *(f"{frame}:Button A" for frame in range(1700, 4300, 120)),
        *(f"{frame}:Button A" for frame in (4500, 4700, 4900, 5100)),
    ]
)
EMULATOR: Final = (
    "MAME 0.289, gameboy with the cartridge loaded directly; tools/oracle/bardigun_reader.lua "
    "answers the link port the way the Bardigun reader does"
)
SCREEN: Final = (
    "a new game's first egg, scanned at the farm's barcode prompt; species is $CAAC and "
    "record the 22 bytes copied to $CAE4 when the egg hatches"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(
        args.rompath, ARTIFACT, "place the barcode set dumped from your cartridge there"
    )
    for boot in BOOT_ARTIFACTS:
        verify_artifact(args.rompath, boot, "place the boot ROM dumped from your Game Boy there")
    codes = [line.strip() for line in args.codes.read_text().splitlines() if line.strip().isdigit()]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        outputs = list(pool.map(lambda code: run_session(args.rompath, code), codes))
    cards = [card for output in outputs for card in map(parse, output.splitlines()) if card]
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    fixture = {
        "game": GAME,
        "software": SOFTWARE,
        "emulator": EMULATOR,
        "screen": SCREEN,
        "recorded_utc": stamp,
        "cards": cards,
    }
    args.out.write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def parse(line: str) -> dict[str, object] | None:
    parts = line.split()
    if len(parts) != 5 or parts[0] != "REC" or parts[3] == "0":
        return None
    return {"barcode": parts[1], "species": int(parts[2], 16), "record": parts[4]}


def run_session(rompath: Path, code: str) -> str:
    with tempfile.TemporaryDirectory() as scratch:
        (Path(scratch) / "mame.ini").write_text(MAME_INI)
        completed = subprocess.run(  # noqa: S603
            mame_command(rompath, Path(scratch) / "nvram"),
            cwd=scratch,
            env={**os.environ, **HEADLESS, "CODE": code, "STEPS": STEPS},
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    return completed.stdout


def mame_command(rompath: Path, nvram: Path) -> list[str]:
    return [
        "mame",
        "gameboy",
        "-cart",
        str((rompath / ROM_PATH).resolve()),
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
        SECONDS,
        "-nvram_directory",
        str(nvram),
        "-autoboot_script",
        str(SCRIPT),
    ]


if __name__ == "__main__":
    main()
