"""Tests for the recorder that runs Barcode Taisen Bardigun in MAME, without running MAME.

The route, the command line and the parsing of what the reader script prints
are checked here; recording itself needs the game, so it runs by hand.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_bardigun.py"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("record_bardigun", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_route_presses_start_then_a_through_the_story_and_after_the_scan() -> None:
    steps = load().STEPS.split(",")

    assert steps[0] == "1300:Start"
    assert "4500:Button A" in steps
    assert all(step.split(":")[1] in {"Start", "Button A"} for step in steps)


def test_a_hatched_card_is_read_as_its_species_and_record() -> None:
    line = "REC 4902370501445 0e 241 41e803022816221c9600ffffff0f0f0f0f070505055a"

    card = load().parse(line)

    assert card == {
        "barcode": "4902370501445",
        "species": 14,
        "record": "41e803022816221c9600ffffff0f0f0f0f070505055a",
    }


def test_a_scan_the_game_did_not_take_is_left_out() -> None:
    assert load().parse("REC 4902370501445 0e 0 00") is None


def test_a_line_that_is_not_a_record_is_ignored() -> None:
    assert load().parse("Average speed: 900%") is None


def test_the_command_runs_the_cartridge_headless_with_the_reader() -> None:
    tool = load()

    command = tool.mame_command(Path("/roms"), Path("/nv"))

    assert command[:2] == ["mame", "gameboy"]
    assert "-cart" in command
    assert command[command.index("-video") + 1] == "none"
    assert str(tool.SCRIPT) in command
