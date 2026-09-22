"""Tests for the local web interface."""

import io

import pytest
from fastapi.testclient import TestClient

from barcode_battler.barcode.verify import decode_pdf
from barcode_battler.ui.app import create_app


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    return TestClient(create_app())


def sheet_codes(content: bytes, tmp_path: object) -> list[str]:
    path = f"{tmp_path}/downloaded.pdf"
    with open(path, "wb") as handle:  # noqa: PTH123
        handle.write(content)
    return decode_pdf(path)


def test_the_page_is_served(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Barcode Battler" in response.text


def test_the_page_states_that_no_hardware_was_used(client: TestClient) -> None:
    response = client.get("/")

    assert "not been tested on a physical" in response.text


def test_decoding_a_barcode_returns_its_attributes(client: TestClient) -> None:
    response = client.get("/api/decode/0401207237501")

    assert response.status_code == 200
    body = response.json()
    assert body["hp"] == 4000
    assert body["race"] == "aquatic"
    assert body["special"]["code"] == 50


def test_decoding_an_invalid_barcode_reports_the_reason(client: TestClient) -> None:
    response = client.get("/api/decode/0401207237509")

    assert response.status_code == 400
    assert "check digit" in response.json()["detail"]


def test_generating_a_card_returns_the_comparison(client: TestClient) -> None:
    response = client.post(
        "/api/generate",
        json={"name": "Fire Knight", "hp": "5000", "st": "1800", "df": "1200", "race": "human"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["barcode"]
    assert body["character"]["hp"] == 5000
    assert body["mismatches"] == []


def test_generating_an_impossible_card_names_the_field(client: TestClient) -> None:
    response = client.post("/api/generate", json={"hp": "5050"})

    assert response.status_code == 422
    assert any("multiple of 100" in reason for reason in response.json()["detail"])


def test_a_generated_card_can_be_downloaded_as_a_sheet(
    client: TestClient, tmp_path: object
) -> None:
    response = client.post(
        "/api/sheet",
        json={"cards": [{"name": "Fire Knight", "hp": "5000", "race": "human"}]},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(sheet_codes(response.content, tmp_path)) == 1


def test_a_random_sheet_can_be_downloaded(client: TestClient, tmp_path: object) -> None:
    response = client.post(
        "/api/random",
        json={"count": 4, "seed": 3, "hp": "1000-9000", "st": "100-3000", "df": "100-3000"},
    )

    assert response.status_code == 200
    assert len(sheet_codes(response.content, tmp_path)) == 4


def test_a_random_sheet_that_cannot_be_filled_reports_the_shortfall(client: TestClient) -> None:
    response = client.post(
        "/api/random",
        json={
            "count": 5,
            "seed": 1,
            "hp": "5000",
            "st": "1500",
            "df": "1200",
            "race": "human",
            "job": 3,
            "speed": 7,
            "ability": 0,
        },
    )

    assert response.status_code == 422
    assert "distinct" in response.json()["detail"]


def test_an_unreadable_value_is_reported(client: TestClient) -> None:
    response = client.post("/api/generate", json={"hp": "abc"})

    assert response.status_code == 422
    assert "5000-6000" in str(response.json()["detail"])


def test_the_abilities_table_is_served(client: TestClient) -> None:
    response = client.get("/api/abilities")

    assert response.status_code == 200
    table = response.json()
    assert len(table) == 100
    assert table[50]["description"].startswith("hero flag")


def test_an_empty_sheet_request_is_rejected(client: TestClient) -> None:
    response = client.post("/api/sheet", json={"cards": []})

    assert response.status_code == 422


def test_the_downloaded_sheet_is_named(client: TestClient) -> None:
    response = client.post("/api/random", json={"count": 1, "seed": 1})

    assert "attachment" in response.headers["content-disposition"]
    assert io.BytesIO(response.content).read(4) == b"%PDF"


def test_a_sheet_containing_an_impossible_card_is_rejected(client: TestClient) -> None:
    response = client.post("/api/sheet", json={"cards": [{"hp": "5050"}]})

    assert response.status_code == 422
    assert any("multiple of 100" in reason for reason in response.json()["detail"])


UNREACHABLE = {"hp": "20900", "st": "11000", "df": "10000", "race": "mechanical"}


def test_an_impossible_card_is_refused_without_the_nearest_flag(client: TestClient) -> None:
    response = client.post("/api/generate", json=UNREACHABLE)

    assert response.status_code == 422


def test_the_nearest_flag_returns_the_closest_card(client: TestClient) -> None:
    response = client.post("/api/generate", json={**UNREACHABLE, "nearest": True})

    assert response.status_code == 200
    body = response.json()
    assert body["is_exact"] is False
    assert body["distance"] > 0
    assert body["differences"]
    assert body["character"]["race"] == "mechanical"


def test_a_back_read_card_can_be_requested(client: TestClient) -> None:
    response = client.post("/api/generate", json={"race": "human", "backRead": True})

    assert response.status_code == 200
    assert response.json()["character"]["read_type"] == "back"


def test_the_nearest_flag_is_refused_alongside_a_back_read(client: TestClient) -> None:
    response = client.post(
        "/api/generate",
        json={"hp": "99900", "race": "human", "backRead": True, "nearest": True},
    )

    assert response.status_code == 422


def test_the_nearest_flag_reports_when_there_is_no_close_card_either(client: TestClient) -> None:
    response = client.post(
        "/api/generate", json={"hp": "20000-20800", "race": "human", "nearest": True}
    )

    assert response.status_code == 422
    assert any("window" in reason for reason in response.json()["detail"])
