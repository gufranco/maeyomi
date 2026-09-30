"""Record what Monster Maker: Barcode Saga reads from a Barcode Boy, running the game in MAME.

Usage: uv run python tools/oracle/record_monster_maker.py --rompath DIR --codes FILE --out FILE

The game reads a card two ways. Forming the party, a flag at $C67F is 0 and a
card gives one of the seventeen heroes; once the adventure has begun the game
sets that flag to 1, and the same card gives one of thirty-five characters at a
level of its own. barcode_boy.lua plays the reader, as it does for Battle
Space, from the party screen the game opens on. Each code is scanned twice from
that saved state, once with the flag as the game starts it and once with the
flag as the game sets it later. The character record at $C9C3 is kept at the
moment the decoder returns a character, which the game marks by writing $C679
at $6AF9, because the party screen's own code runs after that and cannot place
a monster. A scan that never reaches that point is left out.
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
ARTIFACT: Final = "gameboy_monstmkb"
BOOT_ARTIFACTS: Final = ("gameboy_dmg_boot", "gameboy_dmg_v0")
SOFTWARE: Final = "monstmkb"
GAME: Final = "Monster Maker: Barcode Saga"
SCRIPT: Final = HERE / "barcode_boy.lua"
PARTY_MODE: Final = 0
ADVENTURE_MODE: Final = 1
MODE_FLAG: Final = "0xc67f"
RECORD: Final = "0xc9c3"
RECORD_SIZE: Final = "8"
SLOT: Final = "0xc5b0"
DECODED: Final = "0xc679"
DECODED_AT: Final = "0x6af6"
UNREAD: Final = "ee"
READY_FRAME: Final = "1200"
SETTLE: Final = "150"
EMULATOR: Final = (
    "MAME 0.289, gameboy with no link device; tools/oracle/barcode_boy.lua answers "
    "the serial port the way a Barcode Boy does"
)
SCREEN: Final = (
    "each code is scanned at the party screen's 'insert a card' prompt from one saved "
    "state, once with the flag at $C67F at 0 as a new game has it and once at 1 as the "
    "game sets it once the adventure begins; party and adventure are the 8-byte character "
    "record at $C9C3 when the decoder returns, which the game marks by writing $C679"
)
SESSION_SECONDS: Final = "3000"
TIMEOUT_SECONDS: Final = 1500
FIELDS: Final = 4


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(
        args.rompath, ARTIFACT, "place the monstmkb set dumped from your cartridge there"
    )
    for boot in BOOT_ARTIFACTS:
        verify_artifact(args.rompath, boot, "place the boot ROM dumped from your Game Boy there")
    party = parse(run_session(args.rompath, args.codes, PARTY_MODE))
    adventure = parse(run_session(args.rompath, args.codes, ADVENTURE_MODE))
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = json.dumps(fixture(pair(party, adventure), stamp), indent=1, ensure_ascii=False)
    args.out.write_text(text + "\n", encoding="utf-8")


def session_env(codes: Path, mode: int) -> dict[str, str]:
    return {
        **HEADLESS,
        "CODES": str(codes.resolve()),
        "RECORD_ADDR": RECORD,
        "RECORD_LEN": RECORD_SIZE,
        "STATUS_ADDR": SLOT,
        "READY_FRAME": READY_FRAME,
        "SETTLE": SETTLE,
        "POKE_ADDR": MODE_FLAG,
        "POKE_VALUE": str(mode),
        "CAPTURE_ADDR": DECODED,
        "CAPTURE_PC": DECODED_AT,
    }


def run_session(rompath: Path, codes: Path, mode: int) -> str:
    with tempfile.TemporaryDirectory() as scratch:
        (Path(scratch) / "mame.ini").write_text(MAME_INI)
        completed = subprocess.run(  # noqa: S603
            mame_command(rompath, Path(scratch) / "state"),
            cwd=scratch,
            env={**os.environ, **session_env(codes, mode)},
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


def parse(output: str) -> dict[str, str]:
    records: dict[str, str] = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == FIELDS and fields[0] == "REC" and fields[2] != UNREAD:
            records = {**records, fields[1]: fields[3]}
    return records


def pair(party: dict[str, str], adventure: dict[str, str]) -> list[dict[str, str]]:
    return [
        {"barcode": code, "party": record, "adventure": adventure[code]}
        for code, record in party.items()
        if code in adventure
    ]


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
