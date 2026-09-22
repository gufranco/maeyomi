"""Tests for the words printed on a card, in English and Japanese."""

import pytest

from barcode_battler.models.character_class import CharacterClass
from barcode_battler.models.race import Race
from barcode_battler.models.special_ability import MAX_CODE, MIN_CODE, SpecialAbility
from barcode_battler.rendering.labels import (
    ITEM_CARD,
    NO_POWER,
    SPECIAL_POWER,
    STAT_LABELS,
    SWIPE,
    UNKNOWN_POWER,
    Bilingual,
    ability_text,
    class_label,
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


@pytest.mark.parametrize("key", ["HP", "ST", "DF"])
def test_every_stat_is_named_in_both_languages(key: str) -> None:
    _both(STAT_LABELS[key])


@pytest.mark.parametrize("label", [SWIPE, SPECIAL_POWER, NO_POWER, UNKNOWN_POWER, ITEM_CARD])
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
