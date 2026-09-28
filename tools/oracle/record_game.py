"""Feed barcodes to a Datach game running in MAME and record what it read.

Usage: uv run python tools/oracle/record_game.py --game ultraman --rompath DIR --codes FILE --out FILE

DIR holds MAME's nes_datach sets; FILE lists one barcode per line, optionally
followed by a swipe period in microseconds per module. Without a period the
code goes through MAME's barcode reader at its fixed rate; with one it is
swiped past the reader at that speed, which is how a code whose bars are 1, 2
and 4 modules wide gets read. The ROM is checked against
artifacts.manifest.json before anything runs, and each code gets its own
headless MAME session so no read inherits the one before it.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
MANIFEST = ROOT / "artifacts.manifest.json"
HASH_PATH = "/opt/homebrew/share/mame/hash"
MAME_INI = "window 1\nvideo none\nsound none\nskip_gameinfo 1\n"
HEADLESS = {"SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"}
SESSION_SECONDS = "90"
TIMEOUT_SECONDS = 150
PEEK = re.compile(r"PEEK (\w+) ((?:[0-9a-f]{2} ?)+)")


@dataclass(frozen=True)
class Game:
    software: str
    artifact: str
    menu: tuple[str, ...]
    scan_frame: int
    read_delay: int
    peeks: tuple[tuple[str, int], ...]
    accepted: tuple[tuple[str, int], ...]
    system: str = "nes"
    media: tuple[str, ...] = ()
    reader: str = ":nes_slot:datach:datach"


GAMES = {
    "ultraman": Game(
        software="dtc_ultr",
        artifact="datach_ultraman_prg",
        menu=("700 press Start", "750 press Down", "780 press Down", "820 press A"),
        scan_frame=1300,
        read_delay=600,
        peeks=(("02cd", 7), ("0312", 1)),
        accepted=(("0312", 0),),
    ),
    "sdgundam": Game(
        software="dtc_sdgn",
        artifact="datach_sdgundam_prg",
        menu=("1001 press Start", "1550 press Down", "1580 press Down", "1620 press A"),
        scan_frame=2700,
        read_delay=600,
        peeks=(("0460", 11), ("061c", 1)),
        accepted=(("0460", 1), ("061c", 0)),
    ),
    "yuyu": Game(
        software="dtc_yuyu",
        artifact="datach_yuyu_prg",
        menu=("1001 press Start", "1300 press Start", "1701 press Down", "1760 press A"),
        scan_frame=3100,
        read_delay=200,
        peeks=(("0322", 2),),
        accepted=(("0322", 0), ("0322", 1)),
    ),
    "jleague": Game(
        software="dtc_jltp",
        artifact="datach_jleague_prg",
        menu=(
            "1001 press Start",
            "1350 press Down",
            "1380 press Down",
            "1410 press Down",
            "1440 press Down",
            "1470 press Down",
            "1520 press A",
        ),
        scan_frame=2200,
        read_delay=500,
        peeks=(("02c2", 3),),
        accepted=(("02c2", 0), ("02c2", 1)),
    ),
    "barcodeworld": Game(
        software="barcodew",
        artifact="barcode_world_prg",
        menu=("700 press Start", "1101 press A"),
        scan_frame=1400,
        read_delay=600,
        peeks=(("6525", 11), ("650b", 13)),
        accepted=(("650b", 0),),
        system="famicom",
        media=("-exp", "barcode_battler", "-cart", "barcodew"),
        reader=":exp:barcode_battler:battler",
    ),
}
"""An unread code leaves 0 in both bytes, which is also Yusuke with no technique: the
analyzer cannot tell those two apart, so no such code should be recorded."""


def main() -> None:
    args = parse()
    game = GAMES[args.game]
    verify_rom(args.rompath, game)
    lines = [line.split() for line in args.codes.read_text().splitlines() if line.strip()]
    records = [record(game, words, run_session(args.rompath, game, words)) for words in lines]
    args.out.write_text(json.dumps(records, indent=1, ensure_ascii=False) + "\n")
    print(f"recorded {len(records)} codes to {args.out}")


def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record a Datach game's reads in MAME.")
    parser.add_argument("--game", choices=sorted(GAMES), required=True)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def verify_rom(rompath: Path, game: Game) -> None:
    artifacts = json.loads(MANIFEST.read_text())["artifacts"]
    entry = next(item for item in artifacts if item["id"] == game.artifact)
    rom = rompath / str(entry["path"])
    if not rom.is_file():
        sys.exit(
            f"no ROM at {rom}; place the nes_datach/{game.software} set dumped from your "
            "cartridge there"
        )
    digest = hashlib.sha256(rom.read_bytes()).hexdigest()
    if digest != entry["sha256"]:
        sys.exit(
            f"{rom} has SHA-256 {digest}, but the fixture was recorded with {entry['sha256']}, "
            f"the {entry['size']}-byte dump MAME's nes_datach list names; "
            "dump the cartridge again or use a copy that matches that list"
        )


def plan_lines(game: Game, words: list[str]) -> list[str]:
    code = words[0]
    feed = f"swipe {code} {words[1]}" if len(words) > 1 else f"scan {code}"
    frame = game.scan_frame + game.read_delay
    peeks = [f"{frame} peek {address} {length}" for address, length in game.peeks]
    return [*game.menu, f"{game.scan_frame} {feed}", *peeks, f"{frame + 5} exit"]


def run_session(rompath: Path, game: Game, words: list[str]) -> str:
    with tempfile.TemporaryDirectory() as scratch:
        plan = Path(scratch) / "plan.txt"
        plan.write_text("\n".join(plan_lines(game, words)) + "\n")
        (Path(scratch) / "mame.ini").write_text(MAME_INI)
        completed = subprocess.run(
            mame_command(rompath, game),
            cwd=scratch,
            env={**os.environ, **HEADLESS, "ORACLE_PLAN": str(plan), "READER": game.reader},
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    return completed.stdout


def mame_command(rompath: Path, game: Game) -> list[str]:
    media = game.media or ("-cart", "datach", "-cart2", game.software)
    return [
        "mame",
        game.system,
        *media,
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
        "-autoboot_script",
        str(HERE / "drive.lua"),
    ]


def record(game: Game, words: list[str], output: str) -> dict[str, object]:
    peeked = {
        address: bytes.fromhex(values.replace(" ", "")) for address, values in PEEK.findall(output)
    }
    missing = [address for address, _ in game.peeks if address not in peeked]
    if missing:
        message = (
            f"MAME never reported {', '.join(missing)} for {words[0]}; "
            "read its output for the reason"
        )
        raise RuntimeError(message)
    accepted = any(peeked[address][offset] != 0 for address, offset in game.accepted)
    entry: dict[str, object] = {"barcode": words[0], "accepted": accepted}
    if len(words) > 1:
        entry["swipe_us"] = int(words[1])
    return {**entry, **{name: values.hex(" ") for name, values in peeked.items()}}


if __name__ == "__main__":
    main()
