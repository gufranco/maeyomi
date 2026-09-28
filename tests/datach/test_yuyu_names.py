"""Tests for the names Datach Yu Yu Hakusho gives its characters, techniques and items."""

import pytest

from maeyomi.datach.yuyu_names import CHARACTERS, ITEMS, TECHNIQUE_NAMES, bonus_text, card_named
from maeyomi.datach.yuyu_tables import NUMBERS, TECHNIQUES, TYPE_SLOTS


def test_every_character_and_item_has_a_name_in_both_languages() -> None:
    slots = {ident for ident, _ in TYPE_SLOTS}

    assert set(CHARACTERS) | set(ITEMS) == slots | {20}
    assert set(CHARACTERS) == set(range(len(NUMBERS)))


def test_every_technique_a_character_can_use_is_named() -> None:
    used = {technique for four in TECHNIQUES for technique in four if technique}

    assert used == set(TECHNIQUE_NAMES)


def test_every_item_that_adds_nothing_says_what_it_does_instead() -> None:
    rules = [ITEMS[ident] for ident in (38, 39, 40, 41)]

    assert all(item.effect and item.effect_japanese for item in rules)


def test_a_bonus_is_worded_the_way_the_game_words_it() -> None:
    assert bonus_text(400, 110) == (
        "Adds 400 HP and 110 SP.",
        "このカードは、HPが 400・SPが 110 アップするぞ。",
    )
    assert bonus_text(0, 500) == ("Adds 500 SP.", "このカードは、SPが 500 アップするぞ。")


@pytest.mark.parametrize(
    ("typed", "expected"), [("Yusuke", 0), ("ゆうすけ", 0), ("Botan", 33), ("40", 40)]
)
def test_a_card_is_found_by_either_name_or_its_number(typed: str, expected: int) -> None:
    assert card_named(typed) == expected


def test_an_unknown_card_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown Yu Yu Hakusho card"):
        card_named("Goku")
