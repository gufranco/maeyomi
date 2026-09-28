"""Tests for the 40-bit stream the Datach games build from a barcode."""

from maeyomi.datach.stream import (
    code_for,
    eight_bit,
    field,
    printable_mask,
    stream_of,
    stream_position,
    used_digits,
)
from maeyomi.datach.ultraman_tables import PERMUTATION

ZOFFY: str = "0315424322677"


def test_an_entry_names_a_byte_in_its_high_nibble_and_a_bit_in_its_low_one() -> None:
    top_of_first_byte = stream_position(0x07)

    assert top_of_first_byte == 39


def test_an_ean_13_code_gives_its_third_to_twelfth_digits() -> None:
    digits = used_digits(ZOFFY)

    assert digits == [1, 5, 4, 2, 4, 3, 2, 2, 6, 7]


def test_an_ean_8_code_gives_its_tail_mirrored_after_its_body() -> None:
    digits = used_digits("20158231")

    assert digits == [1, 5, 8, 2, 3, 1, 3, 2, 8, 5]


def test_a_field_is_read_from_the_top_of_the_stream() -> None:
    stream = 0b101 << 37

    assert field(stream, 0, 3) == 0b101


def test_the_stream_of_a_code_comes_back_out_as_the_same_code() -> None:
    stream = stream_of(ZOFFY, PERMUTATION)

    assert code_for(stream, PERMUTATION, "03") == ZOFFY


def test_a_stream_setting_a_bit_no_digit_reaches_has_no_code() -> None:
    unreachable = ((1 << 40) - 1) & ~(printable_mask(PERMUTATION) | eight_bit(PERMUTATION))

    assert code_for(unreachable, PERMUTATION, "03") is None


def test_the_shared_fourth_bit_turns_a_low_digit_into_an_eight_or_a_nine() -> None:
    stream = eight_bit(PERMUTATION)

    code = code_for(stream, PERMUTATION, "03")

    assert code is not None
    assert "8" in code[2:12]
    assert stream_of(code, PERMUTATION) == stream


def test_the_shared_fourth_bit_needs_a_digit_low_enough_to_carry_it() -> None:
    stream = printable_mask(PERMUTATION) | eight_bit(PERMUTATION)

    assert code_for(stream, PERMUTATION, "03") is None


def test_asking_for_no_eights_leaves_the_fourth_bit_unprintable() -> None:
    assert code_for(eight_bit(PERMUTATION), PERMUTATION, "03", eights=0) is None
