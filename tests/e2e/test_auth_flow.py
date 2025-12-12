import subprocess
import time
from playwright.sync_api import sync_playwright


def _start_uvicorn():
    # Start uvicorn in a subprocess; return the Popen object
    # Write uvicorn output to a temporary log to aid debugging when tests fail
    log = open('/tmp/uv_e2e.log', 'a')
    proc = subprocess.Popen(["./.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
                            stdout=log, stderr=subprocess.STDOUT)
    # wait for server to be reachable
    for i in range(60):
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


def _unique_email():
    import uuid

    return f"test+{uuid.uuid4().hex[:8]}@example.com"


def test_register_login_positive_and_negative():
    proc = _start_uvicorn()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Positive: register (should receive token and save it)
            email = _unique_email()
            import uuid as _uuid
            username_generated = f"u_{_uuid.uuid4().hex[:8]}"
            page.goto("http://127.0.0.1:8000/static/register.html")
            page.fill('#email', email)
            page.fill('#username', username_generated)
            page.fill('#password', 'strong-password')
            page.click('#register')
            # wait for either success or error message
            page.wait_for_selector('.msg.success, .msg.error', timeout=7000)
            if page.query_selector('.msg.error'):
                err_txt = page.inner_text('.msg.error')
                raise AssertionError(f"Registration UI showed error: {err_txt}")
            token_reg = page.evaluate("() => localStorage.getItem('access_token')")
            assert token_reg and len(token_reg) > 10

            # Positive: login
            page.goto("http://127.0.0.1:8000/static/login.html")
            page.fill('#username_or_email', email)
            page.fill('#password', 'strong-password')
            page.click('#login')
            # login UI shows a success message with class .msg.success
            page.wait_for_selector('.msg.success', timeout=5000)
            # ensure token stored in localStorage
            token = page.evaluate("() => localStorage.getItem('access_token')")
            assert token and len(token) > 10

            # Negative: register with short password (client-side prevents submit), but we can simulate by direct fetch
            # attempt to create via fetch with short password to get server-side 400 or validation
            bad_email = _unique_email()
            resp = page.evaluate(
                '''async (e) => {
                const r = await fetch('/users/register', {
                  method: 'POST', headers: {'Content-Type':'application/json'},
                  body: JSON.stringify({ username: 'u2', email: e, password: 'x' })
                });
                return { status: r.status, body: await r.text() };
            }''',
                bad_email,
            )
            # server should reject/return 400 or 422
            assert int(resp['status']) in (400, 422)

            # Negative: login with wrong password shows 401
            page.goto("http://127.0.0.1:8000/static/login.html")
            page.fill('#username_or_email', email)
            page.fill('#password', 'wrong-password')
            page.click('#login')
            # login error is shown as .msg.error
            page.wait_for_selector('.msg.error:has-text("Invalid credentials")', timeout=5000)

            browser.close()
    finally:
        proc.terminate()
