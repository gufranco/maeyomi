"""Tests for the tool that records what Monster Maker reads from a Barcode Boy in MAME."""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_monster_maker.py"
LORIEN = "9998017308336"
PARTY = "1100000000000041"
ADVENTURE = "1118013400300447"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("record_monster_maker", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_each_scan_line_becomes_a_record_keyed_by_its_code() -> None:
    records = load().parse(f"noise\nREC {LORIEN} 00 {PARTY}\nDONE\n")

    assert records == {LORIEN: PARTY}


def test_a_scan_the_game_did_not_take_is_left_out() -> None:
    records = load().parse(f"REC {LORIEN} ee {PARTY}\n")

    assert records == {}


def test_the_two_readings_of_a_code_are_paired() -> None:
    tool = load()

    cards = tool.pair({LORIEN: PARTY}, {LORIEN: ADVENTURE})

    assert cards == [{"barcode": LORIEN, "party": PARTY, "adventure": ADVENTURE}]


def test_a_code_read_in_only_one_mode_is_left_out() -> None:
    assert load().pair({LORIEN: PARTY}, {}) == []


def test_the_fixture_names_the_rom_the_emulator_and_the_time() -> None:
    tool = load()
    cards = [{"barcode": LORIEN, "party": PARTY, "adventure": ADVENTURE}]

    fixture = tool.fixture(cards, "2026-09-30T18:00:00Z")

    assert fixture["software"] == "monstmkb"
    assert fixture["rom"] == {"sha1": "f7a101338c4eebcdcc1e5d9082a30caa2d706969", "size": 131072}
    assert "MAME 0.289" in str(fixture["emulator"])
    assert fixture["recorded_utc"] == "2026-09-30T18:00:00Z"
    assert fixture["cards"] == cards


def test_each_mode_runs_with_the_game_s_own_flag_set(tmp_path: Path) -> None:
    tool = load()

    party = tool.session_env(tmp_path / "codes.txt", tool.PARTY_MODE)
    adventure = tool.session_env(tmp_path / "codes.txt", tool.ADVENTURE_MODE)

    assert party["POKE_VALUE"] == "0"
    assert adventure["POKE_VALUE"] == "1"
    assert adventure["POKE_ADDR"] == "0xc67f"
    assert adventure["RECORD_ADDR"] == "0xc9c3"
    assert (adventure["CAPTURE_ADDR"], adventure["CAPTURE_PC"]) == ("0xc679", "0x6af6")


def test_mame_runs_headless_with_the_reader_script(tmp_path: Path) -> None:
    tool = load()

    command = tool.mame_command(tmp_path, tmp_path / "state")

    assert command[:3] == ["mame", "gameboy", "monstmkb"]
    assert command[command.index("-video") + 1] == "none"
    assert command[command.index("-sound") + 1] == "none"
    assert command[command.index("-autoboot_script") + 1].endswith("barcode_boy.lua")
