"""Record which stripe cards a Sega Toys card game reads, scanning each in MAME.

Usage: uv run python tools/oracle/record_beena.py --rompath DIR --game densha --codes FILE --out FILE

A Beena card carries twelve bar positions along one edge, the leftmost first,
and the reader hands the console the twelve bits they spell. MAME's card device
takes that value only from a software list, so each code is written into a
software list of its own beside a blank card image, and MAME runs the game with
it: turn to the page that scans, swipe the card, and save the screen before the
swipe and at a fixed interval after it. Each game gives its own sign that it
read a card. On Densha Daishuugou's station page a blank card, every place
empty, is scanned first; the page ends on the same screen for every card the
game ignores, so a code counts as read when its scan ends anywhere else.
Anpanman ABC's street scrolls on its own and some cards answer inside the
scene, so its own memory is read instead, with no video drawn: the low byte of
the word at $C00CD500 is where the game keeps the number less one of the card
it took. It is set to 255 before the swipe, and 300 frames later a code the
game read has replaced it while one it ignored has left it alone. The scene
itself also follows the console's clock, so only that byte is compared.

TV Ocha-Ken is a machine of its own rather than a cartridge: the same BIOS
boots a game held in flash, and its RD1831 reader takes cards with sixteen
places. Pressing its B button on the title starts a new day, and the room then
asks for a card; it is judged like Densha Daishuugou, against a blank card,
since a card it takes leaves the room for that card's scene.
"""

import argparse
import hashlib
import io
import json
import re
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
BEENA: Final = "beena"
LIST: Final = "sega_beena_cart"
BUTTON_HOLD: Final = 8
SOFTWARE: Final = "probe"
TIMEOUT_SECONDS: Final = 300
WORKERS: Final = 6
FINGERPRINT_LENGTH: Final = 16
FINGERPRINT_SIZE: Final = (16, 16)
CHANGE_FLOOR: Final = 24
SHARE_DIGITS: Final = 2
MARK: Final = re.compile(r"MARK (\d+)")
SENTINEL: Final = 0xFF
UNREAD: Final = -1
SCREEN: Final = "screen"
MEMORY: Final = "memory"
MINIMUM_SHOTS: Final = 2
BLANK_SIZE: Final = (8, 8)
SCRIPT: Final = """
local frame = 0
local scan = manager.machine.ioport.ports[":cardslot:{reader}:IO"].fields["Scan Card"]
local space = manager.machine.devices[":maincpu"].spaces["program"]
emu.register_frame_done(function()
  frame = frame + 1
{prime}
{start}
  if frame == {before_frame} then manager.machine.video:snapshot() end
  if frame == {scan_frame} then scan:set_value(1) end
  if frame == {scan_frame} + 10 then scan:set_value(0) end
  if frame > {scan_frame} and (frame - {scan_frame}) % {shot_every} == 0 then manager.machine.video:snapshot() end
  if frame == {after_frame} then
{report}
    manager.machine:exit()
  end
end)
"""


@dataclass(frozen=True, slots=True)
class Game:
    """Which machine runs a game, where its program sits, which reader it takes and where it scans."""

    title: str
    media: str
    media_path: str
    reader: str
    page: int
    page_frame: int
    scan_frame: int
    after_frame: int
    shot_every: int
    judge: str
    index: int = 0
    machine: str = BEENA
    software_list: str = LIST
    places: int = 12
    presses: tuple[int, ...] = ()


GAMES: Final = {
    "densha": Game(
        title="Densha Daishuugou! Card de Asobou",
        media="beena_densha",
        media_path="beena_carts/denshaca.bin",
        reader="rd2061",
        page=1,
        page_frame=2300,
        scan_frame=3000,
        after_frame=5000,
        shot_every=200,
        judge=SCREEN,
    ),
    "anpanman": Game(
        title="Soreike! Anpanman Card de Tanoshiku ABC",
        media="beena_anpanman",
        media_path="beena_carts/anpaabc.bin",
        reader="rd2061",
        page=1,
        page_frame=2300,
        scan_frame=3000,
        after_frame=3300,
        shot_every=300,
        judge=MEMORY,
        index=0xC00CD500,
    ),
    "tvochken": Game(
        title="TV Ocha-Ken",
        media="tvochken_flash",
        media_path="tvochken/m5m29gt320vp-80.u3",
        reader="rd1831",
        page=0,
        page_frame=0,
        scan_frame=3000,
        after_frame=3600,
        shot_every=100,
        judge=SCREEN,
        machine="tvochken",
        software_list="tvochken",
        places=16,
        presses=(900, 1500, 2100),
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
    for artifact in (*BIOS, game.media):
        verify_artifact(args.rompath, artifact, "place the dump from your own hardware there")
    codes = [line.strip() for line in args.codes.read_text().splitlines() if line.strip()]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        blank, *readings = pool.map(
            lambda code: run_session(args.rompath, game, code), (blank_code(game), *codes)
        )
    fixture = {
        "game": game.title,
        "emulator": f"MAME 0.289 {game.machine} with the {game.reader} reader, {where(game)}",
        "recorded_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ignored_screen": blank["screen"],
        "cards": marked(readings, str(blank["screen"]), game),
    }
    args.out.write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def blank_code(game: Game) -> str:
    """A card with every place of the game's track empty."""
    return "0" * game.places


def where(game: Game) -> str:
    """Where in the game the cards were scanned."""
    if game.machine == BEENA:
        return f"page {game.page}"
    return "the room after a new day starts"


def value(code: str) -> int:
    """The bits the reader hands the console, the leftmost bar lowest."""
    return int(code[::-1], 2)


def _blank() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", BLANK_SIZE, "white").save(buffer, "PNG")
    return buffer.getvalue()


def write_list(here: Path, codes: tuple[str, ...], name: str) -> None:
    """A software list of the given name holding one card per code, each beside a blank card image."""
    image = _blank()
    cards = here / "roms" / name / SOFTWARE
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
        f'<?xml version="1.0"?><softwarelist name="{name}" description="{SOFTWARE}">'
        f'<software name="{SOFTWARE}"><description>{SOFTWARE}</description><year>2026</year>'
        f"<publisher>{SOFTWARE}</publisher>{''.join(parts)}</software></softwarelist>"
    )
    (here / "hash").mkdir(exist_ok=True)
    (here / "hash" / f"{name}.xml").write_text(listing, encoding="utf-8")


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


def reading(code: str, share: float, screen: str, index: int) -> dict[str, str | float | bool]:
    return {
        "barcode": code,
        "value": hex(value(code)),
        "changed": share,
        "screen": screen,
        "index": index,
    }


def read(entry: dict[str, str | float | bool], ignored: str, game: Game) -> bool:
    """Whether a scan shows the game read the card, by the sign the game gives."""
    if game.judge == MEMORY:
        return int(entry["index"]) not in {SENTINEL, UNREAD}
    return entry["screen"] not in {ignored, ""}


def marked(
    readings: list[dict[str, str | float | bool]], ignored: str, game: Game
) -> list[dict[str, str | float | bool]]:
    """Each reading, marked read or not by the game's sign."""
    return [{**entry, "read": read(entry, ignored, game)} for entry in readings]


def mark(output: str) -> int:
    """The index byte the session printed, or UNREAD when it printed none."""
    found = MARK.search(output)
    return UNREAD if found is None else int(found.group(1))


def lines(game: Game) -> tuple[str, str]:
    """The Lua that primes the index byte before the swipe and reports it after, for a memory game."""
    if game.judge != MEMORY:
        return "", ""
    keep = f"(space:read_u32({game.index}) & 0xFFFFFF00)"
    prime = (
        f"  if frame == {game.scan_frame - 10} then "
        f"space:write_u32({game.index}, {keep} | {SENTINEL}) end"
    )
    report = f'    print(string.format("MARK %d", space:read_u32({game.index}) & 255))'
    return prime, report


def judged(code: str, shots: list[Path], memory: int) -> dict[str, str | float | bool]:
    """The snapshot after the scan that differs most, with what the game's memory held."""
    if len(shots) < MINIMUM_SHOTS:
        return reading(code, 0.0, "", memory)
    before, *afters = shots
    share, after = max((changed(before, after), after) for after in afters)
    return reading(code, share, fingerprint(after), memory)


def start(game: Game) -> str:
    """The Lua that brings a game to where it scans: a page turned, or a button pressed."""
    if game.machine == BEENA:
        return (
            f"  if frame == {game.page_frame} then manager.machine.ioport.ports"
            f'[":PAGE"].fields["Selected Page"]:set_value({game.page}) end'
        )
    button = 'manager.machine.ioport.ports[":BUTTONS"].fields["B"]'
    return "\n".join(
        f"  if frame == {at} then {button}:set_value(1) end\n"
        f"  if frame == {at + BUTTON_HOLD} then {button}:set_value(0) end"
        for at in game.presses
    )


def script(game: Game) -> str:
    """The Lua session that scans one card and snapshots what the game does."""
    prime, report = lines(game)
    return SCRIPT.format(
        reader=game.reader,
        start=start(game),
        before_frame=game.scan_frame - 10,
        scan_frame=game.scan_frame,
        after_frame=game.after_frame,
        shot_every=game.shot_every,
        prime=prime,
        report=report,
    )


def stage(rompath: Path, here: Path, game: Game) -> None:
    """The BIOS, and a machine's own flash, where MAME looks for the machine's ROMs."""
    shutil.copytree(rompath / BIOS_DIRECTORY, here / "roms" / game.machine, dirs_exist_ok=True)
    if game.machine != BEENA:
        shutil.copy2(rompath / game.media_path, here / "roms" / game.machine)


def arguments(game: Game, here: Path, rompath: Path) -> list[str]:
    """The MAME command line for one scanning session."""
    media = [] if game.machine != BEENA else ["-cart", str((rompath / game.media_path).resolve())]
    return [
        "mame",
        game.machine,
        "-rompath",
        str(here / "roms"),
        "-hashpath",
        str(here / "hash"),
        *media,
        "-cardslot",
        game.reader,
        "-card",
        f"{game.software_list}:{SOFTWARE}:card1",
        "-window",
        "-video",
        "none" if game.judge == MEMORY else "soft",
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
    ]


def run_session(rompath: Path, game: Game, code: str) -> dict[str, str | float | bool]:
    with tempfile.TemporaryDirectory() as scratch:
        here = Path(scratch)
        write_list(here, (code,), game.software_list)
        stage(rompath, here, game)
        (here / "scan.lua").write_text(script(game))
        finished = subprocess.run(  # noqa: S603
            arguments(game, here, rompath),
            cwd=here,
            env={**os.environ, **HEADLESS},
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
        shots = sorted((here / "snap").glob("*/*.png"))
        return judged(code, shots, mark(finished.stdout))


if __name__ == "__main__":
    main()
