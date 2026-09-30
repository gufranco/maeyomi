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
from http.client import HTTPException
from importlib.metadata import version
from typing import Any, Final, cast
from urllib.request import Request, urlopen

from maeyomi.decoder.validation import validate_barcode

API_URL: Final = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
FIELDS: Final = "product_name_ja,product_name,brands"
PROJECT_URL: Final = "https://github.com/gufranco/maeyomi"
TIMEOUT_SECONDS: Final = 5.0
MAX_ANSWER_BYTES: Final = 256 * 1024
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
    except OSError as error:
        message = f"the product database could not be reached: {error}"
        raise ProductLookupError(message) from error
    except (HTTPException, UnicodeDecodeError) as error:
        message = f"the product database's answer could not be read: {error}"
        raise ProductLookupError(message) from error
    return _name_from(body)


def user_agent() -> str:
    """The name and installed version this project identifies itself by."""
    return f"maeyomi/{version('maeyomi')} (+{PROJECT_URL})"


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
    """Read a URL, identifying this project as the terms of use ask, up to a size limit."""
    request = Request(url, headers={"User-Agent": user_agent()})  # noqa: S310
    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        data: bytes = response.read(MAX_ANSWER_BYTES + 1)
    if len(data) > MAX_ANSWER_BYTES:
        message = f"the product database's answer is too large: over {MAX_ANSWER_BYTES} bytes"
        raise ProductLookupError(message)
    return data.decode("utf-8")
