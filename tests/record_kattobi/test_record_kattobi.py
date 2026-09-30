"""Tests for the tool that records what Kattobi Road reads from a Barcode Boy in MAME."""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_kattobi.py"
TRUCK = "4902105002063"
RECORD = "ccabdcb0d9c4de200326e300a202320f1f2d394c4a40270e48b00000ffbc0000"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("record_kattobi", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_each_scan_line_becomes_a_record() -> None:
    records = load().parse(f"noise\nREC {TRUCK} cc {RECORD}\nDONE\n")

    assert records == [{"barcode": TRUCK, "record": RECORD}]


def test_a_scan_the_game_did_not_take_is_left_out() -> None:
    assert load().parse(f"REC {TRUCK} ee {RECORD}\n") == []


def test_the_fixture_names_the_rom_the_emulator_and_the_time() -> None:
    tool = load()

    fixture = tool.fixture([{"barcode": TRUCK, "record": RECORD}], "2026-09-30T18:00:00Z")

    assert fixture["software"] == "kattobi"
    assert fixture["rom"] == {"sha1": "7ac064a877ecc8247dfb7213722dbd0f4be665f0", "size": 131072}
    assert "MAME 0.289" in str(fixture["emulator"])
    assert fixture["recorded_utc"] == "2026-09-30T18:00:00Z"
    assert fixture["cards"] == [{"barcode": TRUCK, "record": RECORD}]


def test_the_session_walks_the_menus_to_the_barcode_screen(tmp_path: Path) -> None:
    tool = load()

    env = tool.session_env(tmp_path / "codes.txt")

    assert env["BOOT_STEPS"].endswith("1250:Down,1320:Button A")
    assert (env["RECORD_ADDR"], env["STATUS_ADDR"]) == ("0xc980", "0xc980")


def test_mame_runs_headless_with_the_reader_script(tmp_path: Path) -> None:
    tool = load()

    command = tool.mame_command(tmp_path, tmp_path / "state")

    assert command[:3] == ["mame", "gameboy", "kattobi"]
    assert command[command.index("-video") + 1] == "none"
    assert command[command.index("-autoboot_script") + 1].endswith("barcode_boy.lua")
