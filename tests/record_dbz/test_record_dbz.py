"""Tests for the tool that records what Datach Dragon Ball Z shows in MAME."""

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_dbz.py"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("record_dbz", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_plan_opens_the_scanning_room_then_scans_once_and_reports() -> None:
    lines = load().plan_lines("0022248300117")

    assert lines[:3] == ["640 press Start", "760 press Down", "800 press Start"]
    assert "1400 scan 0022248300117" in lines
    assert lines[-1].endswith(" exit")


def test_an_accepted_scan_becomes_a_full_record() -> None:
    output = "REPORT 0022248300117 type=1 char=0 level=1 hp=49500 bp=28250 dp=22750\n"

    entry = load().record("0022248300117", output)

    assert entry == {
        "barcode": "0022248300117",
        "accepted": True,
        "character": 0,
        "level": 1,
        "hp": 49500,
        "bp": 28250,
        "dp": 22750,
    }


def test_a_scan_the_game_left_unread_is_recorded_as_refused() -> None:
    output = "REPORT 20158231 type=0 char=0 level=0 hp=0 bp=0 dp=0\n"

    entry = load().record("20158231", output)

    assert entry == {"barcode": "20158231", "accepted": False}


def test_a_run_that_never_reported_fails_rather_than_passing_as_refused() -> None:
    with pytest.raises(RuntimeError, match="MAME never reported 20158231"):
        load().record("20158231", "")


def test_a_rom_with_the_wrong_digest_is_named_and_refused(tmp_path: Path) -> None:
    tool = load()
    entry = tool.manifest_entry()
    rom = tmp_path / entry["path"]
    rom.parent.mkdir(parents=True)
    rom.write_bytes(b"not the game")

    with pytest.raises(SystemExit, match=hashlib.sha256(b"not the game").hexdigest()):
        tool.verify_rom(tmp_path)


def test_a_missing_rom_says_where_it_was_looked_for(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="no ROM at"):
        load().verify_rom(tmp_path)


def test_the_manifest_entry_matches_the_recorded_fixture() -> None:
    entry = load().manifest_entry()
    fixture = json.loads((ROOT / "tests" / "fixtures" / "oracle" / "datach_dbz.json").read_text())

    assert entry["sha1"] == fixture["rom"]["sha1"]
    assert entry["size"] == fixture["rom"]["size"]
