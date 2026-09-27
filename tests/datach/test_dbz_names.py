"""Tests for the names and effects Datach Dragon Ball Z shows for each id."""

import pytest

from maeyomi.datach.dbz_names import FIGHTERS, ITEMS, fighter_name, item_entry
from maeyomi.datach.dbz_tables import FIGHTER_SLOTS, FORMS, ITEM_SLOTS


def test_every_fighter_the_game_can_produce_has_a_name() -> None:
    reachable = {identifier for identifier, _ in FIGHTER_SLOTS} | {form[-1] for form in FORMS}

    assert reachable <= set(FIGHTERS)


def test_every_item_the_game_can_produce_has_a_name_and_an_effect() -> None:
    reachable = {identifier for identifier, _ in ITEM_SLOTS}

    assert reachable == set(ITEMS)


@pytest.mark.parametrize("name", [*FIGHTERS.values()])
def test_every_fighter_is_named_in_both_languages(name: tuple[str, str]) -> None:
    english, japanese = name

    assert english
    assert japanese


def test_super_saiyan_goku_is_named_as_the_game_shows_him() -> None:
    assert fighter_name(9) == ("Super Saiyan Goku", "Sゴクウ")


def test_an_item_carries_its_effect_in_both_languages() -> None:
    entry = item_entry(33)

    assert entry is not None
    assert (entry.english, entry.japanese) == ("Senzu bean", "せんず")
    assert entry.effect == "Fully restores HP, BP and DP"
    assert entry.effect_japanese == "HP BP DPを かんぜんかいふく"


def test_an_id_the_game_never_produces_has_no_name() -> None:
    assert fighter_name(14) is None
    assert item_entry(60) is None
