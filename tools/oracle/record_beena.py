"""Record which stripe cards an Advanced Pico Beena game reads, scanning each in MAME.

Usage: uv run python tools/oracle/record_beena.py --rompath DIR --game densha --codes FILE --out FILE

A Beena card carries twelve bar positions along one edge, the leftmost first,
and the reader hands the console the twelve bits they spell. MAME's card device
takes that value only from a software list, so each code is written into a
software list of its own beside a blank card image, and MAME runs the game with
it: turn to the page that scans, swipe the card, and save the screen before the
swipe and every 200 frames after it. A card the game reads brings up its own
screen for a while or changes the scene on the page; one it ignores leaves the
page exactly as it was, its animation aside. What is recorded is the largest
share of the screen that changed and a fingerprint of that screen.
"""

import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).parent))

from record_game import HEADLESS, verify_artifact

BIOS: Final = ("beena_bios", "beena_midipcm")
BIOS_DIRECTORY: Final = "beena"
LIST: Final = "sega_beena_cart"
SOFTWARE: Final = "probe"
TIMEOUT_SECONDS: Final = 300
WORKERS: Final = 6
FINGERPRINT_LENGTH: Final = 16
FINGERPRINT_SIZE: Final = (16, 16)
READ_SHARE: Final = 0.02
CHANGE_FLOOR: Final = 24
SHARE_DIGITS: Final = 2
SHOT_EVERY: Final = 200
MINIMUM_SHOTS: Final = 2
BLANK_SIZE: Final = (8, 8)
SCRIPT: Final = """
local frame = 0
local scan = manager.machine.ioport.ports[":cardslot:{reader}:IO"].fields["Scan Card"]
emu.register_frame_done(function()
  frame = frame + 1
  if frame == {page_frame} then manager.machine.ioport.ports[":PAGE"].fields["Selected Page"]:set_value({page}) end
  if frame == {before_frame} then manager.machine.video:snapshot() end
  if frame == {scan_frame} then scan:set_value(1) end
  if frame == {scan_frame} + 10 then scan:set_value(0) end
  if frame > {scan_frame} and (frame - {scan_frame}) % {shot_every} == 0 then manager.machine.video:snapshot() end
  if frame == {after_frame} then manager.machine:exit() end
end)
"""


@dataclass(frozen=True, slots=True)
class Game:
    """Where a game's cartridge sits, which reader it takes and where it scans."""

    title: str
    cartridge: str
    cart_path: str
    reader: str
    page: int
    page_frame: int
    scan_frame: int
    after_frame: int


GAMES: Final = {
    "densha": Game(
        title="Densha Daishuugou! Card de Asobou",
        cartridge="beena_densha",
        cart_path="beena_carts/denshaca.bin",
        reader="rd2061",
        page=1,
        page_frame=2300,
        scan_frame=3000,
        after_frame=5000,
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--game", choices=sorted(GAMES), required=True)
    parser.add_argument("--codes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    game = GAMES[args.game]
    for artifact in (*BIOS, game.cartridge):
        verify_artifact(args.rompath, artifact, "place the dump from your own hardware there")
    codes = [line.strip() for line in args.codes.read_text().splitlines() if line.strip()]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        readings = list(pool.map(lambda code: run_session(args.rompath, game, code), codes))
    fixture = {
        "game": game.title,
        "emulator": f"MAME 0.289 beena with the {game.reader} reader, page {game.page}",
        "recorded_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cards": readings,
    }
    args.out.write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def value(code: str) -> int:
    """The twelve bits the reader hands the console, the leftmost bar lowest."""
    return int(code[::-1], 2)


def _blank() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", BLANK_SIZE, "white").save(buffer, "PNG")
    return buffer.getvalue()


def write_list(here: Path, codes: tuple[str, ...]) -> None:
    """A software list holding one card per code, each beside a blank card image."""
    image = _blank()
    cards = here / "roms" / LIST / SOFTWARE
    cards.mkdir(parents=True, exist_ok=True)
    parts = []
    for number, code in enumerate(codes, 1):
        (cards / f"card{number}.png").write_bytes(image)
        parts.append(
            f'<part name="card{number}" interface="sega_9h0_0008_card">'
            f'<feature name="barcode" value="0x{value(code):04x}"/>'
            f'<dataarea name="card" size="{len(image)}"><rom name="card{number}.png" '
            f'size="{len(image)}" crc="{zlib.crc32(image):08x}" '
            f'sha1="{hashlib.sha1(image).hexdigest()}"/></dataarea></part>'  # noqa: S324
        )
    listing = (
        f'<?xml version="1.0"?><softwarelist name="{LIST}" description="{SOFTWARE}">'
        f'<software name="{SOFTWARE}"><description>{SOFTWARE}</description><year>2026</year>'
        f"<publisher>{SOFTWARE}</publisher>{''.join(parts)}</software></softwarelist>"
    )
    (here / "hash").mkdir(exist_ok=True)
    (here / "hash" / f"{LIST}.xml").write_text(listing, encoding="utf-8")


def changed(before: Path, after: Path) -> float:
    """The share of the screen that changed between two snapshots."""
    if not (before.is_file() and after.is_file()):
        return 0.0
    difference = ImageChops.difference(
        Image.open(before).convert("L"), Image.open(after).convert("L")
    )
    moved = sum(difference.histogram()[CHANGE_FLOOR + 1 :])
    return round(moved / (difference.width * difference.height), SHARE_DIGITS)


def fingerprint(shot: Path) -> str:
    if not shot.is_file():
        return ""
    small = Image.open(shot).convert("L").resize(FINGERPRINT_SIZE)
    return hashlib.sha256(small.tobytes()).hexdigest()[:FINGERPRINT_LENGTH]


def reading(code: str, share: float, screen: str) -> dict[str, str | float | bool]:
    return {
        "barcode": code,
        "value": hex(value(code)),
        "read": share >= READ_SHARE,
        "changed": share,
        "screen": screen,
    }


def judged(code: str, shots: list[Path]) -> dict[str, str | float | bool]:
    """The reading for the snapshot after the scan that differs most from the one before it."""
    if len(shots) < MINIMUM_SHOTS:
        return reading(code, 0.0, "")
    before, *afters = shots
    share, after = max((changed(before, after), after) for after in afters)
    return reading(code, share, fingerprint(after))


def run_session(rompath: Path, game: Game, code: str) -> dict[str, str | float | bool]:
    with tempfile.TemporaryDirectory() as scratch:
        here = Path(scratch)
        write_list(here, (code,))
        shutil.copytree(rompath / BIOS_DIRECTORY, here / "roms" / BIOS_DIRECTORY)
        (here / "scan.lua").write_text(
            SCRIPT.format(
                reader=game.reader,
                page=game.page,
                page_frame=game.page_frame,
                before_frame=game.scan_frame - 10,
                scan_frame=game.scan_frame,
                after_frame=game.after_frame,
                shot_every=SHOT_EVERY,
            )
        )
        subprocess.run(  # noqa: S603
            [
                "mame",
                "beena",
                "-rompath",
                str(here / "roms"),
                "-hashpath",
                str(here / "hash"),
                "-cart",
                str((rompath / game.cart_path).resolve()),
                "-cardslot",
                game.reader,
                "-card",
                f"{LIST}:{SOFTWARE}:card1",
                "-window",
                "-video",
                "soft",
                "-sound",
                "none",
                "-nothrottle",
                "-seconds_to_run",
                "120",
                "-snapshot_directory",
                str(here / "snap"),
                "-nvram_directory",
                str(here / "nv"),
                "-cfg_directory",
                str(here / "cfg"),
                "-autoboot_script",
                str(here / "scan.lua"),
            ],
            cwd=here,
            env={**os.environ, **HEADLESS},
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
        return judged(code, sorted((here / "snap").glob("*/*.png")))


if __name__ == "__main__":
    main()
