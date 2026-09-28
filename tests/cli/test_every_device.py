"""Tests that every command honours --device, rather than quietly reading as the II."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from maeyomi.barcode.verify import decode_pdf
from maeyomi.bb1.decode import decode_first
from maeyomi.cli.main import app
from maeyomi.datach.dbz import DbzKind, decode_dbz

runner = CliRunner()


def test_random_draws_a_dragon_ball_sheet(tmp_path: Path) -> None:
    output = tmp_path / "dbz.pdf"
    ranges = ["--hp", "10000-60000", "--bp", "5000-30000", "--dp", "5000-30000"]

    result = runner.invoke(
        app, ["random", "--device", "dbz", "-n", "3", "--seed", "2", *ranges, "-o", str(output)]
    )

    assert result.exit_code == 0
    codes = decode_pdf(output)
    assert len(codes) == 3
    assert all(decode_dbz(code).kind is not DbzKind.ITEM for code in codes)


def test_random_draws_a_first_barcode_battler_sheet(tmp_path: Path) -> None:
    output = tmp_path / "bb1.pdf"

    result = runner.invoke(
        app, ["random", "--device", "bb1", "-n", "2", "--hp", "1000-9000", "-o", str(output)]
    )

    assert result.exit_code == 0
    assert all(1000 <= decode_first(code).hp <= 9000 for code in decode_pdf(output))


def test_random_names_a_field_the_game_cannot_read(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["random", "--device", "dbz", "--race", "human", "-o", str(tmp_path / "x.pdf")]
    )

    assert result.exit_code == 1
    assert "Datach Dragon Ball Z does not read race" in result.output


def test_products_lists_what_each_product_becomes_in_dragon_ball() -> None:
    result = runner.invoke(app, ["products", "--device", "dbz", "--search", "4901"])

    assert result.exit_code == 0
    assert "BP " in result.output
    assert "Robot" not in result.output


def test_products_prints_a_dragon_ball_sheet(tmp_path: Path) -> None:
    output = tmp_path / "shop.pdf"

    result = runner.invoke(
        app, ["products", "--device", "dbz", "-n", "2", "--seed", "1", "-o", str(output)]
    )

    assert result.exit_code == 0
    assert len(decode_pdf(output)) == 2
    assert "never read by a physical Datach" in result.output


def test_kinds_lists_the_dragon_ball_fighters_and_items() -> None:
    result = runner.invoke(app, ["kinds", "--device", "dbz"])

    assert result.exit_code == 0
    assert "Goku / ゴクウ" in result.output
    assert "Senzu bean / せんず" in result.output


@pytest.mark.parametrize("device", ["bb1", "double"])
def test_kinds_lists_the_races_a_battler_reads(device: str) -> None:
    result = runner.invoke(app, ["kinds", "--device", device])

    assert result.exit_code == 0
    assert "Robot / ロボット" in result.output


@pytest.mark.parametrize(
    ("device", "expected"),
    [
        ("bb1", "18  Hero"),
        ("double", "27  opponent DF down 80%"),
        ("dbz", "33  Senzu bean: Fully restores HP, BP and DP"),
    ],
)
def test_abilities_prints_the_chosen_devices_table(device: str, expected: str) -> None:
    result = runner.invoke(app, ["abilities", "--device", device])

    assert result.exit_code == 0
    assert expected in result.output


def test_official_lists_only_the_chosen_devices_sets() -> None:
    result = runner.invoke(app, ["official", "--list", "--device", "dbz"])

    assert result.exit_code == 0
    assert "datach_dbz" in result.output
    assert "candy" not in result.output
    assert "36  total printable" in result.output


def test_official_prints_every_card_of_the_chosen_device(tmp_path: Path) -> None:
    output = tmp_path / "double.pdf"

    result = runner.invoke(app, ["official", "--device", "double", "-o", str(output)])

    assert result.exit_code == 0
    assert len(decode_pdf(output)) == 56


def test_official_refuses_a_device_nobody_published_a_card_list_for(tmp_path: Path) -> None:
    output = tmp_path / "senki.pdf"

    result = runner.invoke(app, ["official", "--device", "senki", "-o", str(output)])

    assert result.exit_code == 2
    assert "no published card list for Barcode Battler Senki" in result.output
    assert not output.exists()
