"""Tests for the commands run against the Barcode Battler II Double."""

from pathlib import Path

from typer.testing import CliRunner

from maeyomi.barcode.verify import decode_pdf
from maeyomi.cli.main import app
from maeyomi.double.decode import decode_double

runner = CliRunner()


def test_decode_reads_a_seven_read_code() -> None:
    result = runner.invoke(app, ["decode", "7821818898978", "--device", "double"])

    assert result.exit_code == 0
    assert "Device    Barcode Battler 2 Double" in result.output
    assert "Read      7" in result.output
    assert "ST        18800" in result.output
    assert "Race      Bird" in result.output
    assert "Class     Magician" in result.output
    assert "Power     27 opponent DF down 80%" in result.output


def test_decode_refuses_a_bad_check_digit_on_the_double() -> None:
    result = runner.invoke(app, ["decode", "7821818898977", "--device", "double"])

    assert result.exit_code == 1


def test_decode_can_print_a_double_card(tmp_path: Path) -> None:
    output = tmp_path / "card.pdf"

    result = runner.invoke(
        app, ["decode", "7821818898978", "--device", "double", "--output", str(output)]
    )

    assert result.exit_code == 0
    assert decode_pdf(output) == ["7821818898978"]


def test_generate_builds_a_seven_read_card(tmp_path: Path) -> None:
    output = tmp_path / "double.pdf"

    result = runner.invoke(
        app,
        ["generate", "--device", "double", "--st", "99900", "--df", "99900", "-o", str(output)],
    )

    assert result.exit_code == 0
    card = decode_double(decode_pdf(output)[0])
    assert (card.st, card.df) == (99900, 99900)
    assert "ST       99900           99900" in result.output


def test_generate_builds_a_seven_read_card_of_the_race_asked_for(tmp_path: Path) -> None:
    output = tmp_path / "x.pdf"

    result = runner.invoke(
        app, ["generate", "--device", "double", "--race", "human", "-o", str(output)]
    )

    assert result.exit_code == 0
    assert output.exists()


def test_generate_refuses_an_item_race_on_a_seven_read_card(tmp_path: Path) -> None:
    output = tmp_path / "x.pdf"

    result = runner.invoke(
        app, ["generate", "--device", "double", "--race", "weapon", "-o", str(output)]
    )

    assert result.exit_code == 1
    assert "a 7-read card is always a fighter" in result.output
    assert not output.exists()


def test_generate_refuses_a_back_read_on_the_double(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["generate", "--device", "double", "--back-read", "-o", str(tmp_path / "x.pdf")]
    )

    assert result.exit_code == 2
    assert "--device bb2" in result.output


def test_cheat_prints_the_double_deck(tmp_path: Path) -> None:
    output = tmp_path / "deck.pdf"

    result = runner.invoke(app, ["cheat", "--device", "double", "--items", "-o", str(output)])

    assert result.exit_code == 0
    codes = decode_pdf(output)
    assert len(codes) == 6
    fighter = decode_double(codes[0])
    assert (fighter.hp, fighter.st, fighter.df) == (92900, 99900, 99900)
    assert "Cheat Herbs: PP 99; power 35 puts the opponent to sleep at the start" in result.output


def test_cheat_without_items_prints_the_fighter_alone(tmp_path: Path) -> None:
    output = tmp_path / "one.pdf"

    result = runner.invoke(app, ["cheat", "--device", "double", "-o", str(output)])

    assert result.exit_code == 0
    assert len(decode_pdf(output)) == 1
