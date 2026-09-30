"""Tests for how the page and its files are cached, and the headers they carry."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from maeyomi.ui.app import STATIC_DIR, create_app
from maeyomi.ui.assets import asset_stamp, stamped


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    return TestClient(create_app(), base_url="http://localhost")


def test_every_asset_link_carries_the_content_stamp(client: TestClient) -> None:
    page = client.get("/").text
    stamp = asset_stamp(STATIC_DIR)

    for name in ("app.css", "i18n.js", "devices.js", "app.js"):
        assert f"/static/{name}?v={stamp}" in page


def test_the_stamp_changes_when_a_file_changes(tmp_path: Path) -> None:
    (tmp_path / "a.js").write_text("one")
    before = asset_stamp(tmp_path)
    (tmp_path / "a.js").write_text("two")

    assert asset_stamp(tmp_path) != before


def test_only_static_asset_links_are_stamped() -> None:
    markup = '<script src="/static/app.js"></script><a href="https://example.test/static/x.js">'

    result = stamped(markup, "abc")

    assert result == (
        '<script src="/static/app.js?v=abc"></script><a href="https://example.test/static/x.js">'
    )


def test_the_page_is_never_cached(client: TestClient) -> None:
    assert client.get("/").headers["cache-control"] == "no-store"


def test_an_asset_is_cached_for_a_year(client: TestClient) -> None:
    response = client.get("/static/app.js")

    assert response.headers["cache-control"] == "public, max-age=31536000, immutable"


def test_the_page_carries_a_strict_content_security_policy(client: TestClient) -> None:
    headers = client.get("/").headers

    policy = headers["content-security-policy"]
    assert "script-src 'self'" in policy
    assert "unsafe-inline" not in policy
    assert "object-src 'none'" in policy
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["referrer-policy"] == "no-referrer"
