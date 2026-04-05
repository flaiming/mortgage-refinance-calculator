"""E2E tests for Nominálně/Reálně display mode switching."""
from playwright.sync_api import expect
from conftest import wait_for_app_ready, set_number_input, get_segmented_button, get_number_input


def _get_table_text(page):
    table = page.locator("[data-testid='table']").first
    table.wait_for(state="visible", timeout=10000)
    return table.text_content()


def test_default_is_nominal(app_page):
    # Active segmented button has data-testid "segmented-button-active"
    active_btn = app_page.locator('[data-testid="segmented-button-active"]').first
    assert "Nominálně" in active_btn.text_content()


def test_switch_to_real(app_page):
    nominal_table_text = _get_table_text(app_page)

    # Verify inflation input is disabled in nominal mode
    inflation_input = get_number_input(app_page, "Roční inflace")
    expect(inflation_input).to_be_disabled()

    # Click "Reálně"
    realne_btn = get_segmented_button(app_page, "Reálně")
    realne_btn.click()
    wait_for_app_ready(app_page)

    # Verify inflation input is now enabled
    inflation_input = get_number_input(app_page, "Roční inflace")
    expect(inflation_input).to_be_enabled()

    # Verify Reálně is now the active button
    active_btn = app_page.locator('[data-testid="segmented-button-active"]').first
    assert "Reálně" in active_btn.text_content()

    # Verify table values changed
    real_table_text = _get_table_text(app_page)
    assert real_table_text != nominal_table_text


def test_inflation_change_affects_values(app_page):
    # Switch to Reálně first
    realne_btn = get_segmented_button(app_page, "Reálně")
    realne_btn.click()
    wait_for_app_ready(app_page)

    table_at_default_inflation = _get_table_text(app_page)

    # Change inflation to 5.0
    set_number_input(app_page, "Roční inflace", 5.0)

    table_at_high_inflation = _get_table_text(app_page)
    assert table_at_high_inflation != table_at_default_inflation
