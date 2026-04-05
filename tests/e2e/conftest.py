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
def streamlit_server():
    port = _free_port()
    proc = subprocess.Popen(
        [
            "streamlit", "run", "main.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ],
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
def app_page(page, streamlit_server):
    """Navigate to the app and wait for it to load."""
    page.goto(streamlit_server)
    page.wait_for_selector("h1", timeout=15000)
    wait_for_app_ready(page)
    return page


def wait_for_app_ready(page, timeout=15000):
    """Wait for Streamlit to finish running — wait for status widget to appear then disappear."""
    try:
        # First try to wait for the running indicator to appear
        page.wait_for_selector(
            '[data-testid="stStatusWidget"]', state="visible", timeout=2000
        )
    except Exception:
        pass
    try:
        # Then wait for it to disappear
        page.wait_for_selector(
            '[data-testid="stStatusWidget"]', state="hidden", timeout=timeout
        )
    except Exception:
        pass
    # Small extra buffer for DOM to settle
    page.wait_for_timeout(500)


def set_number_input(page, label_text, value):
    """Find a number_input by its label and set a value."""
    label = page.locator('[data-testid="stWidgetLabel"]', has_text=label_text).first
    container = label.locator("xpath=ancestor::div[@data-testid='stNumberInput']").first
    input_el = container.locator("input").first
    input_el.fill(str(value))
    input_el.press("Enter")
    wait_for_app_ready(page)


def get_number_input(page, label_text):
    """Find a number_input element by its label and return the input element."""
    label = page.locator('[data-testid="stWidgetLabel"]', has_text=label_text).first
    container = label.locator("xpath=ancestor::div[@data-testid='stNumberInput']").first
    return container.locator("input").first


def get_table_texts(page):
    """Get text content of all tables."""
    tables = page.locator('[data-testid="stTable"]')
    return [tables.nth(i).text_content() for i in range(tables.count())]


def find_variant_section(page, variant_number):
    """Find the bordered container for a specific variant.

    Returns the most specific wrapper that contains 'Varianta N' and 'Nový úrok'
    but does NOT contain other variants (to avoid matching parent containers).
    """
    wrappers = page.locator('[data-testid="stVerticalBlockBorderWrapper"]')
    for i in range(wrappers.count()):
        w = wrappers.nth(i)
        text = w.text_content() or ""
        if f"Varianta {variant_number}" not in text:
            continue
        if "Nový úrok" not in text:
            continue
        # Skip parent containers that contain multiple variants
        other_variants = False
        for other in range(1, 20):
            if other == variant_number:
                continue
            if f"Varianta {other}" in text and "Nový úrok" in text.split(f"Varianta {other}")[0].split(f"Varianta {variant_number}")[-1] if f"Varianta {other}" in text else False:
                other_variants = True
                break
        # Simpler check: count how many "Varianta" headings are in this wrapper
        import re
        variant_headings = re.findall(r"Varianta \d+", text)
        unique_variants = set(variant_headings)
        if len(unique_variants) == 1:
            return w
    return None


def get_segmented_button(page, label_text):
    """Find a segmented control button by text."""
    return page.locator(
        '[data-testid="stBaseButton-segmented_control"], '
        '[data-testid="stBaseButton-segmented_controlActive"]',
        has_text=label_text,
    ).first
