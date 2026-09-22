"""Tests for random card generation."""

from maeyomi.decoder.decode import decode
from maeyomi.generator.random_cards import generate_random
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race


def template() -> CardRequest:
    return CardRequest(
        hp=Constraint.between(1000, 10000),
        st=Constraint.between(100, 3000),
        df=Constraint.between(100, 3000),
    )


def test_the_requested_number_of_cards_is_produced() -> None:
    batch = generate_random(24, template=template(), seed=7)

    assert len(batch.cards) == 24
    assert batch.shortfall == 0


def test_every_card_decodes_inside_the_requested_ranges() -> None:
    batch = generate_random(24, template=template(), seed=7)

    for card in batch.cards:
        decoded = decode(card.barcode)
        assert 1000 <= decoded.hp <= 10000
        assert 100 <= decoded.st <= 3000
        assert 100 <= decoded.df <= 3000


def test_no_barcode_is_repeated() -> None:
    batch = generate_random(40, template=template(), seed=3)

    assert len({card.barcode for card in batch.cards}) == len(batch.cards)


def test_the_same_seed_produces_the_same_batch() -> None:
    first = generate_random(12, template=template(), seed=99)
    second = generate_random(12, template=template(), seed=99)

    assert [card.barcode for card in first.cards] == [card.barcode for card in second.cards]


def test_a_different_seed_produces_a_different_batch() -> None:
    first = generate_random(12, template=template(), seed=1)
    second = generate_random(12, template=template(), seed=2)

    assert [card.barcode for card in first.cards] != [card.barcode for card in second.cards]


def test_a_fixed_race_is_honoured() -> None:
    batch = generate_random(10, template=CardRequest(race=Race.BIRD), seed=5)

    assert {decode(card.barcode).race for card in batch.cards} == {Race.BIRD}


def test_every_card_carries_a_name() -> None:
    batch = generate_random(5, template=template(), seed=11)

    assert all(card.name for card in batch.cards)


def test_a_batch_larger_than_the_reachable_space_reports_a_shortfall() -> None:
    narrow = CardRequest(
        hp=Constraint.exactly(5000),
        st=Constraint.exactly(1500),
        df=Constraint.exactly(1200),
        race=Race.HUMAN,
        job=3,
        speed=7,
        special=0,
    )

    batch = generate_random(5, template=narrow, seed=1)

    assert len(batch.cards) == 1
    assert batch.shortfall == 4
    assert batch.reason


def test_every_generated_card_carries_its_decoded_character() -> None:
    batch = generate_random(3, template=template(), seed=13)

    for card in batch.cards:
        assert card.character.barcode == card.barcode
