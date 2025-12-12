import time
import subprocess
from playwright.sync_api import sync_playwright


def _start_uvicorn():
    log = open('/tmp/uv_e2e.log', 'a')
    proc = subprocess.Popen(["./.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"], stdout=log, stderr=subprocess.STDOUT)
    for i in range(60):
        try:
            import requests
            r = requests.get("http://127.0.0.1:8000/docs", timeout=1)
            if r.status_code == 200:
                return proc
        except Exception:
            pass
        time.sleep(0.2)
    proc.kill()
    raise RuntimeError("uvicorn did not start in time")


def _unique_email():
    import uuid
    return f"test+{uuid.uuid4().hex[:8]}@example.com"


def test_profile_update_and_password_change():
    proc = _start_uvicorn()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            email = _unique_email()
            username = email.split('@')[0]

            # wait for server and register
            for _ in range(8):
                try:
                    page.goto('http://127.0.0.1:8000/static/register.html')
                    break
                except Exception:
                    import time as _t
                    _t.sleep(0.25)
            else:
                page.goto('http://127.0.0.1:8000/static/register.html')
            page.fill('#email', email)
            page.fill('#username', username)
            page.fill('#password', 'strong-password')
            page.click('#register')
            page.wait_for_selector('.msg.success', timeout=5000)
            token = page.evaluate("() => localStorage.getItem('access_token')")
            assert token

            # go to profile
            page.goto('http://127.0.0.1:8000/static/profile.html')
            page.wait_for_selector('#username')
            # update username
            new_username = username + '_x'
            page.fill('#username', new_username)
            page.fill('#email', email)
            page.click('#save')
            page.wait_for_selector('.msg.success', timeout=5000)

            # change password
            page.fill('#current_password', 'strong-password')
            page.fill('#new_password', 'even-stronger')
            page.click('#changePassword')
            page.wait_for_selector('.msg.success', timeout=5000)

            # after password change, wait a bit for potential redirect
            import time as _time
            _time.sleep(2)
            
            # Navigate to login if not already there (redirect may have happened)
            if not page.url.endswith('/static/login.html'):
                page.goto('http://127.0.0.1:8000/static/login.html')

            # login with old password should fail
            page.fill('#username_or_email', email)
            page.fill('#password', 'strong-password')
            page.click('#login')
            page.wait_for_selector('.msg.error', timeout=5000)

            # login with new password should succeed
            page.fill('#username_or_email', email)
            page.fill('#password', 'even-stronger')
            page.click('#login')
            page.wait_for_selector('.msg.success', timeout=5000)

            browser.close()
    finally:
        proc.terminate()
