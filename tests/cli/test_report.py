"""Tests for the requested against generated comparison."""

from maeyomi.cli.report import DISCLAIMER, DISCLAIMER_JA, comparison_lines, shortfall_lines
from maeyomi.decoder.decode import decode
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race

CHARACTER = decode("0401207237501")


def test_the_three_columns_are_always_shown() -> None:
    lines = comparison_lines(CardRequest(), CHARACTER)

    assert "Requested" in lines[0]
    assert "Generated" in lines[0]
    assert "Difference" in lines[0]


def test_every_attribute_has_a_row() -> None:
    lines = comparison_lines(CardRequest(), CHARACTER)

    for field in ("HP", "ST", "DF", "Race", "Job", "Class", "Speed", "Ability"):
        assert any(line.startswith(field) for line in lines)


def test_a_matching_request_shows_no_difference() -> None:
    request = CardRequest(
        hp=Constraint.exactly(4000),
        st=Constraint.exactly(1200),
        df=Constraint.exactly(700),
        race=Race.AQUATIC,
        job=3,
        character_class=CharacterClass.WARRIOR,
        speed=7,
        special=50,
    )

    lines = comparison_lines(request, CHARACTER)

    assert not any("differs" in line for line in lines)


def test_a_differing_value_is_marked() -> None:
    request = CardRequest(hp=Constraint.exactly(9900))

    lines = comparison_lines(request, CHARACTER)

    assert any(line.startswith("HP") and "differs" in line for line in lines)


def test_an_unconstrained_field_is_never_marked_as_differing() -> None:
    lines = comparison_lines(CardRequest(), CHARACTER)

    assert not any("differs" in line for line in lines)


def test_a_shortfall_is_explained() -> None:
    lines = shortfall_lines(1, 5, "too few distinct barcodes")

    assert "1 of 5" in lines[0]
    assert "distinct" in lines[1]


def test_the_disclaimer_names_both_checks() -> None:
    assert "decoder" in DISCLAIMER
    assert "read on a physical Barcode Battler II" in DISCLAIMER


def test_the_lowest_valued_race_is_reported_rather_than_read_as_absent() -> None:
    request = CardRequest(race=Race.MECHANICAL)

    lines = comparison_lines(request, CHARACTER)

    assert any(line.startswith("Race") and "mechanical" in line for line in lines)


def test_the_disclaimer_exists_in_japanese() -> None:

    assert "実機" in DISCLAIMER_JA
