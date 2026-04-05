"""E2E tests for variant management (add, remove, input visibility)."""
from playwright.sync_api import expect
from conftest import wait_for_app_ready, find_variant_section


def test_variant1_has_only_rate(app_page):
    section = find_variant_section(app_page, 1)
    assert section is not None, "Varianta 1 section not found"

    text = section.text_content()
    assert "Nový úrok" in text
    assert "Přidání/odebrání let" not in text
    assert "Navýšení hypotéky" not in text


def test_variant2_has_all_inputs(app_page):
    section = find_variant_section(app_page, 2)
    assert section is not None, "Varianta 2 section not found"

    text = section.text_content()
    assert "Nový úrok" in text
    assert "Přidání/odebrání let" in text
    assert "Navýšení hypotéky" in text


def test_add_variant(app_page):
    add_button = app_page.get_by_role("button", name="Přidat variantu")
    add_button.click()
    wait_for_app_ready(app_page)

    # After adding, look for Varianta 3 text
    v3_text = app_page.get_by_text("Varianta 3", exact=False)
    expect(v3_text.first).to_be_visible(timeout=10000)

    section = find_variant_section(app_page, 3)
    assert section is not None, "Varianta 3 section not found after adding"

    text = section.text_content()
    assert "Nový úrok" in text
    assert "Přidání/odebrání let" in text
    assert "Navýšení hypotéky" in text

    # Verify Smazat button exists
    delete_button = section.get_by_role("button", name="Smazat")
    expect(delete_button).to_be_visible()


def test_remove_variant(app_page):
    add_button = app_page.get_by_role("button", name="Přidat variantu")
    add_button.click()
    wait_for_app_ready(app_page)

    # Verify Varianta 3 exists
    v3_text = app_page.get_by_text("Varianta 3", exact=False)
    expect(v3_text.first).to_be_visible(timeout=10000)

    section = find_variant_section(app_page, 3)
    assert section is not None, "Varianta 3 not found"

    # Click Smazat
    delete_button = section.get_by_role("button", name="Smazat")
    delete_button.click()
    wait_for_app_ready(app_page)

    # Verify Varianta 3 is gone
    section = find_variant_section(app_page, 3)
    assert section is None, "Varianta 3 should be gone after removal"
