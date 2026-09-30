"""Tests for the tool that records what Battle Space reads from a Barcode Boy in MAME."""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_barcode_boy.py"
BERSERKER = "4907981000301"
RECORD = "18" + "00" * 25 + "0228230a0084031e00982028230a0084031e009820f401"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("record_barcode_boy", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_each_scan_line_becomes_a_record() -> None:
    tool = load()
    output = f"noise\nREC {BERSERKER} 00 {RECORD}\nDONE\n"

    records = tool.parse(output)

    assert records == [{"barcode": BERSERKER, "status": 0, "record": RECORD}]


def test_an_ean_8_scan_is_recorded_too() -> None:
    records = load().parse(f"REC 35623014 00 {RECORD}\n")

    assert records == [{"barcode": "35623014", "status": 0, "record": RECORD}]


def test_lines_that_are_not_scans_are_ignored() -> None:
    assert load().parse("Average speed: 3912.56%\nDONE\n") == []


def test_the_fixture_names_the_rom_the_emulator_and_the_time() -> None:
    tool = load()

    fixture = tool.fixture(
        [{"barcode": BERSERKER, "status": 0, "record": RECORD}], "2026-09-30T18:00:00Z"
    )

    assert fixture["software"] == "bspace"
    assert fixture["rom"] == {"sha1": "76e47ad844abdde9eff09ea29a014f9a1eae5093", "size": 65536}
    assert "MAME 0.289" in str(fixture["emulator"])
    assert fixture["recorded_utc"] == "2026-09-30T18:00:00Z"
    assert fixture["cards"] == [{"barcode": BERSERKER, "status": 0, "record": RECORD}]


def test_mame_runs_headless_with_the_reader_script(tmp_path: Path) -> None:
    tool = load()

    command = tool.mame_command(tmp_path, tmp_path / "state")

    assert command[:3] == ["mame", "gameboy", "bspace"]
    assert command[command.index("-video") + 1] == "none"
    assert command[command.index("-sound") + 1] == "none"
    assert command[command.index("-autoboot_script") + 1].endswith("barcode_boy.lua")
