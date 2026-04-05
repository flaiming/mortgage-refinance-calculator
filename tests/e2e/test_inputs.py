"""Tests for input interactions in the Streamlit app."""
from conftest import wait_for_app_ready, set_number_input, get_segmented_button


def _get_summary_table_text(page):
    table = page.locator('[data-testid="stTable"]').first
    table.wait_for(state="visible", timeout=10000)
    return table.text_content()


def test_change_delka_splaceni(app_page):
    summary_before = _get_summary_table_text(app_page)
    set_number_input(app_page, "Délka splácení", 25)
    summary_after = _get_summary_table_text(app_page)
    assert summary_after != summary_before


def test_change_urok(app_page):
    summary_before = _get_summary_table_text(app_page)
    set_number_input(app_page, "Úrok [%]", 3.5)
    summary_after = _get_summary_table_text(app_page)
    assert summary_after != summary_before


def test_change_investment_strategy(app_page):
    summary_before = _get_summary_table_text(app_page)
    # Open the Strategie selectbox
    selectbox = app_page.locator('[data-testid="stSelectbox"]', has_text="Strategie")
    selectbox.first.click()
    # Pick "Dynamická (8 % ročně)" from the dropdown
    option = app_page.locator('[role="option"]', has_text="Dynamická")
    option.first.click()
    wait_for_app_ready(app_page)
    summary_after = _get_summary_table_text(app_page)
    assert summary_after != summary_before


def test_toggle_nominalne_realne(app_page):
    summary_before = _get_summary_table_text(app_page)
    realne_btn = get_segmented_button(app_page, "Reálně")
    realne_btn.click()
    wait_for_app_ready(app_page)
    summary_after = _get_summary_table_text(app_page)
    assert summary_after != summary_before


def test_change_varianta2_novy_urok(app_page):
    summary_before = _get_summary_table_text(app_page)
    # Find all "Nový úrok" number inputs — second one is Varianta 2
    number_inputs = app_page.locator('[data-testid="stNumberInput"]')
    novy_urok_inputs = []
    for i in range(number_inputs.count()):
        ni = number_inputs.nth(i)
        if "Nový úrok" in (ni.text_content() or ""):
            novy_urok_inputs.append(ni)
    assert len(novy_urok_inputs) >= 2
    input_el = novy_urok_inputs[1].locator("input").first
    input_el.fill("5.5")
    input_el.press("Enter")
    wait_for_app_ready(app_page)
    summary_after = _get_summary_table_text(app_page)
    assert summary_after != summary_before
