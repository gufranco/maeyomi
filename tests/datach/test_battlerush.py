"""Tests for the robot cards Datach Battle Rush reads in pairs."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.battlerush import (
    FRAME_CARD,
    WEAPON_CARD,
    RobotOrder,
    build_robot,
    decode_battlerush,
    robot_stats,
    strongest_robot,
)
from maeyomi.datach.game_card import GameKind
from maeyomi.decoder.errors import BarcodeError

STRONGEST_STATS = {"attack": 233, "defense": 233, "speed": 233, "recovery": 255, "weight": 197}
FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "datach_battlerush.json"


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["pairs"]


@pytest.mark.parametrize("entry", recorded(), ids=lambda entry: str(entry["frame"]))
def test_every_pair_makes_the_robot_the_game_itself_built_in_mame(
    entry: dict[str, object],
) -> None:
    stats = robot_stats(
        decode_battlerush(str(entry["frame"])), decode_battlerush(str(entry["weapons"]))
    )

    assert stats == entry["stats"]


def test_a_last_digit_one_below_the_check_is_a_frame_card() -> None:
    card = decode_battlerush("0021495637396")

    assert (card.kind, card.ident, card.traits[0]) == (GameKind.UNIT, 16, FRAME_CARD)


def test_a_last_digit_two_below_the_check_is_a_weapon_card() -> None:
    card = decode_battlerush("0021474877439")

    assert (card.kind, card.ident, card.traits[0]) == (GameKind.ITEM, 16, WEAPON_CARD)


def test_a_shop_barcode_with_a_correct_check_digit_is_refused() -> None:
    assert decode_battlerush("4912345678904").kind is GameKind.NO_EFFECT


def test_a_pair_makes_the_robot_the_game_built_in_mame() -> None:
    stats = robot_stats(decode_battlerush("0021495637396"), decode_battlerush("0021474877439"))

    assert stats == STRONGEST_STATS


def test_cards_of_two_different_robots_make_no_robot() -> None:
    frame = decode_battlerush("0021495637396")
    other = build_robot(RobotOrder(ident=17))

    assert other is not None
    assert robot_stats(frame, other[1]) is None


def test_a_built_pair_reads_back_as_the_parts_and_levels_asked_for() -> None:
    order = RobotOrder(ident=3, head=4, body=5, shoulder=6, foot=7, pilot=2, levels=(1, 2, 3, 4))

    pair = build_robot(order)

    assert pair is not None
    frame, weapons = pair
    assert (frame.ident, frame.traits[2:7]) == (3, (4, 5, 6, 7, 2))
    assert (weapons.ident, weapons.traits[-4:]) == (3, (1, 2, 3, 4))


def test_the_strongest_pair_is_the_robot_with_every_stat_at_its_top() -> None:
    frame, weapons = strongest_robot()

    assert robot_stats(frame, weapons) == STRONGEST_STATS


def test_a_code_that_is_not_thirteen_digits_is_refused() -> None:
    with pytest.raises(BarcodeError):
        decode_battlerush("12345")


def test_a_short_barcode_is_read_and_refused_like_any_shop_barcode() -> None:
    card = decode_battlerush("49123456")

    assert card.kind is GameKind.NO_EFFECT


def test_a_short_barcode_with_a_wrong_check_digit_is_still_malformed() -> None:
    with pytest.raises(BarcodeError):
        decode_battlerush("49123457")


@pytest.mark.parametrize(
    "order",
    [RobotOrder(ident=64), RobotOrder(ident=1, head=32), RobotOrder(ident=1, levels=(8, 0, 0, 0))],
)
def test_a_number_wider_than_its_field_builds_no_pair(order: RobotOrder) -> None:
    assert build_robot(order) is None


def test_a_code_with_a_letter_is_refused() -> None:
    with pytest.raises(BarcodeError):
        decode_battlerush("00214956373A6")
