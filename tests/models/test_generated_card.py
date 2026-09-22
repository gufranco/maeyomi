"""Tests for the finished card model."""

import dataclasses

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.models.generated_card import GeneratedCard


def build() -> GeneratedCard:
    barcode = "0401207237501"
    return GeneratedCard(name="Fire Knight", barcode=barcode, character=decode(barcode))


def test_a_card_carries_its_name_barcode_and_decoded_character() -> None:
    card = build()

    assert card.name == "Fire Knight"
    assert card.barcode == "0401207237501"
    assert card.character.hp == 4000


def test_the_character_was_decoded_from_the_same_barcode() -> None:
    card = build()

    assert card.character.barcode == card.barcode


def test_a_card_is_immutable() -> None:
    card = build()

    with pytest.raises(dataclasses.FrozenInstanceError):
        card.name = "Other"  # type: ignore[misc]
