"""Tests for the Japanese text of the special abilities."""

import pytest

from barcode_battler.models.special_ability import (
    JAPANESE_UNDOCUMENTED,
    MAX_CODE,
    MIN_CODE,
    SpecialAbility,
)


@pytest.mark.parametrize("code", range(MIN_CODE, MAX_CODE + 1))
def test_a_documented_ability_is_documented_in_both_languages(code: int) -> None:
    ability = SpecialAbility.from_code(code)

    assert ability.is_documented == (ability.japanese != JAPANESE_UNDOCUMENTED)


def test_the_japanese_text_is_the_published_wording() -> None:
    assert SpecialAbility.from_code(18).japanese == "自分の破壊力１００％アップ 2倍剣"


def test_the_hero_flag_carries_its_famicom_effect_in_both_languages() -> None:
    ability = SpecialAbility.from_code(19)

    assert "Famicom" in ability.description
    assert "ファミコン版のみ" in ability.japanese


def test_an_undocumented_code_says_so_in_japanese() -> None:
    assert SpecialAbility.from_code(57).japanese == JAPANESE_UNDOCUMENTED
