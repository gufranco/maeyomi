"""Tests for the tool that records what Family Jockey 2 reads from a Barcode Boy in MAME."""

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parent.parent.parent
TOOL = ROOT / "tools" / "oracle" / "record_famjock2.py"
CARD = "2378649896765"
HORSE = "07070507050501"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("record_famjock2", TOOL)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_each_scan_line_becomes_a_horse_with_its_menu_and_bonus() -> None:
    records = load().parse(f"noise\nREC {CARD} 07 {HORSE} 1201\nDONE\n", "mare")

    assert records == [{"barcode": CARD, "kind": "mare", "horse": HORSE, "menu": 0x12, "bonus": 1}]


def test_a_scan_the_game_did_not_take_is_left_out() -> None:
    assert load().parse(f"REC {CARD} ee {HORSE} 1200\n", "mare") == []


def test_every_menu_has_its_route_and_the_frame_its_handshake_ends() -> None:
    tool = load()

    kinds = [menu.kind for menu in tool.MENUS]

    assert kinds == ["racehorse", "mare", "stallion"]
    assert all(menu.steps.startswith(tool.NAME_ENTRY) for menu in tool.MENUS)


def test_each_session_starts_from_an_empty_save(tmp_path: Path) -> None:
    tool = load()

    command = tool.mame_command(tmp_path, tmp_path / "state", tmp_path / "save")

    assert command[:3] == ["mame", "gameboy", "famjock2"]
    assert command[command.index("-nvram_directory") + 1] == str(tmp_path / "save")
    assert command[command.index("-autoboot_script") + 1].endswith("barcode_boy.lua")


def test_the_session_reads_the_menu_and_the_bonus_beside_the_horse(tmp_path: Path) -> None:
    tool = load()

    env = tool.session_env(tmp_path / "codes.txt", tool.MENUS[1])

    assert env["PEEK_ADDRS"] == "0xaf36,0xd90c"
    assert env["BOOT_STEPS"] == tool.MENUS[1].steps
    assert env["READY_FRAME"] == tool.MENUS[1].ready


def test_the_fixture_names_the_rom_the_emulator_and_the_time() -> None:
    fixture = load().fixture([], "2026-09-30T18:00:00Z")

    assert fixture["software"] == "famjock2"
    assert fixture["rom"] == {"sha1": "d858fcdfce099435fa632859a9f8e8c82823bbcb", "size": 131072}
    assert fixture["recorded_utc"] == "2026-09-30T18:00:00Z"
