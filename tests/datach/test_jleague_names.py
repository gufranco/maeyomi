"""Tests for the teams and players Datach J.League Super Top Players knows."""

import pytest

from maeyomi.datach.jleague_names import PLAYERS, TEAMS, card_named, ident_of


def test_every_team_has_fifteen_players_named_in_both_languages() -> None:
    assert len(TEAMS) == 10
    assert set(PLAYERS) == {(team, number) for team in range(10) for number in range(1, 16)}
    assert all(english and japanese for english, japanese in PLAYERS.values())


@pytest.mark.parametrize(
    ("typed", "expected"),
    [("Zico", ident_of(0, 10)), ("ジーコ", ident_of(0, 10)), ("Kashima Antlers", 0), ("16", 16)],
)
def test_a_card_is_found_by_a_name_or_its_number(typed: str, expected: int) -> None:
    assert card_named(typed) == expected


def test_an_unknown_card_is_refused() -> None:
    with pytest.raises(ValueError, match=r"unknown J\.League card"):
        card_named("Pele")
