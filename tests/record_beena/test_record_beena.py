"""Tests for the recorder that scans Advanced Pico Beena cards in MAME, without running MAME.

The software list it writes, the card value it hands MAME and the way it
judges a scan are checked here; running the game needs the cartridge and the
console's BIOS, so recording runs by hand.
"""

import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

from PIL import Image

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_beena.py"


def load() -> ModuleType:
    sys.path.insert(0, str(TOOL.parent))
    spec = importlib.util.spec_from_file_location("record_beena", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_code_is_handed_to_mame_as_the_value_its_bars_spell() -> None:
    assert load().value("100010110011") == 0xCD1


def test_the_software_list_holds_one_card_per_code_with_its_value(tmp_path: Path) -> None:
    tool = load()

    tool.write_list(tmp_path, ("100010110011", "101000000011"))

    listing = (tmp_path / "hash" / "sega_beena_cart.xml").read_text(encoding="utf-8")
    values = re.findall(r'name="barcode" value="(0x[0-9a-f]+)"', listing)
    assert values == ["0x0cd1", "0x0c05"]
    assert (tmp_path / "roms" / "sega_beena_cart" / "probe" / "card1.png").is_file()


def test_a_screen_that_left_the_page_counts_as_read(tmp_path: Path) -> None:
    tool = load()
    before, after = tmp_path / "before.png", tmp_path / "after.png"
    Image.new("RGB", (40, 40), "white").save(before)
    Image.new("RGB", (40, 40), "black").save(after)

    assert tool.changed(before, after) == 1.0


def test_a_screen_that_only_moved_a_little_does_not(tmp_path: Path) -> None:
    tool = load()
    before, after = tmp_path / "before.png", tmp_path / "after.png"
    Image.new("RGB", (40, 40), "white").save(before)
    moved = Image.new("RGB", (40, 40), "white")
    moved.paste((0, 0, 0), (0, 0, 4, 4))
    moved.save(after)

    assert tool.changed(before, after) == 0.01


def test_a_missing_screen_counts_as_unread(tmp_path: Path) -> None:
    assert load().changed(tmp_path / "none.png", tmp_path / "none.png") == 0.0


def test_a_reading_names_the_code_its_value_and_whether_the_game_took_it() -> None:
    assert load().reading("100010110011", 0.9, "abc") == {
        "barcode": "100010110011",
        "value": "0xcd1",
        "read": True,
        "changed": 0.9,
        "screen": "abc",
    }


def test_the_snapshot_that_changed_most_after_the_scan_decides(tmp_path: Path) -> None:
    tool = load()
    shots = [tmp_path / f"{index}.png" for index in range(3)]
    Image.new("RGB", (40, 40), "white").save(shots[0])
    Image.new("RGB", (40, 40), "black").save(shots[1])
    Image.new("RGB", (40, 40), "white").save(shots[2])

    reading = tool.judged("100010110011", shots)

    assert (reading["read"], reading["changed"]) == (True, 1.0)


def test_a_session_with_too_few_snapshots_counts_as_unread() -> None:
    assert load().judged("100010110011", [])["read"] is False
