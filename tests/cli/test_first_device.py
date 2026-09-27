"""Tests for the commands run against the first Barcode Battler."""

from pathlib import Path

from typer.testing import CliRunner

from maeyomi.barcode.verify import decode_pdf
from maeyomi.bb1.decode import decode_first
from maeyomi.cli.main import app

runner = CliRunner()


def test_decode_reads_a_code_with_the_first_device_flag_table() -> None:
    result = runner.invoke(app, ["decode", "0120401154185", "--device", "bb1"])

    assert result.exit_code == 0
    assert "Device    Barcode Battler" in result.output
    assert "Flag      18 Hero" in result.output
    assert "HP        1200" in result.output
    assert "DX        4" in result.output


def test_decode_says_an_enemy_race_and_dx_are_unknown() -> None:
    result = runner.invoke(app, ["decode", "4902102072618", "--device", "bb1"])

    assert result.exit_code == 0
    assert "Race      unknown" in result.output
    assert "DX        unknown" in result.output


def test_decode_refuses_a_bad_check_digit_on_the_first_device() -> None:
    result = runner.invoke(app, ["decode", "0120401154184", "--device", "bb1"])

    assert result.exit_code == 1
    assert "check digit" in result.output


def test_decode_can_print_the_card(tmp_path: Path) -> None:
    output = tmp_path / "card.pdf"

    result = runner.invoke(
        app, ["decode", "0120401154185", "--device", "bb1", "--output", str(output)]
    )

    assert result.exit_code == 0
    assert decode_pdf(output) == ["0120401154185"]


def test_generate_builds_a_first_device_card_and_shows_the_comparison(tmp_path: Path) -> None:
    output = tmp_path / "bb1.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--device",
            "bb1",
            "--hp",
            "19900",
            "--st",
            "9900",
            "--df",
            "9900",
            "--race",
            "human",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    card = decode_first(decode_pdf(output)[0])
    assert (card.hp, card.st, card.df) == (19900, 9900, 9900)
    assert "HP       19900           19900" in result.output


def test_generate_refuses_what_the_first_device_cannot_hold(tmp_path: Path) -> None:
    output = tmp_path / "x.pdf"

    result = runner.invoke(
        app, ["generate", "--device", "bb1", "--hp", "25000", "--output", str(output)]
    )

    assert result.exit_code == 1
    assert "hp of 25000 is above the ceiling of 19900" in result.output
    assert not output.exists()


def test_generate_builds_an_enemy_read_from_the_back(tmp_path: Path) -> None:
    output = tmp_path / "enemy.pdf"

    result = runner.invoke(
        app,
        ["generate", "--device", "bb1", "--back-read", "--hp", "8000", "--output", str(output)],
    )

    assert result.exit_code == 0
    assert decode_first(decode_pdf(output)[0]).hp == 8000


def test_cheat_with_items_prints_the_first_device_deck(tmp_path: Path) -> None:
    output = tmp_path / "deck.pdf"

    result = runner.invoke(app, ["cheat", "--device", "bb1", "--items", "--output", str(output)])

    assert result.exit_code == 0
    codes = decode_pdf(output)
    assert len(codes) == 4
    fighter = decode_first(codes[0])
    assert (fighter.hp, fighter.st, fighter.df) == (19900, 9900, 9900)
    assert "Cheat Blade: ST 9900; flag 13 Reduce opponent DF to 0" in result.output


def test_cheat_without_items_prints_the_fighter_alone(tmp_path: Path) -> None:
    output = tmp_path / "one.pdf"

    result = runner.invoke(app, ["cheat", "--device", "bb1", "--output", str(output)])

    assert result.exit_code == 0
    assert len(decode_pdf(output)) == 1


def test_official_list_names_the_device_each_list_is_read_by() -> None:
    result = runner.invoke(app, ["official", "--list"])

    assert result.exit_code == 0
    line = next(line for line in result.output.splitlines() if " original " in f" {line} ")
    assert line.rstrip().endswith("read by the Barcode Battler")
    assert "read by the Barcode Battler 2" in result.output
