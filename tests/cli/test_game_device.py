"""Tests for the commands run against the Datach games after Dragon Ball Z."""

from pathlib import Path

from typer.testing import CliRunner

from maeyomi.barcode.verify import decode_pdf
from maeyomi.cli.main import app
from maeyomi.datach.jleague import decode_jleague
from maeyomi.datach.sdgundam import decode_sdgundam
from maeyomi.datach.ultraman import decode_ultraman
from maeyomi.datach.yuyu import decode_yuyu
from maeyomi.games.barcode_world import decode_barcode_world
from maeyomi.games.senki import decode_senki
from maeyomi.models.device import Device

runner = CliRunner()


def test_decode_reads_an_ultraman_club_fighter_with_its_three_numbers() -> None:
    result = runner.invoke(app, ["decode", "0315424322677", "--device", "ultraman"])

    assert result.exit_code == 0
    assert "Device    Datach Ultraman Club" in result.output
    assert "Kind      Fighter" in result.output
    assert "Name      Zoffy / ゾフィー" in result.output
    assert "PW        7200" in result.output
    assert "ST        6900" in result.output
    assert "SP        4800" in result.output


def test_decode_notes_a_code_that_reads_only_at_some_swipe_speeds() -> None:
    result = runner.invoke(app, ["decode", "0315424322677", "--device", "ultraman"])

    assert "Reads only at some swipe speeds" in result.output


def test_decode_refuses_a_bad_check_digit_on_a_game() -> None:
    result = runner.invoke(app, ["decode", "0315424322670", "--device", "ultraman"])

    assert result.exit_code == 1


def test_decode_prints_the_card_when_asked(tmp_path: Path) -> None:
    output = tmp_path / "zoffy.pdf"

    result = runner.invoke(
        app, ["decode", "0344046250372", "--device", "ultraman", "--output", str(output)]
    )

    assert result.exit_code == 0
    assert decode_pdf(output) == ["0344046250372"]


def test_generate_builds_an_ultraman_club_card_with_the_numbers_asked_for(tmp_path: Path) -> None:
    output = tmp_path / "card.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--device",
            "ultraman",
            "--character",
            "Zoffy",
            "--hp",
            "9900",
            "--st",
            "100",
            "--df",
            "5000",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    barcode = decode_pdf(output)[0]
    card = decode_ultraman(barcode)
    assert (card.ident, card.value("PW"), card.value("UST"), card.value("USP")) == (
        3,
        9900,
        100,
        5000,
    )


def test_generate_refuses_numbers_the_game_cannot_hold(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["generate", "--device", "ultraman", "--hp", "7250", "--output", str(tmp_path / "x.pdf")],
    )

    assert result.exit_code == 1
    assert "Datach Ultraman Club reads no card with those numbers" in result.output


def test_generate_refuses_the_dragon_ball_z_level_on_another_game(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["generate", "--device", "ultraman", "--level", "2", "--output", str(tmp_path / "x.pdf")],
    )

    assert result.exit_code == 2
    assert "only --device dbz reads --level" in result.output


def test_cheat_prints_a_card_at_the_top_of_all_three(tmp_path: Path) -> None:
    output = tmp_path / "cheat.pdf"

    result = runner.invoke(app, ["cheat", "--device", "ultraman", "--output", str(output)])

    assert result.exit_code == 0
    assert "PW 9900, ST 9900, SP 9900" in result.output
    card = decode_ultraman(decode_pdf(output)[0])
    assert (card.value("PW"), card.value("UST"), card.value("USP")) == (9900, 9900, 9900)


def test_generate_refuses_a_field_the_game_does_not_read(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["generate", "--device", "ultraman", "--race", "human", "-o", str(tmp_path / "x.pdf")],
    )

    assert result.exit_code == 2
    assert "Datach Ultraman Club does not read race" in result.output


def test_cheat_with_items_says_the_game_has_none_and_prints_the_card(tmp_path: Path) -> None:
    output = tmp_path / "cheat.pdf"

    result = runner.invoke(
        app, ["cheat", "--device", "ultraman", "--items", "--output", str(output)]
    )

    assert result.exit_code == 0
    assert "has no strongest items" in result.output
    assert len(decode_pdf(output)) == 1


def test_decode_reads_an_sd_gundam_unit_with_its_weapons() -> None:
    result = runner.invoke(app, ["decode", "0403775140252", "--device", "sdgundam"])

    assert result.exit_code == 0
    assert "Name      Gundam / ガンダム" in result.output
    assert "Kind      RX-78" in result.output
    assert "HP        3880" in result.output
    assert "CP        9" in result.output
    assert "SR Beam saber, LR Beam rifle" in result.output


def test_decode_reads_an_sd_gundam_command_with_its_cost() -> None:
    result = runner.invoke(app, ["decode", "0465464360068", "--device", "sdgundam"])

    assert result.exit_code == 0
    assert "Name      White Base / ホワイトベース" in result.output
    assert "Costs 7 CP." in result.output


def test_generate_builds_a_unit_with_the_weapons_picked(tmp_path: Path) -> None:
    output = tmp_path / "gundam.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--device",
            "sdgundam",
            "--character",
            "RX-78",
            "--pick",
            "sr=1",
            "--pick",
            "lr=5",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    card = decode_sdgundam(decode_pdf(output)[0])
    assert card.traits[:2] == (1, 5)


def test_generate_says_when_it_offers_the_closest_numbers(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "generate",
            "--device",
            "sdgundam",
            "--character",
            "Gundam",
            "--hp",
            "3885",
            "-o",
            str(tmp_path / "x.pdf"),
        ],
    )

    assert result.exit_code == 0
    assert "offering the closest one that prints" in result.output


def test_a_malformed_pick_is_refused(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["generate", "--device", "sdgundam", "--pick", "sr", "-o", str(tmp_path / "x.pdf")],
    )

    assert result.exit_code == 2
    assert "--pick takes key=value" in result.output


def test_a_pick_is_refused_on_a_machine(tmp_path: Path) -> None:
    result = runner.invoke(app, ["generate", "--pick", "sr=1", "-o", str(tmp_path / "x.pdf")])

    assert result.exit_code == 2
    assert "only a Datach game after Dragon Ball Z reads --pick" in result.output


def test_decode_reads_a_yu_yu_hakusho_fighter_with_its_techniques() -> None:
    result = runner.invoke(app, ["decode", "0871024742401", "--device", "yuyu"])

    assert result.exit_code == 0
    assert "Name      Yusuke / ゆうすけ" in result.output
    assert "HP        3000" in result.output
    assert "Spirit Shotgun, Super Spirit Gun" in result.output


def test_generate_builds_a_yu_yu_hakusho_item_at_its_top_level(tmp_path: Path) -> None:
    output = tmp_path / "botan.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--device",
            "yuyu",
            "--character",
            "Botan",
            "--pick",
            "level=3",
            "-o",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert decode_yuyu(decode_pdf(output)[0]).value("YHP") == 1000


def test_cheat_prints_the_hidden_toguro(tmp_path: Path) -> None:
    result = runner.invoke(app, ["cheat", "--device", "yuyu", "-o", str(tmp_path / "x.pdf")])

    assert result.exit_code == 0
    assert "SP Toguro, HP 9999, SP 9999" in result.output


def test_decode_reads_a_j_league_player_with_his_team() -> None:
    result = runner.invoke(app, ["decode", "1200520240125", "--device", "jleague"])

    assert result.exit_code == 0
    assert "Name      Masaaki Furukawa / 古川 昌明" in result.output
    assert "Kind      Kashima Antlers" in result.output


def test_generate_builds_a_j_league_team_card(tmp_path: Path) -> None:
    output = tmp_path / "team.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--device",
            "jleague",
            "--character",
            "Nagoya Grampus Eight",
            "-o",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert decode_jleague(decode_pdf(output)[0]).ident == 7 * 16


def test_cheat_says_a_j_league_card_has_nothing_to_raise(tmp_path: Path) -> None:
    result = runner.invoke(app, ["cheat", "--device", "jleague", "-o", str(tmp_path / "x.pdf")])

    assert result.exit_code == 1
    assert "carry no numbers" in result.output


def test_decode_reads_a_barcode_world_magician_with_its_numbers() -> None:
    result = runner.invoke(app, ["decode", "4994699095453", "--device", "barcodeworld"])

    assert result.exit_code == 0
    assert "Name      Magician / まほうつかい" in result.output
    assert "HP        49900" in result.output
    assert "DF        9900" in result.output
    assert "MP        10" in result.output
    assert "Reads only" not in result.output


def test_generate_builds_a_barcode_world_warrior_with_the_job_picked(tmp_path: Path) -> None:
    output = tmp_path / "warrior.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--device",
            "barcodeworld",
            "--character",
            "warrior",
            "--hp",
            "12300",
            "--pick",
            "job=3",
            "-o",
            str(output),
        ],
    )

    assert result.exit_code == 0
    card = decode_barcode_world(decode_pdf(output)[0])
    assert (card.value("WHP"), card.traits[0]) == (12300, 3)


def test_generate_prints_a_senki_magician_the_game_reads_back(tmp_path: Path) -> None:
    output = tmp_path / "magician.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--device",
            "senki",
            "--character",
            "magician",
            "--hp",
            "35900",
            "--st",
            "15000",
            "-o",
            str(output),
        ],
    )

    assert result.exit_code == 0
    card = decode_senki(decode_pdf(output)[0])
    assert (card.game, card.value("WHP"), card.value("WST"), card.value("WMP")) == (
        Device.SENKI,
        35900,
        15000,
        10,
    )
