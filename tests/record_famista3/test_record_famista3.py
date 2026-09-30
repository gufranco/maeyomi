"""Tests for the tool that records what Famista 3 reads from a Barcode Boy in MAME."""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_famista3.py"
HOME_RUN = "8357933639923"
PLAYER = "03004140001801230eff0064ad01d400"
DUMP = "00" + "00" + PLAYER + "00" * 16 + "4d4a"
PITCHER_DUMP = "01" + "00" + PLAYER + "00" * 16 + "7626"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("record_famista3", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_each_scan_line_becomes_a_player_with_its_kind_and_place() -> None:
    records = load().parse(f"noise\nREC {HOME_RUN} 4d {DUMP}\nDONE\n")

    assert records == [{"barcode": HOME_RUN, "kind": "batter", "record": PLAYER, "pointer": "4d4a"}]


def test_the_game_s_own_flag_marks_a_pitcher() -> None:
    records = load().parse(f"REC {HOME_RUN} 76 {PITCHER_DUMP}\n")

    assert records[0]["kind"] == "pitcher"


def test_a_scan_the_game_did_not_take_is_left_out() -> None:
    assert load().parse(f"REC {HOME_RUN} ee {DUMP}\n") == []


def test_the_fixture_names_the_rom_the_emulator_and_the_time() -> None:
    tool = load()

    fixture = tool.fixture([], "2026-09-30T18:00:00Z")

    assert fixture["software"] == "famista3"
    assert fixture["rom"] == {"sha1": "ac4b03e11e2ba135d0427c8b1da7de57c006b4a6", "size": 262144}
    assert "MAME 0.289" in str(fixture["emulator"])
    assert fixture["recorded_utc"] == "2026-09-30T18:00:00Z"


def test_the_session_walks_the_menus_to_the_barcode_screen(tmp_path: Path) -> None:
    tool = load()

    env = tool.session_env(tmp_path / "codes.txt")

    assert env["BOOT_STEPS"] == "700:Start,900:Down,960:Button A,1300:Button A"
    assert (env["RECORD_ADDR"], env["STATUS_ADDR"]) == ("0xc30e", "0xc330")


def test_mame_runs_headless_with_the_reader_script(tmp_path: Path) -> None:
    tool = load()

    command = tool.mame_command(tmp_path, tmp_path / "state")

    assert command[:3] == ["mame", "gameboy", "famista3"]
    assert command[command.index("-video") + 1] == "none"
    assert command[command.index("-autoboot_script") + 1].endswith("barcode_boy.lua")
