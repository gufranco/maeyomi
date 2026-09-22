"""Tests for the bundled Japanese supermarket."""

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.models.race import Race
from maeyomi.products.japan import (
    MINIMUM_PRODUCTS,
    JapaneseProduct,
    japanese_products,
    product_cards,
    random_products,
    search_products,
)

JAPANESE_PREFIXES = ("45", "49")


def test_the_shelf_is_stocked() -> None:
    assert len(japanese_products()) >= MINIMUM_PRODUCTS


def test_every_product_carries_a_japanese_barcode() -> None:
    for product in japanese_products():
        assert product.barcode.startswith(JAPANESE_PREFIXES), product.barcode


def test_every_product_reads_on_the_device() -> None:
    for product in japanese_products():
        assert decode(product.barcode).barcode == product.barcode


def test_every_product_has_a_name_written_in_japanese() -> None:
    for product in japanese_products():
        assert product.name
        assert not product.name.isascii(), product.name


def test_no_product_appears_twice() -> None:
    products = japanese_products()

    assert len({product.barcode for product in products}) == len(products)
    assert len({product.name for product in products}) == len(products)


def test_the_shelf_holds_both_fighters_and_items() -> None:
    kinds = {decode(product.barcode).race for product in japanese_products()}

    assert any(race.is_fighter for race in kinds)
    assert any(not race.is_fighter for race in kinds)
    assert len(kinds) >= 6


def test_a_product_knows_what_it_becomes() -> None:
    product = japanese_products()[0]

    assert isinstance(product, JapaneseProduct)
    assert isinstance(product.kind, Race)


def test_searching_finds_a_product_by_its_name() -> None:
    target = japanese_products()[0]

    found = search_products(target.name[:2])

    assert target.barcode in {product.barcode for product in found}


def test_searching_finds_a_product_by_its_barcode() -> None:
    target = japanese_products()[5]

    assert search_products(target.barcode)[0].barcode == target.barcode


def test_searching_for_nothing_returns_the_whole_shelf() -> None:
    assert len(search_products("   ")) == len(japanese_products())


def test_searching_for_something_absent_returns_nothing() -> None:
    assert search_products("zzzzzzzz") == ()


def test_cards_are_built_from_the_barcode_rather_than_the_list() -> None:
    cards = product_cards(japanese_products()[:5])

    assert len(cards) == 5
    for card in cards:
        assert card.character == decode(card.barcode)


def test_a_card_is_named_after_its_product() -> None:
    product = japanese_products()[0]

    assert product_cards([product])[0].name == product.name


@pytest.mark.parametrize("count", [1, 9, 30])
def test_a_random_handful_is_repeatable(count: int) -> None:
    assert [p.barcode for p in random_products(count, seed=7)] == [
        p.barcode for p in random_products(count, seed=7)
    ]
    assert len(random_products(count, seed=7)) == count
