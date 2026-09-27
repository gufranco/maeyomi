"""The back read against a second, independent source of its formulas.

barcodebattler.co.uk, "Barcode Battler Museum: Barcode Battler II" technical
info, Method 2, writes the back read's formulas out per mode in terms of the
last five digits, P to T. The decoder is a port of the MIT simulator instead,
so agreement on every digit combination is evidence that both describe the
device rather than each other.
"""

import itertools

import pytest

from maeyomi.decoder.back_read import read_back
from maeyomi.decoder.c1_rescale import rescale_for_c1
from maeyomi.decoder.check_digit import expected_check_digit


def back_read_code(p: int, q: int, r: int, s: int, t: int) -> str:
    free = next(
        digit for digit in range(10) if expected_check_digit(f"2{digit}000000{p}{q}{r}{s}") == t
    )
    return f"2{free}000000{p}{q}{r}{s}{t}"


def c0_item(p: int, q: int, r: int, s: int, t: int) -> tuple[str, int]:
    if t in {5, 6}:
        return "st", 1000 * (1 + (r + 5) % 10 // 4) + 100 * ((q + 5) % 10)
    if t in {7, 8}:
        return "df", 1000 * ((q + 7) % 10 // 4) + 100 * ((p + 7) % 10)
    return "hp", 10000 * (s // 8) + 1000 * r + 100 * q


@pytest.mark.parametrize("t", [5, 6, 7, 8, 9])
def test_every_c0_item_matches_the_uk_formula(t: int) -> None:
    disagreeing: list[tuple[int, int, int, int]] = []
    for p, q, r, s in itertools.product(range(10), repeat=4):
        field, expected = c0_item(p, q, r, s, t)
        produced = getattr(read_back(back_read_code(p, q, r, s, t)), field)
        if produced != expected:
            disagreeing.append((p, q, r, s))

    assert disagreeing == []


def test_every_c1_hero_matches_the_uk_formula() -> None:
    disagreeing: list[tuple[int, int, int, int]] = []
    for p, q, r, s in itertools.product(range(10), repeat=4):
        hero = rescale_for_c1(read_back(back_read_code(p, q, r, s, 4)))
        expected = (
            100 * (10 * (s // 2) + r),
            100 * ((r + 5) % 10 + 3),
            100 * ((q + 7) % 10 + 3),
        )
        if (hero.hp, hero.st, hero.df) != expected:
            disagreeing.append((p, q, r, s))

    assert disagreeing == []
