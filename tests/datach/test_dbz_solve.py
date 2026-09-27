"""Tests for building a Datach Dragon Ball Z barcode to order."""

import pytest

from maeyomi.datach.dbz import DbzKind, decode_dbz
from maeyomi.datach.dbz_solve import (
    NEAR_WIDTHS,
    DbzRequest,
    digits_for,
    request_from,
    solve_dbz,
    solve_dbz_nearest,
    strongest_dbz,
    unread_fields,
)
from maeyomi.datach.dbz_tables import SECRET_STREAM
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race


def test_a_fully_specified_fighter_decodes_to_exactly_the_request() -> None:
    request = DbzRequest(
        character=0,
        level=1,
        hp=Constraint.exactly(49500),
        bp=Constraint.exactly(28250),
        dp=Constraint.exactly(22750),
    )

    outcome = solve_dbz(request)

    assert outcome.card is not None
    card = decode_dbz(outcome.card.barcode)
    assert (card.character, card.level, card.hp, card.bp, card.dp) == (0, 1, 49500, 28250, 22750)


def test_a_stronger_form_is_reached_through_its_base_character() -> None:
    outcome = solve_dbz(DbzRequest(character=9))

    assert outcome.card is not None
    assert outcome.card.character == 9


def test_an_item_is_built_by_its_id() -> None:
    outcome = solve_dbz(DbzRequest(character=44, kind=DbzKind.ITEM))

    assert outcome.card is not None
    assert outcome.card.kind is DbzKind.ITEM
    assert outcome.card.character == 44


def test_a_level_of_none_is_reachable() -> None:
    outcome = solve_dbz(DbzRequest(character=19, no_level=True))

    assert outcome.card is not None
    assert outcome.card.level is None


@pytest.mark.parametrize(
    ("request_", "reason"),
    [
        (DbzRequest(character=14), "character 14 is not one the game can produce"),
        (DbzRequest(character=0, hp=Constraint.exactly(99600)), "hp of 99600 is above 99500"),
        (
            DbzRequest(character=0, bp=Constraint.exactly(1005)),
            "bp of 1005 is not a multiple of 10",
        ),
        (DbzRequest(character=0, level=4), "level 4 is not one the game can produce"),
    ],
    ids=["character", "ceiling", "multiple", "level"],
)
def test_an_impossible_request_names_the_reason(request_: DbzRequest, reason: str) -> None:
    outcome = solve_dbz(request_)

    assert outcome.card is None
    assert reason in outcome.blockers


def test_every_generated_digit_is_a_decimal_digit() -> None:
    outcome = solve_dbz(DbzRequest(character=5))

    assert outcome.card is not None
    assert outcome.card.barcode.isdigit()
    assert len(outcome.card.barcode) == 13


def test_the_hidden_stream_maps_back_to_real_digits() -> None:
    assert digits_for(SECRET_STREAM) == (0, 2, 4, 2, 5, 3, 7, 3, 7, 3)


def test_a_stream_whose_digits_would_pass_nine_has_none() -> None:
    assert digits_for((1 << 40) - 1) is None


def test_a_character_its_numbers_would_transform_is_reported_unreachable() -> None:
    request = DbzRequest(
        character=5,
        level=2,
        hp=Constraint.exactly(99500),
        bp=Constraint.exactly(48250),
        dp=Constraint.exactly(33250),
    )
    transformed = decode_dbz("0036348233367")

    outcome = solve_dbz(request)

    assert transformed.character == 13
    assert outcome.card is None
    assert outcome.blockers == ("no barcode satisfies every constraint at once",)


def test_a_request_naming_no_character_takes_any_fighter() -> None:
    outcome = solve_dbz(DbzRequest(hp=Constraint.exactly(40000)))

    assert outcome.card is not None
    assert outcome.card.kind is DbzKind.FIGHTER
    assert outcome.card.hp == 40000


def test_the_strongest_search_refuses_an_impossible_request() -> None:
    assert strongest_dbz(DbzRequest(character=14)) is None


def test_the_strongest_search_finds_nothing_when_the_numbers_transform_the_fighter() -> None:
    request = DbzRequest(
        character=5,
        level=2,
        hp=Constraint.exactly(99500),
        bp=Constraint.exactly(48250),
        dp=Constraint.exactly(33250),
    )

    assert strongest_dbz(request) is None


def test_a_shared_request_maps_attack_to_bp_and_defence_to_dp() -> None:
    shared = CardRequest(
        name="Rival",
        hp=Constraint.exactly(40000),
        st=Constraint.exactly(20000),
        df=Constraint.at_least(1000),
    )

    request = request_from(shared, character=7, level=2)

    assert request == DbzRequest(
        character=7,
        level=2,
        hp=Constraint.exactly(40000),
        bp=Constraint.exactly(20000),
        dp=Constraint.at_least(1000),
        name="Rival",
    )


def test_a_shared_request_naming_an_item_asks_for_an_item() -> None:
    assert request_from(CardRequest(), character=33, level=None).kind is DbzKind.ITEM


def test_every_field_the_game_has_no_place_for_is_named() -> None:
    shared = CardRequest(
        race=Race.HUMAN,
        character_class=CharacterClass.WARRIOR,
        job=3,
        speed=2,
        special=4,
        pp=Constraint.exactly(5),
        mp=Constraint.exactly(5),
    )

    unread = unread_fields(shared, back_read=True)

    assert unread == ("race", "class", "job", "speed", "ability", "herbs", "magic", "back-read")


def test_a_request_the_game_can_read_has_no_unread_fields() -> None:
    assert unread_fields(CardRequest(hp=Constraint.exactly(100)), back_read=False) == ()


def test_the_nearest_card_is_found_when_the_exact_numbers_cannot_print() -> None:
    request = DbzRequest(
        character=7,
        level=2,
        hp=Constraint.exactly(40000),
        bp=Constraint.exactly(20000),
        dp=Constraint.exactly(15000),
    )

    outcome = solve_dbz_nearest(request)

    assert solve_dbz(request).card is None
    assert outcome.card is not None
    assert outcome.exact is False
    assert (outcome.card.character, outcome.card.level) == (7, 2)
    assert abs(outcome.card.hp - 40000) <= NEAR_WIDTHS[-1]


def test_the_nearest_search_returns_an_exact_card_when_there_is_one() -> None:
    request = DbzRequest(character=0, level=1, hp=Constraint.exactly(49500))

    outcome = solve_dbz_nearest(request)

    assert outcome.exact is True
    assert outcome.card is not None
    assert outcome.card.hp == 49500


def test_the_nearest_search_keeps_the_reasons_when_nothing_is_near() -> None:
    outcome = solve_dbz_nearest(DbzRequest(character=14, hp=Constraint.exactly(1000)))

    assert outcome.card is None
    assert "character 14 is not one the game can produce" in outcome.blockers


def test_the_nearest_card_sits_close_to_every_number_asked_for() -> None:
    request = DbzRequest(
        character=7,
        level=2,
        hp=Constraint.exactly(5000),
        bp=Constraint.exactly(1750),
        dp=Constraint.exactly(1250),
    )

    outcome = solve_dbz_nearest(request)

    assert outcome.card is not None
    distance = (
        abs(outcome.card.hp - 5000) + abs(outcome.card.bp - 1750) + abs(outcome.card.dp - 1250)
    )
    assert distance == 5000


def test_a_request_for_any_fighter_finishes_within_its_stream_budget() -> None:
    request = DbzRequest(
        hp=Constraint.exactly(5000), bp=Constraint.exactly(1750), dp=Constraint.exactly(1250)
    )

    outcome = solve_dbz_nearest(request)

    assert outcome.card is not None
    assert outcome.card.kind is DbzKind.FIGHTER
