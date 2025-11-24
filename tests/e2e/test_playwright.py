import pytest
from playwright.sync_api import sync_playwright

def test_swagger_ui_loads():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000/docs")
        assert "Swagger UI" in page.content()
        browser.close()
