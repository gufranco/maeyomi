"""A shelf of real Japanese supermarket products, each of which is a card.

The device reads any barcode, which is how it was played: a bottle of tomato
sauce is a fighter and a packet of crisps is a weapon. This is a curated shelf
of real products so a game can be played without a shopping trip.

The list comes from Open Food Facts, filtered to barcodes issued to Japanese
companies, the 45 and 49 prefixes, with a name written in Japanese that this
project's decoder accepts. Names, brands and barcodes are their data, published
under the Open Database License; see NOTICE.md. The numbers on each card are
never taken from that data. They are read from the barcode by this project's own
decoder, so a wrong name spoils a joke and nothing else.
"""

import json
import random
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache
from importlib import resources
from typing import Final

from maeyomi.decoder.decode import decode
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.models.race import Race

DATA_FILE: Final = "japan.json"
MINIMUM_PRODUCTS: Final = 500
"""What the shelf must hold to be worth browsing, asserted in the tests."""


SHELF_SOURCE: Final = "https://world.openfoodfacts.org/"
SHELF_LICENCE: Final = "Open Database License 1.0 (ODbL)"


@dataclass(frozen=True, slots=True)
class JapaneseProduct:
    """One product on the shelf, and what the device makes of it."""

    barcode: str
    name: str
    brand: str
    kind: Race


@cache
def japanese_products() -> tuple[JapaneseProduct, ...]:
    """Every product on the shelf, in barcode order."""
    raw = resources.files("maeyomi.products").joinpath(DATA_FILE).read_text("utf-8")
    return tuple(
        JapaneseProduct(
            barcode=entry["barcode"],
            name=entry["name"],
            brand=entry["brand"],
            kind=Race[entry["kind"].upper()],
        )
        for entry in json.loads(raw)["products"]
    )


def search_products(query: str) -> tuple[JapaneseProduct, ...]:
    """Every product whose name, brand or barcode contains the query."""
    wanted = query.strip().casefold()
    if not wanted:
        return japanese_products()
    return tuple(
        product
        for product in japanese_products()
        if wanted in product.name.casefold()
        or wanted in product.brand.casefold()
        or wanted in product.barcode
    )


def random_products(count: int, *, seed: int | None = None) -> tuple[JapaneseProduct, ...]:
    """A handful off the shelf, repeatable from a seed."""
    shelf = japanese_products()
    return tuple(random.Random(seed).sample(shelf, min(count, len(shelf))))  # noqa: S311


def product_cards(products: Sequence[JapaneseProduct]) -> tuple[GeneratedCard, ...]:
    """Turn products into cards, reading every number off the barcode."""
    return tuple(
        GeneratedCard(name=product.name, barcode=product.barcode, character=decode(product.barcode))
        for product in products
    )
