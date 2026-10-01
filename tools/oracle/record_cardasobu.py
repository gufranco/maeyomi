"""Record which cards Card de Asobu! Hajimete no DS accepts, running the game in GBE+.

Usage: uv run python tools/oracle/record_cardasobu.py --rompath DIR --gbe FILE --codes FILE --out FILE

GBE+ is the only emulator with Sega's HCV-1000. tools/oracle/gbe_plus/build.sh
builds it at a pinned commit with a small patch that replays a frame-timed
script: here, swipe one card on the practice screen the game opens with, then
save the screen it answers with. A card the game accepts and one it refuses
draw different screens, and every accepted card draws the same one, so each
code is recorded with a fingerprint of that screen. Codes run several at
once, each in its own emulator.
"""

import argparse
import hashlib
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

from record_game import HEADLESS, verify_artifact

ARTIFACT: Final = "nds_cardasobu"
ROM_PATH: Final = "nds/cardasobu.nds"
GAME: Final = "Card de Asobu! Hajimete no DS"
CONFIG: Final = "[#slot2_device:6]\n[#mute:1]\n"
SWIPE_FRAME: Final = 1100
SHOT_FRAME: Final = 1250
TIMEOUT_SECONDS: Final = 300
WORKERS: Final = 6
FINGERPRINT_LENGTH: Final = 16
EMULATOR: Final = (
    "GBE+ at 05a05e93 built by tools/oracle/gbe_plus/build.sh, whose patch replays a "
    "frame-timed script and emulates the HCV-1000 with its own slot-2 device"
)
SCREEN: Final = (
    "the practice scan the game opens with; screen is a fingerprint of both screens "
    "150 frames after the swipe"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--gbe", type=Path, required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(args.rompath, ARTIFACT, "place the game dumped from your cartridge there")
    codes = [line.strip() for line in args.codes.read_text().splitlines() if line.strip()]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        screens = list(pool.map(lambda code: run_session(args.gbe, args.rompath, code), codes))
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    fixture = {
        "game": GAME,
        "emulator": EMULATOR,
        "screen": SCREEN,
        "recorded_utc": stamp,
        "cards": [
            {"barcode": code, "screen": screen} for code, screen in zip(codes, screens, strict=True)
        ],
    }
    args.out.write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def script(code: str, shot: Path) -> str:
    return "\n".join(
        [
            f"{SWIPE_FRAME} card {code}",
            f"{SHOT_FRAME} shot {shot}",
            f"{SHOT_FRAME + 1} exit",
        ]
    )


def command(gbe: Path, rompath: Path) -> list[str]:
    return [str(gbe), str((rompath / ROM_PATH).resolve())]


def fingerprint(shot: Path) -> str:
    if not shot.exists():
        return ""
    return hashlib.sha256(shot.read_bytes()).hexdigest()[:FINGERPRINT_LENGTH]


def run_session(gbe: Path, rompath: Path, code: str) -> str:
    with tempfile.TemporaryDirectory() as scratch:
        here = Path(scratch)
        (here / "gbe.ini").write_text(CONFIG)
        (here / "script.txt").write_text(script(code, here / "shot.ppm") + "\n")
        subprocess.run(  # noqa: S603
            command(gbe, rompath),
            cwd=here,
            env={**os.environ, **HEADLESS, "GBE_SCRIPT": str(here / "script.txt")},
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
        return fingerprint(here / "shot.ppm")


if __name__ == "__main__":
    main()
