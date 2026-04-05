import pytest
import subprocess
import time
import socket
import urllib.request


def _free_port():
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def app_server():
    port = _free_port()
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "api.app:app", "--port", str(port)],
        cwd="/home/flaim/www/EngetoHackathon",
    )
    url = f"http://localhost:{port}"
    for _ in range(30):
        try:
            urllib.request.urlopen(url, timeout=1)
            break
        except Exception:
            time.sleep(1)
    yield url
    proc.terminate()
    proc.wait()


@pytest.fixture
def app_page(page, app_server):
    """Navigate to the app and wait for it to load."""
    page.goto(app_server)
    page.wait_for_selector("h1", timeout=15000)
    wait_for_app_ready(page)
    return page


def wait_for_app_ready(page, timeout=15000):
    """Wait for the app to finish loading — wait for loading indicator to appear then disappear."""
    try:
        # First try to wait for the loading indicator to appear
        page.wait_for_selector(
            '[data-testid="loading-indicator"]', state="visible", timeout=2000
        )
    except Exception:
        pass
    try:
        # Then wait for it to disappear
        page.wait_for_selector(
            '[data-testid="loading-indicator"]', state="hidden", timeout=timeout
        )
    except Exception:
        pass
    # Small extra buffer for DOM to settle
    page.wait_for_timeout(500)


def set_number_input(page, label_text, value):
    """Find a number_input by its label and set a value."""
    label = page.locator('label', has_text=label_text).first
    container = label.locator("xpath=ancestor::div[@data-testid='number-input']").first
    input_el = container.locator("input").first
    input_el.fill(str(value))
    input_el.press("Enter")
    wait_for_app_ready(page)


def get_number_input(page, label_text):
    """Find a number_input element by its label and return the input element."""
    label = page.locator('label', has_text=label_text).first
    container = label.locator("xpath=ancestor::div[@data-testid='number-input']").first
    return container.locator("input").first


def get_table_texts(page):
    """Get text content of all tables."""
    tables = page.locator('[data-testid="table"]')
    return [tables.nth(i).text_content() for i in range(tables.count())]


def find_variant_section(page, variant_number):
    """Find the variant-card container for a specific variant.

    Each variant-card wraps exactly ONE variant, so just find the card containing "Varianta N".
    """
    cards = page.locator('[data-testid="variant-card"]')
    for i in range(cards.count()):
        card = cards.nth(i)
        text = card.text_content() or ""
        if f"Varianta {variant_number}" in text:
            return card
    return None


def get_segmented_button(page, label_text):
    """Find a segmented control button by text."""
    return page.locator(
        '[data-testid="segmented-button"], '
        '[data-testid="segmented-button-active"]',
        has_text=label_text,
    ).first
