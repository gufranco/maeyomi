"""Tests for the recorder that runs Card de Asobu in the scripted GBE+, without running it.

The script, the configuration, the command line and the screen fingerprint are
checked here; recording itself needs the game and the built emulator, so it
runs by hand.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_cardasobu.py"
CODE = "*AA01C0RD00V01*"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("record_cardasobu", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_script_swipes_the_card_then_photographs_the_answer() -> None:
    tool = load()

    lines = tool.script(CODE, Path("/shot.ppm")).splitlines()

    assert lines == [
        f"{tool.SWIPE_FRAME} card {CODE}",
        f"{tool.SHOT_FRAME} shot /shot.ppm",
        f"{tool.SHOT_FRAME + 1} exit",
    ]


def test_the_configuration_plugs_in_the_hcv_1000_and_mutes_the_game() -> None:
    assert load().CONFIG == "[#slot2_device:6]\n[#mute:1]\n"


def test_the_command_runs_the_built_emulator_on_the_cartridge() -> None:
    tool = load()

    command = tool.command(Path("/gbe"), Path("/roms"))

    assert command == ["/gbe", str(Path("/roms/nds/cardasobu.nds").resolve())]


def test_a_screen_is_fingerprinted_by_its_bytes(tmp_path: Path) -> None:
    shot = tmp_path / "shot.ppm"
    shot.write_bytes(b"P6\n1 1\n255\n\x00\x00\x00")

    fingerprint = load().fingerprint(shot)

    assert fingerprint == "3ff6c5463ace13c0"


def test_a_screen_never_drawn_has_no_fingerprint(tmp_path: Path) -> None:
    assert load().fingerprint(tmp_path / "missing.ppm") == ""
