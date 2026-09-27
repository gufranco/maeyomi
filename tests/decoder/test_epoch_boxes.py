"""Tests for the barcodes on Epoch's own boxes, which the devices read as heroes."""

import pytest

from maeyomi.bb1.decode import decode_first
from maeyomi.decoder.decode import decode
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.double.decode import decode_double
from maeyomi.models.race import Race

FIRST_BOX = "4905040352507"
SECOND_BOX = "4905040352521"


@pytest.mark.parametrize(
    ("box", "job", "speed"),
    [(FIRST_BOX, 0, 6), (SECOND_BOX, 8, 7)],
    ids=["first-device-box", "second-device-box"],
)
def test_the_second_device_reads_each_box_as_the_uk_source_lists_it(
    box: str, job: int, speed: int
) -> None:
    character = decode(box)

    assert character.barcode == box
    assert (character.hp, character.st, character.df) == (5200, 1500, 100)
    assert (character.race, character.job, character.speed) == (Race.ANIMAL, job, speed)
    assert character.special.code == 50


@pytest.mark.parametrize("box", ["4905040352606", "4905040352705", "4905040352804"])
def test_a_software_box_nobody_has_recorded_is_refused_by_name(box: str) -> None:
    with pytest.raises(UnsupportedBarcodeError, match="Epoch box"):
        decode(box)


def test_the_first_device_reads_its_own_box_as_note_com_lists_it() -> None:
    card = decode_first(FIRST_BOX)

    assert card.barcode == FIRST_BOX
    assert (card.hp, card.st, card.df, card.dx) == (5200, 1500, 100, 2)
    assert (card.race, card.job, card.flag.code) == (Race.MECHANICAL, 2, 18)


def test_the_double_reads_a_box_the_way_the_second_device_does() -> None:
    card = decode_double(SECOND_BOX)

    assert (card.hp, card.st, card.df, card.job) == (5200, 1500, 100, 8)
