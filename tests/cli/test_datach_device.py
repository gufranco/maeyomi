"""Tests for the commands run against Datach Dragon Ball Z."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from maeyomi.barcode.verify import decode_pdf
from maeyomi.cli.datach_device import describe_dbz
from maeyomi.cli.main import app
from maeyomi.datach.dbz import DbzCard, DbzKind, decode_dbz

runner = CliRunner()


def test_decode_reads_a_fighter() -> None:
    result = runner.invoke(app, ["decode", "0022248300117", "--device", "dbz"])

    assert result.exit_code == 0
    assert "Device    Datach Dragon Ball Z" in result.output
    assert "Kind      fighter" in result.output
    assert "Name      Goku / ゴクウ" in result.output
    assert "Level     1" in result.output
    assert "HP        49500" in result.output
    assert "BP        28250" in result.output
    assert "DP        22750" in result.output


def test_decode_reads_an_item_with_its_effect() -> None:
    result = runner.invoke(app, ["decode", "0120631203219", "--device", "dbz"])

    assert result.exit_code == 0
    assert "Name      Korin / カリンさま" in result.output
    assert "Effect    Adds 6000 to HP, BP and DP" in result.output
    assert "HP " not in result.output


def test_decode_refuses_a_bad_check_digit_on_dbz() -> None:
    result = runner.invoke(app, ["decode", "0022248300118", "--device", "dbz"])

    assert result.exit_code == 1


def test_decode_can_print_a_dbz_card(tmp_path: Path) -> None:
    output = tmp_path / "card.pdf"

    result = runner.invoke(
        app, ["decode", "0022248300117", "--device", "dbz", "--output", str(output)]
    )

    assert result.exit_code == 0
    assert decode_pdf(output) == ["0022248300117"]
    assert "never read by a physical Datach" in result.output


def test_generate_builds_a_fighter_by_name(tmp_path: Path) -> None:
    output = tmp_path / "dbz.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--device",
            "dbz",
            "--character",
            "vegeta",
            "--level",
            "2",
            "--hp",
            "40000",
            "--bp",
            ">=20000",
            "-o",
            str(output),
        ],
    )

    assert result.exit_code == 0
    card = decode_dbz(decode_pdf(output)[0])
    assert (card.character, card.level, card.hp) == (7, 2, 40000)
    assert card.bp >= 20000
    assert "HP       40000           40000" in result.output


def test_generate_builds_an_item_by_id(tmp_path: Path) -> None:
    output = tmp_path / "item.pdf"

    result = runner.invoke(
        app, ["generate", "--device", "dbz", "--character", "33", "-o", str(output)]
    )

    assert result.exit_code == 0
    card = decode_dbz(decode_pdf(output)[0])
    assert (card.kind, card.character) == (DbzKind.ITEM, 33)


def test_generate_reports_why_a_dbz_request_is_impossible(tmp_path: Path) -> None:
    output = tmp_path / "x.pdf"

    result = runner.invoke(app, ["generate", "--device", "dbz", "--hp", "99600", "-o", str(output)])

    assert result.exit_code == 1
    assert "hp of 99600 is above 99500" in result.output
    assert not output.exists()


def test_generate_refuses_an_unknown_character(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["generate", "--device", "dbz", "--character", "Mr. Satan", "-o", str(tmp_path / "x.pdf")],
    )

    assert result.exit_code == 2
    assert "unknown character 'Mr. Satan'" in result.output


@pytest.mark.parametrize(
    "options",
    [["--race", "human"], ["--job", "3"], ["--back-read"], ["--herbs", "5"], ["--ability", "4"]],
    ids=["race", "job", "back-read", "herbs", "ability"],
)
def test_generate_refuses_a_field_dbz_does_not_read(tmp_path: Path, options: list[str]) -> None:
    result = runner.invoke(
        app, ["generate", "--device", "dbz", *options, "-o", str(tmp_path / "x.pdf")]
    )

    assert result.exit_code == 2
    assert "Datach Dragon Ball Z does not read" in result.output


@pytest.mark.parametrize("options", [["--character", "goku"], ["--level", "1"]])
def test_generate_refuses_dbz_options_on_another_device(tmp_path: Path, options: list[str]) -> None:
    result = runner.invoke(app, ["generate", *options, "-o", str(tmp_path / "x.pdf")])

    assert result.exit_code == 2
    assert "only --device dbz reads" in result.output


def test_cheat_prints_the_strongest_dbz_fighter_and_items(tmp_path: Path) -> None:
    output = tmp_path / "deck.pdf"

    result = runner.invoke(app, ["cheat", "--device", "dbz", "--items", "-o", str(output)])

    assert result.exit_code == 0
    codes = decode_pdf(output)
    fighter = decode_dbz(codes[0])
    assert (fighter.character, fighter.hp) == (9, 99500)
    assert [decode_dbz(code).character for code in codes[1:]] == [33, 35, 39, 43, 45, 71]
    assert (
        "Maximus Cheatimus: Super Saiyan Goku, level 3, HP 99500, BP 48250, DP 33250"
        in result.output
    )
    assert "Senzu bean: Fully restores HP, BP and DP" in result.output


def test_cheat_without_items_prints_the_dbz_fighter_alone(tmp_path: Path) -> None:
    output = tmp_path / "one.pdf"

    result = runner.invoke(app, ["cheat", "--device", "dbz", "-o", str(output)])

    assert result.exit_code == 0
    assert len(decode_pdf(output)) == 1


def test_an_id_the_game_never_produces_is_described_as_unknown() -> None:
    fighter = describe_dbz(DbzCard("0000000000000", DbzKind.FIGHTER, 14, None, 100, 100, 100))
    item = describe_dbz(DbzCard("0000000000000", DbzKind.ITEM, 60, None))

    assert "Name      unknown 14" in fighter
    assert "Level     none" in fighter
    assert "Effect    unknown" in item
