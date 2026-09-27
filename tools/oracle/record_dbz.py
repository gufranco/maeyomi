"""Feed barcodes to Datach Dragon Ball Z running in MAME and record what it shows.

Usage: uv run python tools/oracle/record_dbz.py --rompath DIR --codes FILE --out FILE

DIR holds MAME's nes_datach/dtc_dbz set; FILE lists one barcode per line. The
ROM is checked against artifacts.manifest.json before anything runs. Each code
gets its own headless MAME session, so a refused scan cannot inherit the card
the one before it left in memory: the game sets $03D0 only when it accepts.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
MANIFEST = ROOT / "artifacts.manifest.json"
ARTIFACT = "datach_dbz_prg"
HASH_PATH = "/opt/homebrew/share/mame/hash"
MENU = ("640 press Start", "760 press Down", "800 press Start")
SCAN_FRAME = 1400
REPORT_DELAY = 500
SESSION_SECONDS = "90"
TIMEOUT_SECONDS = 120
MAME_INI = "window 1\nvideo none\nsound none\nskip_gameinfo 1\n"
HEADLESS = {"SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"}
REPORT = re.compile(r"REPORT (\d+) type=(\d+) char=(\d+) level=(\d+) hp=(\d+) bp=(\d+) dp=(\d+)")


def main() -> None:
    args = parse()
    verify_rom(args.rompath)
    codes = [line.strip() for line in args.codes.read_text().splitlines() if line.strip()]
    records = [record(code, run_session(args.rompath, code)) for code in codes]
    args.out.write_text(json.dumps(records, indent=1) + "\n")
    print(f"recorded {len(records)} codes to {args.out}")


def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record Datach Dragon Ball Z reads in MAME.")
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def manifest_entry() -> dict[str, str | int]:
    artifacts = json.loads(MANIFEST.read_text())["artifacts"]
    return next(item for item in artifacts if item["id"] == ARTIFACT)


def verify_rom(rompath: Path) -> None:
    entry = manifest_entry()
    rom = rompath / str(entry["path"])
    if not rom.is_file():
        sys.exit(
            f"no ROM at {rom}; place the nes_datach/dtc_dbz set dumped from your cartridge there"
        )
    digest = hashlib.sha256(rom.read_bytes()).hexdigest()
    if digest != entry["sha256"]:
        sys.exit(
            f"{rom} has SHA-256 {digest}, but the fixture was recorded with {entry['sha256']}, "
            f"the {entry['size']}-byte dump MAME's nes_datach list names; "
            "dump the cartridge again or use a copy that matches that list"
        )


def plan_lines(code: str) -> list[str]:
    report = SCAN_FRAME + REPORT_DELAY
    return [*MENU, f"{SCAN_FRAME} scan {code}", f"{report} report {code}", f"{report + 10} exit"]


def run_session(rompath: Path, code: str) -> str:
    with tempfile.TemporaryDirectory() as scratch:
        plan = Path(scratch) / "plan.txt"
        plan.write_text("\n".join(plan_lines(code)) + "\n")
        (Path(scratch) / "mame.ini").write_text(MAME_INI)
        completed = subprocess.run(
            mame_command(rompath, scratch),
            cwd=scratch,
            env={**os.environ, **HEADLESS, "ORACLE_PLAN": str(plan)},
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    return completed.stdout


def mame_command(rompath: Path, scratch: str) -> list[str]:
    return [
        "mame",
        "nes",
        "-cart",
        "datach",
        "-cart2",
        "dtc_dbz",
        "-hashpath",
        HASH_PATH,
        "-rompath",
        str(rompath.resolve()),
        "-snapshot_directory",
        scratch,
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


def record(code: str, output: str) -> dict[str, str | int | bool]:
    match = next((found for found in REPORT.findall(output) if found[0] == code), None)
    if match is None:
        message = f"MAME never reported {code}; read its output for the reason"
        raise RuntimeError(message)
    _, kind, character, level, hp, bp, dp = match
    if kind == "0":
        return {"barcode": code, "accepted": False}
    return {
        "barcode": code,
        "accepted": True,
        "character": int(character),
        "level": int(level),
        "hp": int(hp),
        "bp": int(bp),
        "dp": int(dp),
    }


if __name__ == "__main__":
    main()
