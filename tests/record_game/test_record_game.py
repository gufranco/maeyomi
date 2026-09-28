"""Tests for the tool that records what a Datach game reads in MAME."""

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_game.py"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("record_game", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_plan_opens_the_analyzer_then_scans_and_peeks() -> None:
    tool = load()

    lines = tool.plan_lines(tool.GAMES["ultraman"], ["0315424322677"])

    assert lines[:4] == ["700 press Start", "750 press Down", "780 press Down", "820 press A"]
    assert "1300 scan 0315424322677" in lines
    assert "1900 peek 02cd 7" in lines
    assert lines[-1] == "1905 exit"


def test_a_period_after_the_code_swipes_it_at_that_speed() -> None:
    tool = load()

    lines = tool.plan_lines(tool.GAMES["ultraman"], ["0310026276212", "450"])

    assert "1300 swipe 0310026276212 450" in lines


def test_a_read_becomes_a_record_of_every_peeked_byte() -> None:
    tool = load()
    output = "PEEK 02cd 03 20 1c f4 1a c0 12\nPEEK 0312 01\n"

    entry = tool.record(tool.GAMES["ultraman"], ["0315424322677"], output)

    assert entry == {
        "barcode": "0315424322677",
        "accepted": True,
        "02cd": "03 20 1c f4 1a c0 12",
        "0312": "01",
    }


def test_a_swiped_read_keeps_its_speed_and_an_unread_one_is_refused() -> None:
    tool = load()
    output = "PEEK 02cd 00 00 00 00 00 00 00\nPEEK 0312 00\n"

    entry = tool.record(tool.GAMES["ultraman"], ["0310026276212", "300"], output)

    assert entry["accepted"] is False
    assert entry["swipe_us"] == 300


def test_a_run_that_never_reported_fails_rather_than_passing_as_refused() -> None:
    tool = load()

    with pytest.raises(RuntimeError, match="MAME never reported 02cd, 0312"):
        tool.record(tool.GAMES["ultraman"], ["0315424322677"], "")


def test_a_rom_with_the_wrong_digest_is_named_and_refused(tmp_path: Path) -> None:
    tool = load()
    game = tool.GAMES["ultraman"]
    rom = (
        tmp_path / "nes_datach" / "dtc_ultr" / "datach - ultraman club - supokon fight (japan).prg"
    )
    rom.parent.mkdir(parents=True)
    rom.write_bytes(b"not the game")

    with pytest.raises(SystemExit, match=hashlib.sha256(b"not the game").hexdigest()):
        tool.verify_rom(tmp_path, game)


def test_a_missing_rom_says_where_it_was_looked_for(tmp_path: Path) -> None:
    tool = load()

    with pytest.raises(SystemExit, match="no ROM at"):
        tool.verify_rom(tmp_path, tool.GAMES["ultraman"])


def test_every_game_the_tool_records_names_a_rom_in_the_manifest() -> None:
    tool = load()
    manifest = json.loads((ROOT / "artifacts.manifest.json").read_text())
    ids = {entry["id"] for entry in manifest["artifacts"]}

    assert {game.artifact for game in tool.GAMES.values()} <= ids


def test_the_ultraman_fixture_was_recorded_with_the_rom_the_manifest_names() -> None:
    manifest = json.loads((ROOT / "artifacts.manifest.json").read_text())
    entry = next(item for item in manifest["artifacts"] if item["id"] == "datach_ultraman_prg")
    fixture = json.loads(
        (ROOT / "tests" / "fixtures" / "oracle" / "datach_ultraman.json").read_text()
    )

    assert entry["sha1"] == fixture["rom"]["sha1"]
    assert entry["size"] == fixture["rom"]["size"]
