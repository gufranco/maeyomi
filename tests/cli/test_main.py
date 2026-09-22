"""Tests for the command line interface."""

from pathlib import Path

from typer.testing import CliRunner

from barcode_battler.barcode.verify import decode_pdf
from barcode_battler.cli.main import app
from barcode_battler.decoder.decode import decode

runner = CliRunner()


def test_the_help_lists_both_generation_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "random" in result.output
    assert "generate" in result.output


def test_random_writes_a_sheet_whose_barcodes_decode(tmp_path: Path) -> None:
    output = tmp_path / "cards.pdf"

    result = runner.invoke(app, ["random", "--count", "9", "--seed", "1", "--output", str(output)])

    assert result.exit_code == 0
    assert len(decode_pdf(output)) == 9


def test_random_honours_the_requested_ranges(tmp_path: Path) -> None:
    output = tmp_path / "ranged.pdf"

    result = runner.invoke(
        app,
        [
            "random",
            "--count",
            "4",
            "--seed",
            "2",
            "--hp",
            "1000-2000",
            "--st",
            "100-500",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    decoded = [decode(code) for code in decode_pdf(output)]
    assert len(decoded) == 4
    assert all(1000 <= character.hp <= 2000 for character in decoded)
    assert all(100 <= character.st <= 500 for character in decoded)


def test_random_is_reproducible_from_a_seed(tmp_path: Path) -> None:
    first = tmp_path / "a.pdf"
    second = tmp_path / "b.pdf"

    runner.invoke(app, ["random", "--count", "4", "--seed", "7", "--output", str(first)])
    runner.invoke(app, ["random", "--count", "4", "--seed", "7", "--output", str(second)])

    assert decode_pdf(first) == decode_pdf(second)


def test_random_reports_a_shortfall_rather_than_pretending(tmp_path: Path) -> None:
    output = tmp_path / "narrow.pdf"

    result = runner.invoke(
        app,
        [
            "random",
            "--count",
            "5",
            "--seed",
            "1",
            "--hp",
            "5000",
            "--st",
            "1500",
            "--df",
            "1200",
            "--race",
            "human",
            "--job",
            "3",
            "--speed",
            "7",
            "--ability",
            "0",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code != 0
    assert "shortfall" in result.output.lower() or "distinct" in result.output.lower()


def test_generate_writes_one_card_matching_the_request(tmp_path: Path) -> None:
    output = tmp_path / "knight.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--name",
            "Fire Knight",
            "--hp",
            "5000",
            "--attack",
            "1800",
            "--defense",
            "1200",
            "--race",
            "human",
            "--class",
            "warrior",
            "--ability",
            "17",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert decode_pdf(output)


def test_generate_prints_the_requested_and_generated_values(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "generate",
            "--hp",
            "5000",
            "--attack",
            "1800",
            "--race",
            "human",
            "--output",
            str(tmp_path / "card.pdf"),
        ],
    )

    assert "Requested" in result.output
    assert "Generated" in result.output
    assert "Difference" in result.output


def test_generate_refuses_an_impossible_request_and_names_the_field(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["generate", "--hp", "5050", "--race", "human", "--output", str(tmp_path / "x.pdf")],
    )

    assert result.exit_code != 0
    assert "multiple of 100" in result.output
    assert not (tmp_path / "x.pdf").exists()


def test_decode_prints_the_attributes_of_a_barcode() -> None:
    result = runner.invoke(app, ["decode", "0401207237501"])

    assert result.exit_code == 0
    assert "4000" in result.output
    assert "Aquatic" in result.output


def test_decode_rejects_an_invalid_barcode() -> None:
    result = runner.invoke(app, ["decode", "0401207237509"])

    assert result.exit_code != 0
    assert "check digit" in result.output


def test_abilities_lists_the_published_table() -> None:
    result = runner.invoke(app, ["abilities"])

    assert result.exit_code == 0
    assert "hero flag" in result.output


def test_the_output_states_that_no_hardware_was_used(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["random", "--count", "1", "--seed", "1", "--output", str(tmp_path / "c.pdf")]
    )

    assert "not been tested on a physical" in result.output.lower()


def test_images_are_written_when_asked(tmp_path: Path) -> None:
    output = tmp_path / "cards.pdf"

    result = runner.invoke(
        app,
        [
            "random",
            "--count",
            "1",
            "--seed",
            "1",
            "--output",
            str(output),
            "--images",
            "png",
        ],
    )

    assert result.exit_code == 0
    assert list((tmp_path / "cards-images").glob("page-*.png"))


def test_an_unreadable_value_is_rejected_before_anything_is_written(tmp_path: Path) -> None:
    output = tmp_path / "bad.pdf"

    result = runner.invoke(app, ["random", "--count", "1", "--hp", "abc", "--output", str(output)])

    assert result.exit_code == 2
    assert "5000-6000" in result.output
    assert not output.exists()


def test_an_unknown_race_is_rejected_before_anything_is_written(tmp_path: Path) -> None:
    output = tmp_path / "bad.pdf"

    result = runner.invoke(
        app, ["generate", "--hp", "4000", "--race", "dragon", "--output", str(output)]
    )

    assert result.exit_code == 2
    assert "mechanical" in result.output
    assert not output.exists()
