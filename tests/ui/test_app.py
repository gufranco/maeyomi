"""Tests for the local web interface."""

import io

import pytest
from fastapi.testclient import TestClient

import maeyomi.ui.app as app_module
from maeyomi.barcode.verify import decode_pdf
from maeyomi.products.lookup import ProductLookupError
from maeyomi.ui.app import create_app


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


def test_the_races_endpoint_names_every_kind(client: TestClient) -> None:
    body = client.get("/api/races").json()

    assert len(body) == 10
    assert {race["name"] for race in body if race["is_fighter"]} == {
        "mechanical",
        "animal",
        "aquatic",
        "bird",
        "human",
    }
    assert all(race["description"] for race in body)


def test_the_abilities_endpoint_flags_the_ones_a_battle_ignores(client: TestClient) -> None:
    body = client.get("/api/abilities").json()

    assert body[0]["usable_in_battle"] is True
    assert body[49]["usable_in_battle"] is True
    assert body[50]["usable_in_battle"] is False


def test_a_card_preview_is_a_png_of_the_real_card(client: TestClient) -> None:
    response = client.post("/api/preview", json={"barcode": "0401207237501", "name": "Knight"})

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_a_preview_of_an_invalid_barcode_is_refused(client: TestClient) -> None:
    response = client.post("/api/preview", json={"barcode": "0401207237509"})

    assert response.status_code == 400
    assert "check digit" in response.json()["detail"]


def test_a_sheet_preview_returns_page_images(client: TestClient) -> None:
    response = client.post("/api/sheet-preview", json={"count": 2, "seed": 4})

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 2
    assert len(body["pages"]) == 1
    assert body["pages"][0].startswith("data:image/png;base64,")


def test_a_sheet_preview_that_cannot_be_filled_reports_the_shortfall(client: TestClient) -> None:
    response = client.post(
        "/api/sheet-preview",
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


def test_the_cheat_returns_the_strongest_card(client: TestClient) -> None:
    response = client.post("/api/cheat", json={"name": "Grandma"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Grandma"
    assert (body["character"]["hp"], body["character"]["st"], body["character"]["df"]) == (
        99900,
        14600,
        19900,
    )
    assert (body["character"]["battle_st"], body["character"]["battle_df"]) == (24600, None)


def test_the_cheat_has_a_silly_default_name(client: TestClient) -> None:
    response = client.post("/api/cheat", json={})

    assert response.json()["name"] == "Maximus Cheatimus"


def test_a_sheet_can_be_built_from_barcodes(client: TestClient, tmp_path: object) -> None:
    response = client.post(
        "/api/barcode-sheet",
        json={"cards": [{"barcode": "9994599095183", "name": "Maximus"}]},
    )

    assert response.status_code == 200
    assert sheet_codes(response.content, tmp_path) == ["9994599095183"]


def test_a_barcode_sheet_rejects_a_bad_barcode(client: TestClient) -> None:
    response = client.post("/api/barcode-sheet", json={"cards": [{"barcode": "123"}]})

    assert response.status_code == 400


def test_a_barcode_sheet_needs_at_least_one_card(client: TestClient) -> None:
    response = client.post("/api/barcode-sheet", json={"cards": []})

    assert response.status_code == 422


def test_the_official_sets_are_listed_with_their_counts(client: TestClient) -> None:
    response = client.get("/api/official")

    assert response.status_code == 200
    body = response.json()
    board = next(entry for entry in body["sets"] if entry["key"] == "board_game")
    assert board["english"] == "Barcode Battler II board game"
    assert board["count"] > 0
    assert body["total"] == 705
    assert len(body["rejected"]) == 4


@pytest.mark.parametrize(
    ("device", "sets", "total", "rejected"),
    [("bb2", 15, 705, 4), ("bb1", 5, 157, 1), ("double", 2, 56, 0), ("dbz", 1, 36, 0)],
)
def test_the_real_cards_are_only_those_of_the_chosen_device(
    client: TestClient, device: str, sets: int, total: int, rejected: int
) -> None:
    body = client.get(f"/api/official?device={device}").json()

    assert len(body["sets"]) == sets
    assert body["total"] == total
    assert len(body["rejected"]) == rejected


def test_every_card_of_a_device_prints_when_no_set_is_named(
    client: TestClient, tmp_path: object
) -> None:
    response = client.post("/api/official-sheet", json={"device": "dbz"})

    assert len(sheet_codes(response.content, tmp_path)) == 36


def test_a_device_preview_counts_only_that_device(client: TestClient) -> None:
    body = client.post("/api/official-preview", json={"device": "double"}).json()

    assert body["count"] == 56


def test_an_unknown_device_has_no_real_cards(client: TestClient) -> None:
    assert client.get("/api/official?device=gameboy").status_code == 422


def test_an_official_set_downloads_as_a_sheet(client: TestClient, tmp_path: object) -> None:
    response = client.post("/api/official-sheet", json={"set": "candy"})

    assert response.status_code == 200
    assert len(sheet_codes(response.content, tmp_path)) == 10


def test_an_unknown_official_set_is_rejected(client: TestClient) -> None:
    response = client.post("/api/official-sheet", json={"set": "nope"})

    assert response.status_code == 422


def test_an_official_set_can_be_previewed(client: TestClient) -> None:
    response = client.post("/api/official-preview", json={"set": "candy"})

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 10
    assert body["pages"][0].startswith("data:image/png;base64,")


def test_every_official_card_can_be_downloaded_at_once(client: TestClient) -> None:
    response = client.post("/api/official-sheet", json={})

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_a_product_barcode_reads_as_a_character(client: TestClient) -> None:
    response = client.get("/api/decode/4901085061169")

    assert response.status_code == 200
    body = response.json()
    assert body["barcode"] == "4901085061169"
    assert body["read_type"] in {"front", "back"}


def test_a_barcode_with_a_wrong_check_digit_says_so(client: TestClient) -> None:
    response = client.get("/api/decode/4901085061160")

    assert response.status_code == 400
    assert "check digit" in response.json()["detail"]


def test_an_eight_digit_barcode_reads_too(client: TestClient) -> None:
    response = client.get("/api/decode/49010856")

    assert response.status_code in {200, 400}


def test_the_shelf_is_served(client: TestClient) -> None:
    response = client.get("/api/products")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 500
    assert body["products"]


def test_the_shelf_can_be_searched_over_http(client: TestClient) -> None:
    response = client.get("/api/products", params={"q": "茶", "limit": 5})

    assert response.status_code == 200
    body = response.json()
    assert len(body["products"]) <= 5
    assert all("茶" in p["name"] or "茶" in p["brand"] for p in body["products"])


def test_every_served_product_says_what_it_becomes(client: TestClient) -> None:
    product = client.get("/api/products", params={"limit": 1}).json()["products"][0]

    assert product["kind"]
    assert product["label"]
    assert product["label_ja"]


def test_a_name_can_be_looked_up(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def answer(_: str) -> str:
        return "トマトソース"

    monkeypatch.setattr(app_module, "look_up_name", answer)

    response = client.get("/api/lookup/4901085061169")

    assert response.status_code == 200
    assert response.json() == {"barcode": "4901085061169", "name": "トマトソース"}


def test_a_lookup_that_cannot_reach_the_service_is_not_an_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def refuse(_: str) -> str:
        message = "no answer"
        raise ProductLookupError(message)

    monkeypatch.setattr(app_module, "look_up_name", refuse)

    response = client.get("/api/lookup/4901085061169")

    assert response.status_code == 200
    assert response.json()["name"] is None


def test_a_lookup_of_a_bad_barcode_is_refused(client: TestClient) -> None:
    response = client.get("/api/lookup/12")

    assert response.status_code == 400


def test_the_shelf_prints_as_a_sheet(client: TestClient, tmp_path: object) -> None:
    products = client.get("/api/products", params={"limit": 3}).json()["products"]
    cards = [{"barcode": p["barcode"], "name": p["name"]} for p in products]

    response = client.post("/api/barcode-sheet", json={"cards": cards})

    assert response.status_code == 200
    assert sheet_codes(response.content, tmp_path) == [p["barcode"] for p in products]


def test_the_shelf_reads_every_product_the_way_the_chosen_device_does(client: TestClient) -> None:
    body = client.get("/api/products", params={"limit": 40, "device": "dbz"}).json()

    kinds = {product["kind"] for product in body["products"]}
    assert kinds <= {"fighter", "item", "hidden"}
    fighter = next(product for product in body["products"] if product["kind"] == "fighter")
    assert "BP " in fighter["stats"]
    assert "DP " in fighter["stats"]
    item = next(product for product in body["products"] if product["kind"] == "item")
    assert item["stats"] == item["effect"]


def test_the_shelf_keeps_the_second_barcode_battler_numbers_by_default(client: TestClient) -> None:
    product = client.get("/api/products", params={"limit": 1}).json()["products"][0]

    assert product["kind"] == "single_use_armour"
    assert product["stats"] == "DF 100"


def test_a_shelf_sheet_prints_for_the_chosen_device(client: TestClient, tmp_path: object) -> None:
    products = client.get("/api/products", params={"limit": 2, "device": "dbz"}).json()
    cards = [
        {"barcode": p["barcode"], "name": p["name"], "device": "dbz"} for p in products["products"]
    ]

    response = client.post("/api/barcode-sheet", json={"cards": cards})

    assert sheet_codes(response.content, tmp_path) == [p["barcode"] for p in products["products"]]
