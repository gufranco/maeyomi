"""Ask the open product database what a barcode is called.

The device needs no name: the barcode alone decides every number on the card.
A name is decoration, so this is a convenience that must never be allowed to
fail the work around it. Every failure is reported as one error type and every
caller is expected to carry on without a name.

The source is Open Food Facts, whose data is published under the Open Database
License. Its terms ask for an identifying user agent, which is sent below.
"""

import json
from collections.abc import Callable
from typing import Any, Final, cast
from urllib.error import URLError
from urllib.request import Request, urlopen

from maeyomi.decoder.validation import validate_barcode

API_URL: Final = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
FIELDS: Final = "product_name_ja,product_name,brands"
USER_AGENT: Final = "maeyomi/0.1 (personal card generator)"
TIMEOUT_SECONDS: Final = 5.0
FOUND: Final = 1
NAME_KEYS: Final = ("product_name_ja", "product_name", "brands")
"""Tried in turn. A brand is a poor name and beats no name at all."""

Fetcher = Callable[..., str]


class ProductLookupError(RuntimeError):
    """The product database could not be asked, or did not answer sensibly."""


def look_up_name(barcode: str, *, fetch: Fetcher | None = None) -> str | None:
    """The product's name, or None when nobody has recorded one.

    Raises `ProductLookupError` when the service itself is the problem, so a
    caller can tell "no such product" from "no answer".
    """
    code = validate_barcode(barcode)
    url = API_URL.format(barcode=code) + f"?fields={FIELDS}"
    try:
        body = (fetch or _fetch)(url, timeout=TIMEOUT_SECONDS)
    except (OSError, URLError) as error:
        message = f"the product database could not be reached: {error}"
        raise ProductLookupError(message) from error
    return _name_from(body)


def _name_from(body: str) -> str | None:
    """Read the name out of an answer, rejecting one that is not an answer."""
    try:
        decoded: Any = json.loads(body)
    except json.JSONDecodeError as error:
        message = "the product database did not answer with a product"
        raise ProductLookupError(message) from error
    if not isinstance(decoded, dict):
        return None
    payload = cast("dict[str, Any]", decoded)
    if payload.get("status") != FOUND:
        return None
    raw: Any = payload.get("product")
    if not isinstance(raw, dict):
        return None
    product = cast("dict[str, Any]", raw)
    for key in NAME_KEYS:
        name = product.get(key)
        if isinstance(name, str) and name.strip():
            return name.strip().split(",")[0].strip()
    return None


def _fetch(url: str, *, timeout: float) -> str:
    """Read a URL, identifying this project as the terms of use ask."""
    request = Request(url, headers={"User-Agent": USER_AGENT})  # noqa: S310
    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        return str(response.read().decode("utf-8"))
