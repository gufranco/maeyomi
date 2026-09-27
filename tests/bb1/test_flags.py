"""Tests for the first Barcode Battler's flag table."""

import pytest

from maeyomi.bb1.flags import FIRST_UNLISTED_CODE, Flag

PUBLISHED = {
    0: ("No ability", "特殊能力なし"),
    5: ("Double own ST", "自分の破壊力100％アップ(2倍剣)"),
    6: ("Increase own DF by 50%", "自分の防御力50％アップ(受けるダメージが0.5倍になる)"),
    13: ("Reduce opponent DF to 0", "相手のDFダウン(相手のDFを0にする)"),
    18: ("Hero", "主人公フラグ(COM/B1モードで主人公として使える)"),
    19: ("Boss, B1 mode", "B1モード ボスフラグ"),
    35: ("Rewards player with passcode 092, B1 mode", "B1モード パスコード092"),
    39: ("Reduce opponent DF to 0", "相手のDFダウン(相手のDFを0にする)"),
}


@pytest.mark.parametrize(("code", "expected"), PUBLISHED.items())
def test_a_flag_carries_the_published_words_in_both_languages(
    code: int, expected: tuple[str, str]
) -> None:
    flag = Flag.from_code(code)

    assert (flag.description, flag.japanese) == expected


def test_every_code_from_zero_to_ninety_nine_has_words() -> None:
    flags = [Flag.from_code(code) for code in range(100)]

    assert all(flag.description and flag.japanese for flag in flags)


def test_an_unlisted_code_says_what_the_one_source_claims_and_that_it_is_alone() -> None:
    flag = Flag.from_code(FIRST_UNLISTED_CODE)

    assert "enemy's HP" in flag.description
    assert "one source" in flag.description
    assert not flag.is_documented


@pytest.mark.parametrize("code", [-1, 100])
def test_a_code_outside_two_digits_is_refused(code: int) -> None:
    with pytest.raises(ValueError, match="outside 00-99"):
        Flag.from_code(code)
