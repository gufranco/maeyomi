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

    tool.write_list(tmp_path, ("100010110011", "101000000011"), "sega_beena_cart")

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


def test_a_reading_names_the_code_its_value_and_the_screen_it_ended_on() -> None:
    assert load().reading("100010110011", 0.9, "abc", 3) == {
        "barcode": "100010110011",
        "value": "0xcd1",
        "changed": 0.9,
        "screen": "abc",
        "index": 3,
    }


def test_a_scan_that_ends_where_an_ignored_card_does_is_unread() -> None:
    tool = load()
    readings = [
        tool.reading("100010110011", 0.2, "card", -1),
        tool.reading("100000000011", 0.06, "page", -1),
    ]

    marks = [entry["read"] for entry in tool.marked(readings, "page", tool.GAMES["densha"])]

    assert marks == [True, False]


def test_a_scan_with_no_screen_is_unread() -> None:
    tool = load()

    entry = tool.reading("100010110011", 0.0, "", -1)

    assert tool.marked([entry], "page", tool.GAMES["densha"])[0]["read"] is False


def test_a_memory_game_reads_a_card_that_replaced_the_primed_index() -> None:
    tool = load()
    readings = [
        tool.reading("100010110011", 0.06, "a", 3),
        tool.reading("100001111011", 0.06, "b", 0),
        tool.reading("100000000011", 0.16, "c", 255),
        tool.reading("100000000001", 0.06, "d", -1),
    ]

    marks = [entry["read"] for entry in tool.marked(readings, "", tool.GAMES["anpanman"])]

    assert marks == [True, True, False, False]


def test_the_index_is_parsed_from_what_the_session_printed() -> None:
    tool = load()

    assert (tool.mark("boot\nMARK 3\n"), tool.mark("no mark")) == (3, -1)


def test_only_a_memory_game_primes_and_reports_its_index() -> None:
    tool = load()
    prime, report = tool.lines(tool.GAMES["anpanman"])

    assert ("255" in prime, "MARK" in report) == (True, True)
    assert tool.lines(tool.GAMES["densha"]) == ("", "")


def test_the_snapshot_that_changed_most_after_the_scan_decides(tmp_path: Path) -> None:
    tool = load()
    shots = [tmp_path / f"{index}.png" for index in range(3)]
    Image.new("RGB", (40, 40), "white").save(shots[0])
    Image.new("RGB", (40, 40), "black").save(shots[1])
    Image.new("RGB", (40, 40), "white").save(shots[2])

    reading = tool.judged("100010110011", shots, -1)

    assert reading["changed"] == 1.0


def test_a_session_with_too_few_snapshots_counts_as_unread() -> None:
    assert load().judged("100010110011", [], -1)["screen"] == ""


def test_a_game_scans_a_blank_card_of_its_own_length() -> None:
    tool = load()

    assert (tool.blank_code(tool.GAMES["densha"]), tool.blank_code(tool.GAMES["tvochken"])) == (
        "0" * 12,
        "0" * 16,
    )


def test_the_software_list_takes_the_name_the_machine_looks_for(tmp_path: Path) -> None:
    tool = load()

    tool.write_list(tmp_path, ("1000000000000001",), "tvochken")

    listing = (tmp_path / "hash" / "tvochken.xml").read_text(encoding="utf-8")
    assert 'value="0x8001"' in listing
    assert (tmp_path / "roms" / "tvochken" / "probe" / "card1.png").is_file()


def test_a_cartridge_game_turns_the_page_and_a_machine_presses_its_button() -> None:
    tool = load()

    densha = tool.script(tool.GAMES["densha"])
    ochaken = tool.script(tool.GAMES["tvochken"])

    assert (":PAGE" in densha, ":BUTTONS" in densha) == (True, False)
    assert (":PAGE" in ochaken, ":BUTTONS" in ochaken) == (False, True)


def test_a_cartridge_game_is_run_on_the_beena_and_a_machine_on_its_own(tmp_path: Path) -> None:
    tool = load()

    densha = tool.arguments(tool.GAMES["densha"], tmp_path, tmp_path)
    ochaken = tool.arguments(tool.GAMES["tvochken"], tmp_path, tmp_path)

    assert (densha[1], "-cart" in densha) == ("beena", True)
    assert (ochaken[1], "-cart" in ochaken, ochaken[ochaken.index("-cardslot") + 1]) == (
        "tvochken",
        False,
        "rd1831",
    )


def test_a_machine_finds_the_bios_and_its_flash_under_its_own_name(tmp_path: Path) -> None:
    tool = load()
    rompath, here = tmp_path / "roms", tmp_path / "here"
    (rompath / "beena").mkdir(parents=True)
    (rompath / "beena" / "bios.bin").write_bytes(b"bios")
    (rompath / "tvochken").mkdir()
    (rompath / "tvochken" / "m5m29gt320vp-80.u3").write_bytes(b"flash")
    tool.write_list(here, ("0" * 16,), "tvochken")

    tool.stage(rompath, here, tool.GAMES["tvochken"])

    staged = sorted(path.name for path in (here / "roms" / "tvochken").iterdir())
    assert staged == ["bios.bin", "m5m29gt320vp-80.u3", "probe"]


def test_a_cartridge_game_finds_the_bios_under_the_beena(tmp_path: Path) -> None:
    tool = load()
    rompath, here = tmp_path / "roms", tmp_path / "here"
    (rompath / "beena").mkdir(parents=True)
    (rompath / "beena" / "bios.bin").write_bytes(b"bios")

    tool.stage(rompath, here, tool.GAMES["densha"])

    assert (here / "roms" / "beena" / "bios.bin").read_bytes() == b"bios"
