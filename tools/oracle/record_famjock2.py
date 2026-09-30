"""Record what Family Jockey 2 reads from a Barcode Boy, running the game in MAME.

Usage: uv run python tools/oracle/record_famjock2.py --rompath DIR --codes FILE --out FILE

The game reads a card as a racehorse, a mare or a stallion depending on the
menu it is scanned from, so each code is recorded three times. For each menu
barcode_boy.lua starts a new game from an empty save, enters a name, walks to
that menu's バーコード item, answers the handshake, saves the machine, and for
each code reloads that state, scans it and prints the horse the game built at
$A8ED with the menu id at $AF36 and the Namco box bonus at $D90C. The first
horse byte is marked before every scan, so a scan the game did not take shows
as that mark and is left out.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).parent))

from record_game import HASH_PATH, HEADLESS, MAME_INI, MANIFEST, verify_artifact

HERE: Final = Path(__file__).parent
ARTIFACT: Final = "gameboy_famjock2"
BOOT_ARTIFACTS: Final = ("gameboy_dmg_boot", "gameboy_dmg_v0")
SOFTWARE: Final = "famjock2"
GAME: Final = "Family Jockey 2"
SCRIPT: Final = HERE / "barcode_boy.lua"
NAME_ENTRY: Final = (
    "700:Button A,900:Button A,1100:Button A,1300:Down,1360:Down,1420:Down,1480:Right,"
    "1540:Right,1600:Right,1660:Right,1720:Right,1780:Right,1840:Right,1900:Right,"
    "1960:Right,2020:Right,2080:Down,2140:Button A"
)
HORSE: Final = "0xa8ed"
HORSE_SIZE: Final = "7"
PEEKS: Final = "0xaf36,0xd90c"
SETTLE: Final = "150"
UNREAD: Final = "ee"
FIELDS: Final = 5
EMULATOR: Final = (
    "MAME 0.289, gameboy with no link device; tools/oracle/barcode_boy.lua answers "
    "the serial port the way a Barcode Boy does"
)
SCREEN: Final = (
    "each code is scanned from the バーコード item of the racehorse, mare and stallion "
    "menus of a new game; horse is the 7 bytes at $A8ED, menu the id at $AF36, bonus "
    "the Namco box bonus at $D90C"
)
SESSION_SECONDS: Final = "3000"
TIMEOUT_SECONDS: Final = 1500


@dataclass(frozen=True, slots=True)
class Menu:
    """One menu a card can be read from: its kind, the route to it, and when to save."""

    kind: str
    steps: str
    ready: str


MENUS: Final = (
    Menu(
        "racehorse",
        NAME_ENTRY + ",2700:Button A,2880:Button A,2980:Down,3040:Button A",
        "3150",
    ),
    Menu(
        "mare",
        NAME_ENTRY + ",2440:Button A,2600:Down,2660:Button A,2800:Down,2860:Down,2920:Down,"
        "2990:Button A",
        "3100",
    ),
    Menu(
        "stallion",
        NAME_ENTRY + ",2700:Button A,2880:Down,2940:Down,3000:Button A,3140:Down,3200:Down,"
        "3260:Button A",
        "3370",
    ),
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    verify_artifact(
        args.rompath, ARTIFACT, "place the famjock2 set dumped from your cartridge there"
    )
    for boot in BOOT_ARTIFACTS:
        verify_artifact(args.rompath, boot, "place the boot ROM dumped from your Game Boy there")
    cards = [
        card
        for menu in MENUS
        for card in parse(run_session(args.rompath, args.codes, menu), menu.kind)
    ]
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = json.dumps(fixture(cards, stamp), indent=1, ensure_ascii=False)
    args.out.write_text(text + "\n", encoding="utf-8")


def session_env(codes: Path, menu: Menu) -> dict[str, str]:
    return {
        **HEADLESS,
        "CODES": str(codes.resolve()),
        "RECORD_ADDR": HORSE,
        "RECORD_LEN": HORSE_SIZE,
        "STATUS_ADDR": HORSE,
        "READY_FRAME": menu.ready,
        "SETTLE": SETTLE,
        "BOOT_STEPS": menu.steps,
        "PEEK_ADDRS": PEEKS,
    }


def run_session(rompath: Path, codes: Path, menu: Menu) -> str:
    with tempfile.TemporaryDirectory() as scratch:
        (Path(scratch) / "mame.ini").write_text(MAME_INI)
        completed = subprocess.run(  # noqa: S603
            mame_command(rompath, Path(scratch) / "state", Path(scratch) / "save"),
            cwd=scratch,
            env={**os.environ, **session_env(codes, menu)},
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    return completed.stdout


def mame_command(rompath: Path, state: Path, save: Path) -> list[str]:
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
        "-nvram_directory",
        str(save),
        "-autoboot_script",
        str(SCRIPT),
    ]


def parse(output: str, kind: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == FIELDS and fields[0] == "REC" and fields[2] != UNREAD:
            peeks = bytes.fromhex(fields[4])
            records = [
                *records,
                {
                    "barcode": fields[1],
                    "kind": kind,
                    "horse": fields[3],
                    "menu": peeks[0],
                    "bonus": peeks[1],
                },
            ]
    return records


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
