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


def test_an_sd_gundam_read_counts_a_command_as_accepted() -> None:
    tool = load()
    output = "PEEK 0460 00 00 00 00 00 00 00 00 00 00 00\nPEEK 061c 12\n"

    entry = tool.record(tool.GAMES["sdgundam"], ["0465464360068"], output)

    assert entry["accepted"] is True


def test_the_sd_gundam_fixture_was_recorded_with_the_rom_the_manifest_names() -> None:
    manifest = json.loads((ROOT / "artifacts.manifest.json").read_text())
    entry = next(item for item in manifest["artifacts"] if item["id"] == "datach_sdgundam_prg")
    fixture = json.loads(
        (ROOT / "tests" / "fixtures" / "oracle" / "datach_sdgundam.json").read_text()
    )

    assert entry["sha1"] == fixture["rom"]["sha1"]


def test_the_yu_yu_hakusho_fixture_was_recorded_with_the_rom_the_manifest_names() -> None:
    manifest = json.loads((ROOT / "artifacts.manifest.json").read_text())
    entry = next(item for item in manifest["artifacts"] if item["id"] == "datach_yuyu_prg")
    fixture = json.loads((ROOT / "tests" / "fixtures" / "oracle" / "datach_yuyu.json").read_text())

    assert entry["sha1"] == fixture["rom"]["sha1"]


def test_the_j_league_fixture_was_recorded_with_the_rom_the_manifest_names() -> None:
    manifest = json.loads((ROOT / "artifacts.manifest.json").read_text())
    entry = next(item for item in manifest["artifacts"] if item["id"] == "datach_jleague_prg")
    fixture = json.loads(
        (ROOT / "tests" / "fixtures" / "oracle" / "datach_jleague.json").read_text()
    )

    assert entry["sha1"] == fixture["rom"]["sha1"]


def test_barcode_world_runs_as_a_famicom_with_the_barcode_battler_attached() -> None:
    tool = load()

    command = tool.mame_command(ROOT, tool.GAMES["barcodeworld"])

    assert command[1:6] == ["famicom", "-exp", "barcode_battler", "-cart", "barcodew"]


def test_the_barcode_world_fixture_was_recorded_with_the_rom_the_manifest_names() -> None:
    manifest = json.loads((ROOT / "artifacts.manifest.json").read_text())
    entry = next(item for item in manifest["artifacts"] if item["id"] == "barcode_world_prg")
    fixture = json.loads(
        (ROOT / "tests" / "fixtures" / "oracle" / "barcode_world.json").read_text()
    )

    assert entry["sha1"] == fixture["rom"]["sha1"]


def test_senki_runs_as_a_super_famicom_with_the_barcode_battler_on_the_second_port() -> None:
    tool = load()

    command = tool.mame_command(ROOT, tool.GAMES["senki"])

    assert command[1:6] == ["snes", "-ctrl2", "barcode_battler", "-cart", "conveni"]


def test_senki_is_sent_its_code_through_the_interface_the_drive_script_emulates() -> None:
    tool = load()

    lines = tool.plan_lines(tool.GAMES["senki"], ["4994699095453"])

    assert "2100 bbscan 4994699095453" in lines


def test_every_rom_a_game_needs_beside_its_own_is_in_the_manifest() -> None:
    tool = load()
    manifest = json.loads((ROOT / "artifacts.manifest.json").read_text())
    ids = {entry["id"] for entry in manifest["artifacts"]}

    assert {extra for game in tool.GAMES.values() for extra in game.extras} <= ids
    assert tool.GAMES["senki"].extras == ("snes_spc700_ipl",)


def test_a_missing_boot_rom_is_named_before_mame_runs(tmp_path: Path) -> None:
    tool = load()
    manifest = json.loads((ROOT / "artifacts.manifest.json").read_text())
    entry = next(item for item in manifest["artifacts"] if item["id"] == "senki_rom")
    rom = tmp_path / str(entry["path"])
    rom.parent.mkdir(parents=True)
    rom.write_bytes(b"x")

    with pytest.raises(SystemExit, match="no ROM at"):
        tool.verify_extras(tmp_path, tool.GAMES["senki"])


def test_the_senki_fixture_was_recorded_with_the_rom_the_manifest_names() -> None:
    manifest = json.loads((ROOT / "artifacts.manifest.json").read_text())
    entry = next(item for item in manifest["artifacts"] if item["id"] == "senki_rom")
    fixture = json.loads(
        (ROOT / "tests" / "fixtures" / "oracle" / "barcode_battler_senki.json").read_text()
    )

    assert entry["sha1"] == fixture["rom"]["sha1"]


@pytest.mark.parametrize(
    ("game", "software"),
    [("lupin", "lupin3"), ("donald", "donaldd"), ("spiderman", "spidfoes"), ("alice", "alicepnt")],
)
def test_each_password_screen_game_runs_as_its_software_list_set(game: str, software: str) -> None:
    tool = load()

    command = tool.mame_command(ROOT, tool.GAMES[game])

    assert command[1:6] == ["snes", "-ctrl2", "barcode_battler", "-cart", software]


def test_a_caught_write_is_planned_before_the_code_arrives() -> None:
    tool = load()

    lines = tool.plan_lines(tool.GAMES["lupin"], ["4914177063576"])

    assert lines.index("1140 catch 05b3") < lines.index("1150 bbscan 4914177063576")


def test_a_caught_byte_is_recorded_beside_the_peeks() -> None:
    tool = load()
    output = "CATCH 05b3 0a\nCATCH 05b3 00\nPEEK 05b9 08 04 01 09 03 08 09 09 01 06 09 09 04\n"

    entry = tool.record(tool.GAMES["lupin"], ["4999619839148"], output)

    assert (entry["catch 05b3"], entry["accepted"]) == ("0a", True)


def test_a_code_the_matcher_never_wrote_for_is_recorded_as_unmatched() -> None:
    tool = load()
    output = "PEEK 05b9 04 00 09 08 07 06 05 04 03 02 01 09 04\n"

    entry = tool.record(tool.GAMES["lupin"], ["4912345678904"], output)

    assert entry["catch 05b3"] is None


@pytest.mark.parametrize(
    ("screen", "software"),
    [
        ("doraemon2", "doraemn2"),
        ("doraemon2_menu", "doraemn2"),
        ("doraemon3", "doraemn3"),
        ("doraemon3_menu", "doraemn3"),
    ],
)
def test_each_doraemon_screen_runs_as_its_games_set(screen: str, software: str) -> None:
    tool = load()

    command = tool.mame_command(ROOT, tool.GAMES[screen])

    assert command[1:6] == ["snes", "-ctrl2", "barcode_battler", "-cart", software]


def test_a_screen_deep_in_a_game_gets_a_session_long_enough_to_reach_it() -> None:
    tool = load()
    game = tool.GAMES["yousei_menu"]

    command = tool.mame_command(ROOT, game)

    seconds = int(command[command.index("-seconds_to_run") + 1])
    assert seconds * 60 > game.scan_frame + game.read_delay


@pytest.mark.parametrize("screen", ["yousei", "yousei_menu"])
def test_yousei_is_loaded_from_its_file_since_its_list_entry_names_no_rom_mapping(
    screen: str,
) -> None:
    tool = load()

    command = tool.mame_command(ROOT, tool.GAMES[screen])

    cart = command[command.index("-cart") + 1]
    assert cart == str(ROOT.resolve() / "snes" / "doraemon" / "shvc-dr-1.u1")


def test_excite_stage_95_opens_its_barcode_screen_before_an_open_match() -> None:
    tool = load()

    lines = tool.plan_lines(tool.GAMES["excite95"], ["4964262129977"])

    assert lines[:3] == ["700 press Start", "1000 press Start", "1300 press Start"]
    assert "2250 bbscan 4964262129977" in lines
    assert tool.GAMES["excite95"].extras == ("snes_spc700_ipl", "excite95_p1")


def test_a_game_read_by_its_branches_runs_under_the_debugger_with_each_breakpoint_set() -> None:
    tool = load()
    game = tool.GAMES["dslayer2"]

    command = tool.mame_command(ROOT, game)
    lines = tool.plan_lines(game, ["4900000040104"])

    assert command[command.index("-debug") + 1 : command.index("-debug") + 3] == [
        "-debugger",
        "none",
    ]
    assert "10 bp c1e5a9 ENDING" in lines


def test_the_branches_a_code_took_are_recorded_in_order() -> None:
    tool = load()
    output = "HIT BOOST 0f\nHIT EXIT ff\nPEEK 0b57 0f\n"

    entry = tool.record(tool.GAMES["dslayer2"], ["4900000040104"], output)

    assert entry["hits"] == ["BOOST 0f", "EXIT ff"]


def test_hatayama_is_read_on_its_battle_baseball_board_battler_screen() -> None:
    tool = load()

    lines = tool.plan_lines(tool.GAMES["hatayama"], ["9999999295997"])

    assert "1900 bbscan 9999999295997" in lines
    assert "1990 peek 7eff69 20" in lines


def test_every_write_to_a_caught_address_is_kept_in_order() -> None:
    tool = load()
    output = (
        "CATCH 08ca 02\nCATCH 08ca 10\nCATCH 08ca 00\n"
        "PEEK 03d3 04 02 06 02 03 06 02 05 04 09 07 04 00\n"
    )

    entry = tool.record(tool.GAMES["doraemon3_menu"], ["4794052362624"], output)

    assert (entry["catch 08ca"], entry["writes 08ca"]) == ("02", ["02", "10", "00"])


def test_battle_rush_scans_a_robots_two_cards_one_after_the_other() -> None:
    tool = load()

    lines = tool.plan_lines(tool.GAMES["battlerush"], ["0021495637396", "0021474877439"])

    assert "3100 scan 0021495637396" in lines
    assert "3400 scan 0021474877439" in lines
    assert "1100 poke 05a2 02" in lines
    assert "4300 peek 0348 48" in lines


def test_a_paired_read_records_both_cards() -> None:
    tool = load()
    output = "PEEK 0348 " + " ".join(["00"] * 48) + "\n"

    entry = tool.record(tool.GAMES["battlerush"], ["0021495637396", "0021474877439"], output)

    assert (entry["barcode"], entry["second"]) == ("0021495637396", "0021474877439")
