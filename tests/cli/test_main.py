"""Tests for the command line interface."""

from pathlib import Path

import pytest
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


def test_serve_starts_the_local_interface(monkeypatch: pytest.MonkeyPatch) -> None:
    started: dict[str, object] = {}

    def fake_run(application: object, *, host: str, port: int) -> None:
        started["host"] = host
        started["port"] = port
        started["app"] = application

    monkeypatch.setattr("uvicorn.run", fake_run)

    result = runner.invoke(app, ["serve", "--host", "127.0.0.2", "--port", "8123"])

    assert result.exit_code == 0
    assert started["host"] == "127.0.0.2"
    assert started["port"] == 8123


def test_serve_explains_how_to_install_the_optional_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing() -> tuple[object, object]:
        message = "No module named 'uvicorn'"
        raise ImportError(message)

    monkeypatch.setattr("barcode_battler.cli.main._web_server", missing)

    result = runner.invoke(app, ["serve"])

    assert result.exit_code == 1
    assert "uv sync --extra ui" in result.output


def unreachable_args(output: Path) -> list[str]:
    return [
        "generate",
        "--hp",
        "20900",
        "--st",
        "11000",
        "--df",
        "10000",
        "--race",
        "mechanical",
        "--output",
        str(output),
    ]


def test_an_impossible_request_writes_nothing_without_the_nearest_flag(tmp_path: Path) -> None:
    output = tmp_path / "none.pdf"

    result = runner.invoke(app, unreachable_args(output))

    assert result.exit_code == 1
    assert not output.exists()


def test_the_nearest_flag_offers_the_closest_card(tmp_path: Path) -> None:
    output = tmp_path / "near.pdf"

    result = runner.invoke(app, [*unreachable_args(output), "--nearest"])

    assert result.exit_code == 0
    assert "closest card differs by" in result.output
    assert "differs" in result.output
    assert decode_pdf(output)


def test_the_nearest_flag_keeps_the_requested_race(tmp_path: Path) -> None:
    output = tmp_path / "near-race.pdf"

    runner.invoke(app, [*unreachable_args(output), "--nearest"])

    assert decode(decode_pdf(output)[0]).race.name.lower() == "mechanical"


def test_the_back_read_flag_produces_a_back_read_card(tmp_path: Path) -> None:
    output = tmp_path / "back.pdf"

    result = runner.invoke(
        app, ["generate", "--race", "human", "--back-read", "--output", str(output)]
    )

    assert result.exit_code == 0
    assert decode(decode_pdf(output)[0]).read_type.value == "back"


def test_the_nearest_flag_is_refused_alongside_a_back_read(tmp_path: Path) -> None:
    output = tmp_path / "both.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--hp",
            "99900",
            "--race",
            "human",
            "--back-read",
            "--nearest",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 1
    assert "front reads only" in result.output


def test_the_nearest_flag_reports_when_there_is_no_close_card_either(tmp_path: Path) -> None:
    output = tmp_path / "none.pdf"

    result = runner.invoke(
        app,
        [
            "generate",
            "--hp",
            "20000-20800",
            "--race",
            "human",
            "--nearest",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 1
    assert "window" in result.output
    assert not output.exists()


def test_cheat_writes_the_strongest_card_there_is(tmp_path: Path) -> None:
    output = tmp_path / "cheat.pdf"

    result = runner.invoke(app, ["cheat", "--output", str(output)])

    assert result.exit_code == 0
    character = decode(decode_pdf(output)[0])
    assert (character.hp, character.st, character.df) == (99900, 24500, 19900)


def test_cheat_takes_a_name(tmp_path: Path) -> None:
    output = tmp_path / "grandma.pdf"

    result = runner.invoke(app, ["cheat", "--name", "Grandma", "--output", str(output)])

    assert result.exit_code == 0
    assert "Grandma" in result.output


def test_official_lists_every_set_with_its_count() -> None:
    result = runner.invoke(app, ["official", "--list"])

    assert result.exit_code == 0
    assert "Barcode Battler II board game" in result.output
    assert "572" in result.output


def test_official_names_the_transcriptions_it_rejected() -> None:
    result = runner.invoke(app, ["official", "--list"])

    assert "1162864348006" in result.output


def test_official_prints_one_set(tmp_path: Path) -> None:
    output = tmp_path / "candy.pdf"

    result = runner.invoke(app, ["official", "--set", "candy", "--output", str(output)])

    assert result.exit_code == 0
    assert len(decode_pdf(output)) == 10


def test_official_rejects_a_set_it_does_not_know(tmp_path: Path) -> None:
    result = runner.invoke(app, ["official", "--set", "nope", "--output", str(tmp_path / "x.pdf")])

    assert result.exit_code == 2
    assert "candy" in result.output


def test_official_needs_an_output_unless_listing() -> None:
    result = runner.invoke(app, ["official"])

    assert result.exit_code == 2
