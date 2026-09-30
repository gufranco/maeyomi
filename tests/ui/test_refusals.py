"""Every refusal the page can show comes back in Japanese as well as in English.

The page shows `detail_ja` when it is in Japanese, so each refusal a person can
cause from the page is asked for here and its Japanese is checked to be
Japanese, line for line with the English.
"""

import re
from typing import cast

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from maeyomi.datach.games import GAMES
from maeyomi.ui.app import create_app, refusal

JAPANESE = re.compile(r"[぀-ヿ㐀-鿿]")
RANDOM_SHORTFALL = {
    "count": 5,
    "seed": 1,
    "hp": "5000",
    "st": "1500",
    "df": "1200",
    "race": "human",
    "job": 3,
    "speed": 7,
    "ability": 0,
}
POSTS = [
    ("/api/generate", {"hp": "5050"}),
    ("/api/generate", {"hp": "25000"}),
    ("/api/generate", {"hp": "20500", "speed": 3}),
    ("/api/generate", {"st": "25000"}),
    ("/api/generate", {"job": 3, "class": "magician"}),
    ("/api/generate", {"hp": "abc"}),
    ("/api/generate", {"hp": "6000-5000"}),
    ("/api/generate", {"race": "dragon"}),
    ("/api/generate", {"class": "ninja"}),
    ("/api/generate", {"hp": "20000-20800", "race": "human", "nearest": True}),
    ("/api/generate", {"race": "weapon", "hp": "100", "nearest": True}),
    ("/api/random", RANDOM_SHORTFALL),
    ("/api/sheet-preview", {"device": "dbz", "race": "human"}),
    ("/api/device-card", {"device": "dbz", "race": "human"}),
    ("/api/device-card", {"device": "dbz", "character": "Mr. Satan"}),
    ("/api/device-card", {"device": "dbz", "hp": "99600"}),
    ("/api/device-card", {"device": "dbz", "hp": "1005"}),
    ("/api/device-card", {"device": "double", "backRead": True}),
    ("/api/device-card", {"device": "double", "race": "weapon"}),
    ("/api/device-card", {"device": "double", "st": "100000"}),
    ("/api/device-card", {"device": "double", "hp": "150"}),
    ("/api/device-card", {"device": "bb1", "class": "magician"}),
    ("/api/device-card", {"device": "bb1", "hp": "25000"}),
    ("/api/device-card", {"device": "ultraman", "hp": "7250", "st": "100", "df": "100"}),
    ("/api/device-cheat", {"device": "jleague"}),
    ("/api/device-cheat", {"device": "gameboy"}),
    ("/api/official-preview", {"set": "nowhere"}),
]


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    return TestClient(create_app(), base_url="http://localhost")


def as_lines(detail: object) -> list[object]:
    return cast("list[object]", detail) if isinstance(detail, list) else [detail]


def assert_japanese(body: dict[str, object]) -> None:
    lines = as_lines(body["detail"])
    translated = as_lines(body["detail_ja"])
    assert len(translated) == len(lines)
    assert all(isinstance(line, str) and JAPANESE.search(line) for line in translated)


@pytest.mark.parametrize(("url", "payload"), POSTS, ids=str)
def test_a_refusal_is_said_in_japanese(
    client: TestClient, url: str, payload: dict[str, object]
) -> None:
    response = client.post(url, json=payload)

    assert response.status_code in {400, 422}
    assert_japanese(response.json())


@pytest.mark.parametrize("barcode", ["0401207237509", "12345", "40012072375a1"])
def test_an_unreadable_barcode_is_refused_in_japanese(client: TestClient, barcode: str) -> None:
    response = client.get(f"/api/decode/{barcode}")

    assert response.status_code in {400, 404, 422}
    assert_japanese(response.json())


@pytest.mark.parametrize("device", list(GAMES), ids=str)
def test_a_card_a_game_does_not_know_is_refused_in_japanese(
    client: TestClient, device: object
) -> None:
    payload = {"device": str(device), "character": "Nobody at all"}

    response = client.post("/api/device-card", json=payload)

    assert response.status_code == 422
    assert_japanese(response.json())


def test_the_nearest_card_names_its_differences_in_japanese(client: TestClient) -> None:
    payload = {"hp": "20900", "st": "11000", "df": "10000", "race": "mechanical", "nearest": True}

    body = client.post("/api/generate", json=payload).json()

    assert len(body["differences_ja"]) == len(body["differences"]) > 0
    assert all(JAPANESE.search(line) for line in body["differences_ja"])


def test_the_refusal_handler_passes_on_an_error_that_is_not_a_refusal() -> None:
    error = ValueError("not a refusal")

    with pytest.raises(ValueError, match="not a refusal"):
        refusal(Request({"type": "http"}), error)
