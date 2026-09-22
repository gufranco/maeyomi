"""Tests for the C1 and C2 hero rescaling applied to a back-read card."""

from maeyomi.decoder.c1_rescale import rescale_for_c1
from maeyomi.decoder.decode import decode


def test_the_rescale_divides_hit_points_by_ten() -> None:
    original = decode("7310707558739")

    rescaled = rescale_for_c1(original)

    assert rescaled.hp == original.hp_units // 10 * 100


def test_strength_gains_one_unit_and_defence_gains_three() -> None:
    original = decode("7310707558739")

    rescaled = rescale_for_c1(original)

    assert rescaled.st_units == original.st_units // 10 + 1
    assert rescaled.df_units == original.df_units // 10 + 3


def test_the_original_is_left_untouched() -> None:
    original = decode("7310707558739")

    rescale_for_c1(original)

    assert original.hp == decode("7310707558739").hp


def test_every_other_field_is_carried_across() -> None:
    original = decode("7310707558739")

    rescaled = rescale_for_c1(original)

    assert rescaled.race is original.race
    assert rescaled.special == original.special
    assert rescaled.barcode == original.barcode
