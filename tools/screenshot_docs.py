from playwright.sync_api import sync_playwright
from pathlib import Path

output = Path("screenshots")
output.mkdir(parents=True, exist_ok=True)

url = "http://127.0.0.1:8000/docs"

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto(url)
    # wait for the docs main element
    try:
        page.wait_for_selector('div.swagger-ui', timeout=10000)
    except Exception:
        # fallback small wait
        page.wait_for_timeout(2000)
    path = output / "swagger.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"Saved screenshot to: {path}")
    browser.close()
