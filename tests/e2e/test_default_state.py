"""Tests for the default state of the app (no URL params)."""
from conftest import wait_for_app_ready


def test_page_title_contains_kalkulacka(app_page):
    title = app_page.title()
    assert "Kalkulačka" in title


def test_h1_heading_visible(app_page):
    h1 = app_page.locator("h1")
    h1.wait_for(state="visible", timeout=10000)
    assert "Kalkulačka refinancování hypotéky" in h1.text_content()


def test_plotly_chart_rendered(app_page):
    chart = app_page.locator('[data-testid="chart"]').first
    chart.wait_for(state="visible", timeout=10000)
    assert chart.is_visible()


def test_porovnani_scenaru_subheader(app_page):
    heading = app_page.get_by_text("Porovnání scénářů", exact=False).first
    heading.wait_for(state="visible", timeout=10000)
    assert heading.is_visible()


def test_souhrn_variant_subheader(app_page):
    heading = app_page.get_by_text("Souhrn variant", exact=False).first
    heading.wait_for(state="visible", timeout=10000)
    assert heading.is_visible()


def test_doporuceni_subheader(app_page):
    heading = app_page.get_by_text("Doporučení", exact=False).first
    heading.wait_for(state="visible", timeout=10000)
    assert heading.is_visible()


def test_summary_table_exists_with_content(app_page):
    tables = app_page.locator('[data-testid="table"]')
    tables.first.wait_for(state="visible", timeout=10000)
    assert tables.count() >= 1
    text = tables.first.text_content()
    assert len(text.strip()) > 0


def test_at_least_one_milestone_table(app_page):
    tables = app_page.locator('[data-testid="table"]')
    tables.first.wait_for(state="visible", timeout=10000)
    assert tables.count() >= 2


def test_varianta_1_section_exists(app_page):
    section = app_page.get_by_text("Varianta 1", exact=False).first
    section.wait_for(state="visible", timeout=10000)
    assert section.is_visible()


def test_varianta_2_section_exists(app_page):
    section = app_page.get_by_text("Varianta 2", exact=False).first
    section.wait_for(state="visible", timeout=10000)
    assert section.is_visible()


def test_pridat_variantu_button_exists(app_page):
    button = app_page.get_by_role("button", name="Přidat variantu")
    button.wait_for(state="visible", timeout=10000)
    assert button.is_visible()
