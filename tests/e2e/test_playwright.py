import subprocess
import time
from playwright.sync_api import sync_playwright


def _start_uvicorn():
    # Start uvicorn in a subprocess; return the Popen object
    proc = subprocess.Popen(["./.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # wait for server to be reachable
    for i in range(30):
        try:
            import requests

            r = requests.get("http://127.0.0.1:8000/docs", timeout=1)
            if r.status_code == 200:
                return proc
        except Exception:
            pass
        time.sleep(0.2)
    # If not up, kill process and raise
    proc.kill()
    raise RuntimeError("uvicorn did not start in time")


def test_swagger_ui_loads():
    proc = _start_uvicorn()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("http://127.0.0.1:8000/docs")
            assert "Swagger UI" in page.content()
            browser.close()
    finally:
        proc.terminate()
