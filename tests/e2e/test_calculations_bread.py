import subprocess
import sys
import time
import json
from playwright.sync_api import sync_playwright


def _start_uvicorn():
    log = open('/tmp/uv_e2e.log', 'a')
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
                            stdout=log, stderr=subprocess.STDOUT)
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


def test_calculations_bread_positive_and_negative():
    proc = _start_uvicorn()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            # ensure page has same-origin so fetch() works reliably
            # Retry goto a few times to tolerate transient connection races
            for _ in range(8):
                try:
                    page.goto('http://127.0.0.1:8000/docs')
                    break
                except Exception:
                    import time as _t
                    _t.sleep(0.25)
            else:
                # last attempt (let exception bubble)
                page.goto('http://127.0.0.1:8000/docs')

            # Register via API and obtain token
            email = _unique_email()
            username = email.split('@')[0]
            res = page.evaluate(
                "async (data) => { const r = await fetch('http://127.0.0.1:8000/users/register',{method:'POST',headers:{'Content-Type':'application/json'}, body: JSON.stringify({username:data.username,email:data.email,password:'strong-pass'} )}); return {status: r.status, body: await r.json()}; }",
                {"email": email, "username": username},
            )
            assert int(res['status']) in (200,201,201)
            token = res['body'].get('access_token')
            assert token and len(token) > 10

            # Set token in localStorage so our page helper can use it
            page.evaluate("t => localStorage.setItem('access_token', t)", token)

            # Positive: create a calculation
            create = page.evaluate(
                "async () => { const r = await fetch('http://127.0.0.1:8000/calculations', {method:'POST', headers:{'Content-Type':'application/json','Authorization': 'Bearer '+localStorage.getItem('access_token')}, body: JSON.stringify({a:4,b:2,type:'add'})}); return {status: r.status, body: await r.json()}; }"
            )
            assert create['status'] == 201
            calc = create['body']
            calc_id = calc['id']
            assert calc['result'] == 6

            # create modulus
            create_mod = page.evaluate(
                "async () => { const r = await fetch('http://127.0.0.1:8000/calculations', {method:'POST', headers:{'Content-Type':'application/json','Authorization': 'Bearer '+localStorage.getItem('access_token')}, body: JSON.stringify({a:10,b:3,type:'modulus'})}); return {status: r.status, body: await r.json()}; }"
            )
            assert create_mod['status'] == 201
            assert create_mod['body']['result'] == 1

            # create exponent
            create_pow = page.evaluate(
                "async () => { const r = await fetch('http://127.0.0.1:8000/calculations', {method:'POST', headers:{'Content-Type':'application/json','Authorization': 'Bearer '+localStorage.getItem('access_token')}, body: JSON.stringify({a:2,b:5,type:'exponent'})}); return {status: r.status, body: await r.json()}; }"
            )
            assert create_pow['status'] == 201
            assert create_pow['body']['result'] == 32

            # fetch stats and verify counts include operations we created
            stats = page.evaluate("async () => { const r = await fetch('http://127.0.0.1:8000/calculations/stats', {headers:{'Authorization': 'Bearer '+localStorage.getItem('access_token')}}); return {status: r.status, body: await r.json()}; }")
            assert stats['status'] == 200
            assert stats['body']['total'] >= 3
            assert stats['body']['counts'].get('exponent', 0) >= 1

            # Browse list
            listing = page.evaluate("async () => { const r = await fetch('http://127.0.0.1:8000/calculations', {headers:{'Authorization': 'Bearer '+localStorage.getItem('access_token')}}); return {status: r.status, body: await r.json()}; }")
            assert listing['status'] == 200
            assert any(item['id'] == calc_id for item in listing['body'])

            # Read specific
            detail = page.evaluate("async (id) => { const r = await fetch('http://127.0.0.1:8000/calculations/'+id, {headers:{'Authorization': 'Bearer '+localStorage.getItem('access_token')}}); return {status: r.status, body: await r.json()}; }", calc_id)
            assert detail['status'] == 200
            assert detail['body']['id'] == calc_id

            # Update (PUT)
            upd = page.evaluate("async (id) => { const r = await fetch('http://127.0.0.1:8000/calculations/'+id, {method:'PUT', headers:{'Content-Type':'application/json','Authorization': 'Bearer '+localStorage.getItem('access_token')}, body: JSON.stringify({a:10,b:5,type:'subtract'})}); return {status: r.status, body: await r.json()}; }", calc_id)
            assert upd['status'] == 200
            assert abs(upd['body']['result'] - 5) < 1e-9

            # Negative: create with invalid input (divide by zero)
            bad = page.evaluate("async () => { const r = await fetch('http://127.0.0.1:8000/calculations', {method:'POST', headers:{'Content-Type':'application/json','Authorization': 'Bearer '+localStorage.getItem('access_token')}, body: JSON.stringify({a:1,b:0,type:'divide'})}); return {status: r.status, text: await r.text()}; }")
            assert int(bad['status']) in (400,422)

            # Unauthorized access: new page without token
            page.evaluate("() => localStorage.removeItem('access_token')")
            unauth = page.evaluate("async () => { const r = await fetch('http://127.0.0.1:8000/calculations'); return {status: r.status, text: await r.text()}; }")
            assert int(unauth['status']) == 401

            # Re-set token and delete the created calculation
            page.evaluate("t => localStorage.setItem('access_token', t)", token)
            dele = page.evaluate("async (id) => { const r = await fetch('http://127.0.0.1:8000/calculations/'+id, {method:'DELETE', headers:{'Authorization': 'Bearer '+localStorage.getItem('access_token')}}); return {status: r.status, text: await r.text()}; }", calc_id)
            assert int(dele['status']) in (200,204)

            browser.close()
    finally:
        proc.terminate()
