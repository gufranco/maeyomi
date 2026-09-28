"""Feed barcodes to a barcode game running in MAME and record what it read.

Usage: uv run python tools/oracle/record_game.py --game ultraman --rompath DIR --codes FILE --out FILE

DIR holds MAME's software list sets, laid out as MAME's rompath expects; FILE
lists one barcode per line, optionally followed by a swipe period in
microseconds per module. Without a period the
code goes through MAME's barcode reader at its fixed rate; with one it is
swiped past the reader at that speed, which is how a code whose bars are 1, 2
and 4 modules wide gets read. The ROM is checked against
artifacts.manifest.json before anything runs, and each code gets its own
headless MAME session so no read inherits the one before it.

A Super Famicom game gets its code through the drive script's own Barcode
Battler II interface, because MAME 0.289's sends every digit one bit out of
place.
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
from typing import Final

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
MANIFEST = ROOT / "artifacts.manifest.json"
HASH_PATH = "/opt/homebrew/share/mame/hash"
MAME_INI = "window 1\nvideo none\nsound none\nskip_gameinfo 1\n"
HEADLESS = {"SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"}
SESSION_SECONDS = "90"
TIMEOUT_SECONDS = 150
PEEK = re.compile(r"PEEK (\w+) ((?:[0-9a-f]{2} ?)+)")
CATCH = re.compile(r"CATCH (\w+) ([0-9a-f]{2})")
CATCH_LEAD = 10
BREAK_FRAME = 10
PAIR_GAP = 300
HIT = re.compile(r"HIT (\S+ [0-9a-f]{2})")
UNMATCHED = "ff"
SNES = "snes"
SNES_PORT = ("-ctrl2", "barcode_battler", "-cart")
SNES_READER = ":ctrl2:barcode_battler:battler"
SNES_EXTRAS = ("snes_spc700_ipl",)


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
    feed: str = "scan"
    extras: tuple[str, ...] = ()
    catches: tuple[str, ...] = ()
    seconds: str = SESSION_SECONDS
    breakpoints: tuple[tuple[str, str], ...] = ()
    paired: bool = False


DORAEMON2_PASSWORD: Final = (
    "900 press Start",
    "1200 press Start",
    "1500 press Start",
    "1620 press Down",
    "1680 press A",
)
DORAEMON3_PASSWORD: Final = (
    "1500 press Start",
    "1950 press Start",
    "3200 press Start",
    "3300 press Right",
    "3350 press A",
)
DORAEMON3_PLAY: Final = (
    "1500 press Start",
    "1950 press Start",
    "3200 press Start",
    "3300 press A",
    *(f"{frame} press Start" for frame in range(3450, 4651, 60)),
    "5000 press Select",
)
EXCITE95_OPEN_MATCH: Final = (
    "700 press Start",
    "1000 press Start",
    "1300 press Start",
    *(f"{frame} press Down" for frame in range(1400, 1461, 20)),
    "1500 press Left",
    *(f"{frame} press Up" for frame in range(1540, 1601, 20)),
    *(f"{frame} press Start" for frame in range(1650, 2101, 150)),
)
DSLAYER2_BRANCHES: Final = (
    ("c1e48e", "WARP"),
    ("c1e9fc", "ITEM"),
    ("c1e5a9", "ENDING"),
    ("c1e669", "BOOST"),
    ("c1e6de", "BOOST"),
    ("c1e791", "BOOST"),
    ("c1e711", "MONSTERS"),
    ("c1e7c4", "SOUND"),
    ("c1e891", "USE"),
    ("c1e964", "CHAP"),
    ("c1eace", "EXIT"),
    ("c1eaf7", "EXIT"),
)
"""The branches of $C1:E43F, each outcome's own entry point, and its two exits."""
DSLAYER2_FIELD: Final = (
    "700 press Start",
    "1000 press Start",
    "1250 press Down",
    "1450 press A",
    "1700 press A",
    *(f"{frame} press A" for frame in range(2000, 4701, 300)),
    "5100 press A",
    "5700 press B",
    "5900 press X",
)
EXCITE94_FRIENDLY: Final = (
    *(f"{frame} press Start" for frame in (600, 900, 1200, 1500, 1650, 1770)),
    "1850 press Down",
    *(f"{frame} press Start" for frame in (1890, 2010, 2130, 2250)),
)
BATTLE_RUSH_FACTORY: Final = (
    "700 press Start",
    "800 press Down",
    "900 press Down",
    "1020 press Start",
    "1100 poke 05a2 02",
    "1101 poke 05a3 12",
    "1150 press Down",
    "1250 press Start",
    "2400 press A",
    "2700 press A",
    "3900 press A",
)
"""VS BATTLE, VS COM, Robo Factory; the pokes pass the save chip MAME only partly emulates."""
YOUSEI_FILE: Final = "{rompath}/snes/doraemon/shvc-dr-1.u1"
"""MAME's list entry for this cartridge names no ROM mapping and boots it as LoROM, a black
screen; passed as a file, MAME reads the HiROM mapping from the ROM's own header."""
YOUSEI_TITLE: Final = tuple(f"{frame} press Start" for frame in (300, 600, 900, 1300, 1900))
YOUSEI_MAP: Final = (
    *YOUSEI_TITLE,
    "2100 press Start",
    *(f"{frame} press A" for frame in range(2200, 7961, 40)),
    "8200 press Start",
    "8400 press Start",
    "8600 press Select",
    "8800 press Select",
)


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
    "senki": Game(
        software="conveni",
        artifact="senki_rom",
        menu=(
            "700 press Start",
            "1000 press Start",
            "1300 press Down",
            "1340 press A",
            "1500 press A",
            "1700 press A",
            "1950 press A",
        ),
        scan_frame=2100,
        read_delay=190,
        peeks=(("0890", 26), ("07b7", 13)),
        accepted=(("07b7", 0),),
        system=SNES,
        media=(*SNES_PORT, "conveni"),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
    ),
    "lupin": Game(
        software="lupin3",
        artifact="lupin_rom",
        menu=("500 press Start", "760 press Start", "860 press Down", "900 press Start"),
        scan_frame=1150,
        read_delay=110,
        peeks=(("05b9", 13),),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, "lupin3"),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
        catches=("05b3",),
    ),
    "donald": Game(
        software="donaldd",
        artifact="donald_rom",
        menu=("700 press Start", "1000 press Start", "1200 press Down", "1260 press Start"),
        scan_frame=1500,
        read_delay=60,
        peeks=(("05c3", 3), ("05c9", 13), ("006c", 5)),
        accepted=(("05c3", 1),),
        system=SNES,
        media=(*SNES_PORT, "donaldd"),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
    ),
    "spiderman": Game(
        software="spidfoes",
        artifact="spiderman_rom",
        menu=("650 press Start", "720 press Down", "760 press Start"),
        scan_frame=950,
        read_delay=50,
        peeks=(("0e86", 1), ("7e2019", 3), ("03a0", 10)),
        accepted=(("0e86", 0),),
        system=SNES,
        media=(*SNES_PORT, "spidfoes"),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
    ),
    "alice": Game(
        software="alicepnt",
        artifact="alice_rom",
        menu=("1700 press Start", "2000 press A", "2250 press A", "2450 press A"),
        scan_frame=2800,
        read_delay=100,
        peeks=(("1805", 4), ("06f0", 13)),
        accepted=(("1805", 0),),
        system=SNES,
        media=(*SNES_PORT, "alicepnt"),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
    ),
    "doraemon2": Game(
        software="doraemn2",
        artifact="doraemon2_rom",
        menu=DORAEMON2_PASSWORD,
        scan_frame=1820,
        read_delay=10,
        peeks=(("0598", 13),),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, "doraemn2"),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
        catches=("0c6b",),
    ),
    "doraemon2_menu": Game(
        software="doraemn2",
        artifact="doraemon2_rom",
        menu=(
            *DORAEMON2_PASSWORD,
            "1820 bbscan 4916858783100",
            "1860 press Start",
            "2100 press A",
            "2400 press Select",
        ),
        scan_frame=2500,
        read_delay=40,
        peeks=(("0b2a", 1), ("0b4e", 1), ("0598", 13)),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, "doraemn2"),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
        catches=("0b2a",),
    ),
    "doraemon3": Game(
        software="doraemn3",
        artifact="doraemon3_rom",
        menu=DORAEMON3_PASSWORD,
        scan_frame=3570,
        read_delay=10,
        peeks=(("03d3", 13),),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, "doraemn3"),
        reader=SNES_READER,
        feed="bbscan",
        extras=(*SNES_EXTRAS, "doraemon3_p1"),
        catches=("03d1",),
    ),
    "doraemon3_menu": Game(
        software="doraemn3",
        artifact="doraemon3_rom",
        menu=DORAEMON3_PLAY,
        scan_frame=5130,
        read_delay=20,
        peeks=(("03d3", 13),),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, "doraemn3"),
        reader=SNES_READER,
        feed="bbscan",
        extras=(*SNES_EXTRAS, "doraemon3_p1"),
        catches=("08ca",),
        seconds="120",
    ),
    "yousei": Game(
        software="doraemon",
        artifact="yousei_rom",
        menu=(*YOUSEI_TITLE, "2040 press Down", "2160 press Start"),
        scan_frame=2350,
        read_delay=50,
        peeks=(("7e0f48", 1), ("7e0fa7", 13)),
        accepted=(("7e0f48", 0),),
        system=SNES,
        media=(*SNES_PORT, YOUSEI_FILE),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
    ),
    "yousei_menu": Game(
        software="doraemon",
        artifact="yousei_rom",
        menu=YOUSEI_MAP,
        scan_frame=8950,
        read_delay=50,
        peeks=(("7e043d", 2), ("7e0fa7", 13)),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, YOUSEI_FILE),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
        seconds="170",
    ),
    "excite95": Game(
        software="jlexct95",
        artifact="excite95_rom",
        menu=EXCITE95_OPEN_MATCH,
        scan_frame=2250,
        read_delay=200,
        peeks=(("1b8e", 3), ("1b49", 13)),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, "jlexct95"),
        reader=SNES_READER,
        feed="bbscan",
        extras=(*SNES_EXTRAS, "excite95_p1"),
    ),
    "dslayer2": Game(
        software="dslayed2",
        artifact="dslayer2_rom",
        menu=("700 press Start", "1000 press Start"),
        scan_frame=1250,
        read_delay=50,
        peeks=(("0b57", 1),),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, "dslayed2"),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
        breakpoints=DSLAYER2_BRANCHES,
    ),
    "dslayer2_field": Game(
        software="dslayed2",
        artifact="dslayer2_rom",
        menu=DSLAYER2_FIELD,
        scan_frame=6100,
        read_delay=100,
        peeks=(("013d", 8),),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, "dslayed2"),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
        breakpoints=DSLAYER2_BRANCHES,
        seconds="120",
    ),
    "hatayama": Game(
        software="hatayama",
        artifact="hatayama_rom",
        menu=(
            "850 press Start",
            "1250 press Start",
            "1450 press Down",
            "1550 press Down",
            "1650 press A",
        ),
        scan_frame=1900,
        read_delay=90,
        peeks=(("7eff69", 20),),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, "hatayama"),
        reader=SNES_READER,
        feed="bbscan",
        extras=SNES_EXTRAS,
    ),
    "excite94": Game(
        software="jlexct94",
        artifact="excite94_rom",
        menu=EXCITE94_FRIENDLY,
        scan_frame=2350,
        read_delay=200,
        peeks=(("1d89", 12), ("1c76", 1), ("1e9c", 13)),
        accepted=(),
        system=SNES,
        media=(*SNES_PORT, "jlexct94"),
        reader=SNES_READER,
        feed="bbscan",
        extras=(*SNES_EXTRAS, "excite94_p1"),
    ),
    "battlerush": Game(
        software="dtc_brsh",
        artifact="datach_battlerush_prg",
        menu=BATTLE_RUSH_FACTORY,
        scan_frame=3100,
        read_delay=1200,
        peeks=(("0348", 48),),
        accepted=(),
        paired=True,
    ),
}
"""An unread code leaves 0 in both bytes, which is also Yusuke with no technique: the
analyzer cannot tell those two apart, so no such code should be recorded."""


def main() -> None:
    args = parse()
    game = GAMES[args.game]
    verify_rom(args.rompath, game)
    verify_extras(args.rompath, game)
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
    hint = f"place the {game.software} set dumped from your cartridge there"
    verify_artifact(rompath, game.artifact, hint)


def verify_extras(rompath: Path, game: Game) -> None:
    for extra in game.extras:
        verify_artifact(rompath, extra, "place the copy dumped from your console there")


def verify_artifact(rompath: Path, artifact: str, hint: str) -> None:
    artifacts = json.loads(MANIFEST.read_text())["artifacts"]
    entry = next(item for item in artifacts if item["id"] == artifact)
    rom = rompath / str(entry["path"])
    if not rom.is_file():
        sys.exit(f"no ROM at {rom}; {hint}")
    digest = hashlib.sha256(rom.read_bytes()).hexdigest()
    if digest != entry["sha256"]:
        sys.exit(
            f"{rom} has SHA-256 {digest}, but the fixture was recorded with {entry['sha256']}, "
            f"the {entry['size']}-byte dump MAME's software list names; "
            "dump the cartridge again or use a copy that matches that list"
        )


def plan_lines(game: Game, words: list[str]) -> list[str]:
    code = words[0]
    if game.paired:
        scans = [
            f"{game.scan_frame} {game.feed} {code}",
            f"{game.scan_frame + PAIR_GAP} {game.feed} {words[1]}",
        ]
    else:
        feed = f"swipe {code} {words[1]}" if len(words) > 1 else f"{game.feed} {code}"
        scans = [f"{game.scan_frame} {feed}"]
    frame = game.scan_frame + game.read_delay
    peeks = [f"{frame} peek {address} {length}" for address, length in game.peeks]
    catches = [f"{game.scan_frame - CATCH_LEAD} catch {address}" for address in game.catches]
    breaks = [f"{BREAK_FRAME} bp {address} {label}" for address, label in game.breakpoints]
    return [
        *breaks,
        *game.menu,
        *catches,
        *scans,
        *peeks,
        f"{frame + 5} exit",
    ]


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
    rompath_text = str(rompath.resolve())
    media = tuple(
        item.format(rompath=rompath_text)
        for item in game.media or ("-cart", "datach", "-cart2", game.software)
    )
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
        game.seconds,
        *(("-debug", "-debugger", "none") if game.breakpoints else ()),
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
    caught = first_catches(game, output)
    firsts = [caught[f"catch {address}"] for address in game.catches]
    accepted = any(peeked[address][offset] != 0 for address, offset in game.accepted) or any(
        value not in {None, UNMATCHED} for value in firsts
    )
    entry: dict[str, object] = {"barcode": words[0], "accepted": accepted, **caught}
    if game.paired:
        entry = {**entry, "second": words[1]}
    if game.breakpoints:
        entry = {**entry, "hits": HIT.findall(output)}
    if len(words) > 1 and not game.paired:
        entry["swipe_us"] = int(words[1])
    return {**entry, **{name: values.hex(" ") for name, values in peeked.items()}}


def first_catches(game: Game, output: str) -> dict[str, object]:
    """The first byte the game wrote to each caught address after the scan, and every write."""
    found = CATCH.findall(output)
    writes = {address: [value for at, value in found if at == address] for address in game.catches}
    return {
        **{
            f"catch {address}": (values[0] if values else None)
            for address, values in writes.items()
        },
        **{f"writes {address}": values for address, values in writes.items()},
    }


if __name__ == "__main__":
    main()
