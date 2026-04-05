"""E2E tests for URL query parameter synchronization."""
import json
import urllib.parse

from playwright.sync_api import expect
from conftest import wait_for_app_ready, set_number_input, get_number_input


def test_url_params_preload(streamlit_server, page):
    url = streamlit_server + "/?principal=3000000&term=25&rate=2.5&refi_year=5"
    page.goto(url)
    page.wait_for_selector("h1", timeout=15000)
    wait_for_app_ready(page)

    # Verify "Splácená částka" shows "3 000 000"
    principal_input = page.locator('[data-testid="stTextInput"] input').first
    expect(principal_input).to_have_value("3 000 000")

    # Verify "Délka splácení" shows 25
    term_input = get_number_input(page, "Délka splácení")
    expect(term_input).to_have_value("25")

    # Verify "Úrok" shows 2.5 or 2.50
    rate_input = get_number_input(page, "Úrok [%]")
    value = rate_input.input_value()
    assert float(value) == 2.5


def test_url_params_variants(streamlit_server, page):
    variants = [{"rate": 5.0, "years": 0, "extra": 0}]
    variants_json = json.dumps(variants, separators=(",", ":"))
    encoded = urllib.parse.quote(variants_json)
    url = f"{streamlit_server}/?variants={encoded}"
    page.goto(url)
    page.wait_for_selector("h1", timeout=15000)
    wait_for_app_ready(page)

    # Variant 1 rate should be 5.0
    rate_input = get_number_input(page, "Nový úrok")
    value = rate_input.input_value()
    assert float(value) == 5.0


def test_url_syncs_after_change(app_page):
    set_number_input(app_page, "Délka splácení", 20)
    # Wait for URL to update
    app_page.wait_for_timeout(1000)
    assert "term=20" in app_page.url
