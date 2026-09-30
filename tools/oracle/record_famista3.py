"""Record what Famista 3 reads from a Barcode Boy, running the game in MAME.

Usage: uv run python tools/oracle/record_famista3.py --rompath DIR --codes FILE --out FILE

The game reads a card from team editing: チームへんせい, then バーコード, where
it sends the handshake. barcode_boy.lua presses those buttons from power on,
answers the handshake, saves the machine at the barcode prompt, and for each
code reloads that state, scans it and prints from $C30E: the game's own flag,
1 for a pitcher, the 16-byte player it copied to $C310, and the pointer it
copied from at $C330. The pointer is marked before every scan, so a scan the
game did not take shows as that mark and is left out.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import HASH_PATH, HEADLESS, MAME_INI, MANIFEST, verify_artifact

HERE: Final = Path(__file__).parent
ARTIFACT: Final = "gameboy_famista3"
BOOT_ARTIFACTS: Final = ("gameboy_dmg_boot", "gameboy_dmg_v0")
SOFTWARE: Final = "famista3"
GAME: Final = "Famista 3"
SCRIPT: Final = HERE / "barcode_boy.lua"
BOOT_STEPS: Final = "700:Start,900:Down,960:Button A,1300:Button A"
RECORD: Final = "0xc30e"
RECORD_SIZE: Final = "0x24"
POINTER: Final = "0xc330"
PLAYER: Final = slice(4, 36)
POINTER_HEX: Final = slice(68, 72)
PITCHER_FLAG: Final = "01"
READY_FRAME: Final = "1400"
SETTLE: Final = "150"
UNREAD: Final = "ee"
FIELDS: Final = 4
EMULATOR: Final = (
    "MAME 0.289, gameboy with no link device; tools/oracle/barcode_boy.lua answers "
    "the serial port the way a Barcode Boy does"
)
SCREEN: Final = (
    "each code is scanned at the team editing barcode prompt from one saved state; kind is "
    "the game's flag at $C30E, record the 16-byte player copied to $C310, pointer the "
    "address in bank $0A it was copied from, stored at $C330"
)
SESSION_SECONDS: Final = "3000"
TIMEOUT_SECONDS: Final = 1500


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(
        args.rompath, ARTIFACT, "place the famista3 set dumped from your cartridge there"
    )
    for boot in BOOT_ARTIFACTS:
        verify_artifact(args.rompath, boot, "place the boot ROM dumped from your Game Boy there")
    output = run_session(args.rompath, args.codes)
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = json.dumps(fixture(parse(output), stamp), indent=1, ensure_ascii=False)
    args.out.write_text(text + "\n", encoding="utf-8")


def session_env(codes: Path) -> dict[str, str]:
    return {
        **HEADLESS,
        "CODES": str(codes.resolve()),
        "RECORD_ADDR": RECORD,
        "RECORD_LEN": RECORD_SIZE,
        "STATUS_ADDR": POINTER,
        "READY_FRAME": READY_FRAME,
        "SETTLE": SETTLE,
        "BOOT_STEPS": BOOT_STEPS,
    }


def run_session(rompath: Path, codes: Path) -> str:
    with tempfile.TemporaryDirectory() as scratch:
        (Path(scratch) / "mame.ini").write_text(MAME_INI)
        completed = subprocess.run(  # noqa: S603
            mame_command(rompath, Path(scratch) / "state"),
            cwd=scratch,
            env={**os.environ, **session_env(codes)},
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


def parse(output: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == FIELDS and fields[0] == "REC" and fields[2] != UNREAD:
            dump = fields[3]
            kind = "pitcher" if dump[:2] == PITCHER_FLAG else "batter"
            records = [
                *records,
                {
                    "barcode": fields[1],
                    "kind": kind,
                    "record": dump[PLAYER],
                    "pointer": dump[POINTER_HEX],
                },
            ]
    return records


def fixture(cards: list[dict[str, str]], recorded_utc: str) -> dict[str, object]:
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
