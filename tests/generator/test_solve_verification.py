"""Tests for the check that stands between a candidate and a card."""

from maeyomi.decoder.decode import decode
from maeyomi.generator.solve import Mismatch, mismatches, solve, verify
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race


def test_a_candidate_that_satisfies_the_request_is_accepted() -> None:
    request = CardRequest(hp=Constraint.exactly(4000), race=Race.AQUATIC)

    assert verify(request, "0401207237501") is not None


def test_a_candidate_with_the_wrong_hit_points_is_rejected() -> None:
    request = CardRequest(hp=Constraint.exactly(9999900), race=Race.AQUATIC)

    assert verify(request, "0401207237501") is None


def test_a_candidate_that_cannot_be_decoded_is_rejected() -> None:
    request = CardRequest(hp=Constraint.exactly(4000))

    assert verify(request, "0401207237509") is None


def test_a_candidate_resting_on_an_unresolved_branch_is_rejected() -> None:
    request = CardRequest(hp=Constraint.exactly(20900))

    assert verify(request, "2099300045000") is None


def test_a_stat_mismatch_names_the_field_and_both_values() -> None:
    request = CardRequest(st=Constraint.exactly(9900), race=Race.AQUATIC)

    found = mismatches(request, _decoded())

    assert found == (Mismatch("st", "9900", "1200"),)


def test_a_range_mismatch_renders_the_range() -> None:
    request = CardRequest(df=Constraint.between(1000, 2000))

    found = mismatches(request, _decoded())

    assert str(found[0]) == "df: requested 1000 to 2000, produced 700"


def test_a_categorical_mismatch_is_reported() -> None:
    request = CardRequest(race=Race.HUMAN, job=9, character_class=CharacterClass.MAGICIAN)

    names = {mismatch.field_name for mismatch in mismatches(request, _decoded())}

    assert names == {"race", "job", "character_class"}


def test_a_matching_request_reports_no_mismatch() -> None:
    request = CardRequest(
        hp=Constraint.exactly(4000),
        st=Constraint.exactly(1200),
        df=Constraint.exactly(700),
        race=Race.AQUATIC,
        job=3,
        speed=7,
        special=50,
    )

    assert mismatches(request, _decoded()) == ()


def test_a_solved_outcome_reports_itself_as_solved() -> None:
    outcome = solve(CardRequest(hp=Constraint.exactly(4000), race=Race.HUMAN))

    assert outcome.solved


def test_an_unsolved_outcome_reports_itself_as_unsolved() -> None:
    outcome = solve(CardRequest(hp=Constraint.exactly(4050)))

    assert not outcome.solved


def _decoded() -> BarcodeBattlerCharacter:
    return decode("0401207237501")
