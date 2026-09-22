"""Tests for the special ability table published on barcodebattler.net/page05.htm."""

import pytest

from barcode_battler.models.special_ability import MAX_CODE, MIN_CODE, SpecialAbility


def test_code_zero_is_no_ability() -> None:
    ability = SpecialAbility.from_code(0)

    assert ability.description == "none"
    assert ability.is_documented


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (1, "triple damage against job 1"),
        (9, "triple damage against job 9"),
        (10, "triple damage against job 0"),
        (11, "triple damage against race 1"),
        (14, "triple damage against race 4"),
        (15, "triple damage against race 0"),
    ],
)
def test_triple_damage_codes_name_their_target(code: int, expected: str) -> None:
    ability = SpecialAbility.from_code(code)

    assert ability.description == expected


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (65, "on defeat, HP plus 1000"),
        (69, "on defeat, HP plus 10000"),
        (70, "on defeat, ST plus 200"),
        (74, "on defeat, ST plus 1000"),
        (75, "on defeat, DF plus 200"),
        (79, "on defeat, DF plus 1000"),
    ],
)
def test_on_defeat_bonus_codes(code: int, expected: str) -> None:
    ability = SpecialAbility.from_code(code)

    assert ability.description == expected


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (80, "on defeat, passcode 05"),
        (84, "on defeat, passcode 25"),
        (85, "on defeat, passcode 35"),
        (99, "on defeat, passcode 49"),
    ],
)
def test_passcode_codes(code: int, expected: str) -> None:
    ability = SpecialAbility.from_code(code)

    assert ability.description == expected


@pytest.mark.parametrize("code", [33, 34, 35, 36, 46, 47, 48, 49, 51, 64])
def test_gaps_in_the_published_table_are_reported_as_undocumented(code: int) -> None:
    ability = SpecialAbility.from_code(code)

    assert not ability.is_documented


@pytest.mark.parametrize(("code", "expected"), [(49, False), (50, True), (99, True)])
def test_c1_c2_only_boundary(code: int, expected: bool) -> None:
    ability = SpecialAbility.from_code(code)

    assert ability.is_c1_c2_only is expected


def test_every_code_in_range_resolves() -> None:
    abilities = [SpecialAbility.from_code(code) for code in range(MIN_CODE, MAX_CODE + 1)]

    assert len(abilities) == 100


@pytest.mark.parametrize("code", [-1, 100])
def test_out_of_range_code_is_rejected(code: int) -> None:
    with pytest.raises(ValueError, match="outside"):
        SpecialAbility.from_code(code)
