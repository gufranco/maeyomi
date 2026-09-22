"""Tests for looking a barcode up in the open product database.

No test here touches the network. The fetcher is passed in, so what is tested
is this project's handling of every answer the service can give: a product with
a name, a product without one, a code nobody has recorded, and a service that is
slow, broken or unreachable.
"""

import json
from typing import Self
from urllib.request import Request

import pytest

import maeyomi.products.lookup as lookup_module
from maeyomi.products.lookup import (
    API_URL,
    FIELDS,
    TIMEOUT_SECONDS,
    USER_AGENT,
    Fetcher,
    ProductLookupError,
    look_up_name,
)

FOUND = json.dumps(
    {"status": 1, "product": {"product_name_ja": "トマトケチャップ", "brands": "Kagome"}}
)
FOUND_ENGLISH_ONLY = json.dumps({"status": 1, "product": {"product_name": "Green tea"}})
MISSING = json.dumps({"status": 0})
NAMELESS = json.dumps({"status": 1, "product": {"quantity": "500 ml"}})
BARCODE = "4902102072618"


def fetcher(payload: str) -> Fetcher:
    def fetch(url: str, *, timeout: float) -> str:
        assert "4902102072618" in url
        assert timeout > 0
        return payload

    return fetch


def test_a_known_product_gives_its_japanese_name() -> None:
    assert look_up_name("4902102072618", fetch=fetcher(FOUND)) == "トマトケチャップ"


def test_a_product_named_only_in_english_gives_that() -> None:
    assert look_up_name("4902102072618", fetch=fetcher(FOUND_ENGLISH_ONLY)) == "Green tea"


def test_a_code_nobody_recorded_gives_nothing() -> None:
    assert look_up_name("4902102072618", fetch=fetcher(MISSING)) is None


def test_a_product_with_no_name_gives_nothing() -> None:
    assert look_up_name("4902102072618", fetch=fetcher(NAMELESS)) is None


def test_an_unreachable_service_is_reported_rather_than_raised_at_the_caller() -> None:
    def broken(url: str, *, timeout: float) -> str:
        raise OSError(url, timeout)

    with pytest.raises(ProductLookupError, match="could not be reached"):
        look_up_name("4902102072618", fetch=broken)


def test_an_answer_that_is_not_json_is_reported() -> None:
    with pytest.raises(ProductLookupError, match="did not answer"):
        look_up_name("4902102072618", fetch=fetcher("<html>maintenance</html>"))


def test_a_barcode_the_device_would_refuse_is_never_sent() -> None:
    def never(url: str, *, timeout: float) -> str:
        raise AssertionError(url, timeout)

    with pytest.raises(ValueError, match="digits"):
        look_up_name("hello", fetch=never)


def test_an_answer_that_is_not_an_object_is_no_name() -> None:
    assert look_up_name(BARCODE, fetch=fetcher("[]")) is None


def test_a_product_that_is_not_an_object_is_no_name() -> None:
    body = json.dumps({"status": 1, "product": "not a product"})

    assert look_up_name(BARCODE, fetch=fetcher(body)) is None


def test_the_real_fetcher_reads_what_it_is_given(monkeypatch: pytest.MonkeyPatch) -> None:
    opened: list[str] = []

    class Answer:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"status":0}'

    def fake_urlopen(request: Request, timeout: float) -> Answer:
        opened.append(request.full_url)
        assert timeout == TIMEOUT_SECONDS
        assert request.get_header("User-agent") == USER_AGENT
        return Answer()

    monkeypatch.setattr(lookup_module, "urlopen", fake_urlopen)

    assert look_up_name(BARCODE) is None
    assert opened == [API_URL.format(barcode=BARCODE) + f"?fields={FIELDS}"]


def test_a_brand_is_used_when_nobody_recorded_a_name() -> None:
    body = json.dumps({"status": 1, "product": {"brands": "Coca cola, The Coca-Cola Company"}})

    assert look_up_name(BARCODE, fetch=fetcher(body)) == "Coca cola"
