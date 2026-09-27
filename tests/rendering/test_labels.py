"""Tests for the words printed on a card, in English and Japanese."""

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.race import Race
from maeyomi.models.special_ability import MAX_CODE, MIN_CODE, SpecialAbility
from maeyomi.rendering.labels import (
    DBZ_EFFECT,
    DBZ_FIGHTER,
    DBZ_MOVES,
    ITEM_CARD,
    NO_POWER,
    SPECIAL_POWER,
    STAT_LABELS,
    SWIPE,
    UNKNOWN_POWER,
    Bilingual,
    ability_text,
    class_label,
    dbz_level_text,
    panel_text,
    race_label,
)


def _both(label: Bilingual) -> None:
    assert label.english
    assert label.english.isascii()
    assert label.japanese
    assert not label.japanese.isascii()


@pytest.mark.parametrize("race", list(Race))
def test_every_race_is_named_in_both_languages(race: Race) -> None:
    _both(race_label(race))


def test_no_two_races_share_a_name_in_either_language() -> None:
    labels = [race_label(race) for race in Race]

    assert len({label.english for label in labels}) == len(labels)
    assert len({label.japanese for label in labels}) == len(labels)


@pytest.mark.parametrize("character_class", [*CharacterClass, None])
def test_every_class_is_named_in_both_languages(character_class: CharacterClass | None) -> None:
    _both(class_label(character_class))


def test_an_item_is_called_an_item_card() -> None:
    assert class_label(None) == ITEM_CARD


@pytest.mark.parametrize("key", ["HP", "ST", "DF", "BP", "DP"])
def test_every_stat_is_named_in_both_languages(key: str) -> None:
    _both(STAT_LABELS[key])


@pytest.mark.parametrize(
    "label",
    [SWIPE, SPECIAL_POWER, NO_POWER, UNKNOWN_POWER, ITEM_CARD, DBZ_FIGHTER, DBZ_MOVES, DBZ_EFFECT],
)
def test_every_caption_is_in_both_languages(label: Bilingual) -> None:
    _both(label)


@pytest.mark.parametrize("code", range(MIN_CODE, MAX_CODE + 1))
def test_every_ability_reads_in_both_languages(code: int) -> None:
    text = ability_text(SpecialAbility.from_code(code))

    assert text.english
    assert text.japanese


def test_an_undocumented_ability_is_named_in_plain_words() -> None:
    assert ability_text(SpecialAbility.from_code(57)) == UNKNOWN_POWER


def test_code_zero_says_there_is_no_power() -> None:
    assert ability_text(SpecialAbility.from_code(0)) == NO_POWER


def test_a_documented_ability_keeps_its_published_wording() -> None:
    text = ability_text(SpecialAbility.from_code(18))

    assert text.english == "own attack doubled"
    assert text.japanese == "自分の破壊力１００％アップ 2倍剣"


def test_a_card_whose_fight_matches_its_display_carries_only_the_ability() -> None:
    character = decode("2091000045007")

    assert panel_text(character) == ability_text(character.special)


def test_a_hidden_battle_defence_leads_the_panel_in_both_languages() -> None:
    character = decode("2095046145004")

    text = panel_text(character)

    assert text.english.startswith("Fights with DF 24600; ")
    assert text.japanese.startswith("たたかうと ぼうぎょ 24600。")


@pytest.mark.parametrize("level", [None, 0, 1, 2, 3])
def test_every_dragon_ball_level_is_worded_in_both_languages(level: int | None) -> None:
    _both(dbz_level_text(level))


def test_a_dragon_ball_level_names_its_number() -> None:
    assert dbz_level_text(2) == Bilingual("Special move level 2", "ひっさつわざ レベル2")
