FastAPI Calculator — README
===========================

This project is a small FastAPI application that supports user registration/login (JWT-based authentication) and calculation resources (create/list/read/update/delete). The repository includes unit, integration, and e2e tests (Playwright).

This README focuses on how to run the integration tests locally and how to perform manual checks using the OpenAPI (Swagger) UI.

**Prerequisites**

- Python 3.10+ (3.11 recommended)
- `git` and network access to GitHub (optional)
- Optional: Docker & Docker Compose (only if you want to run Postgres or CI-like environment locally)

**Quick setup (recommended)**

- Create and activate a virtual environment (macOS `zsh` example):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Environment variables**

- `JWT_SECRET` — required for JWT token creation/verification. Export a value before running tests or starting the server. Example for local testing:

```bash
export JWT_SECRET="replace-with-a-random-secret"
export ACCESS_TOKEN_EXPIRE_MINUTES=60
```

- `DATABASE_URL` — optional. By default the tests (and `conftest.py`) will use a file-backed SQLite DB at `sqlite:///./test.db` for integration tests. To point to a Postgres instance or other DB, set `DATABASE_URL` appropriately (example for Postgres):

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/fastapi_test"
```

Note: On CI, the workflow sets `DATABASE_URL` to the service Postgres instance.

**Resetting local test DB**

If you need to remove the file-backed test DB and start fresh:

```bash
rm -f test.db
python reset_db.py
```

`conftest.py` also attempts to remove `test.db` at session start to avoid stale schemas.

**Run integration tests**

- Run only integration tests (recommended when iterating on API changes):

```bash
# Ensure environment variables are set
export JWT_SECRET="replace-with-a-random-secret"
# Run integration tests
pytest tests/integration -q
```

- Run the full test suite (unit + integration + e2e):

```bash
pytest -q
```

Notes:
- Integration tests use the configured `DATABASE_URL` (or the default `sqlite:///./test.db` from `conftest.py`).
- Tests create unique users where necessary to avoid collisions.

**Start the app and use OpenAPI (manual checks)**

1. Start the FastAPI server with `uvicorn` (from project root):

```bash
# With virtualenv active
export JWT_SECRET="replace-with-a-random-secret"
uvicorn app.main:app --reload
```

By default the app will be available at `http://127.0.0.1:8000`.

2. Open the interactive docs (OpenAPI / Swagger UI):

- Visit: `http://127.0.0.1:8000/docs`
- The ReDoc documentation is at: `http://127.0.0.1:8000/redoc`

3. Typical manual flow using the OpenAPI UI

- Register a user: `POST /users/register`
  - Request body example (JSON):

```json
{
  "username": "alice",
  "password": "s3cret"
}
```

- Login: `POST /users/login`
  - Request body example (JSON):

```json
{
  "username": "alice",
  "password": "s3cret"
}
```

  - Response contains a JWT access token, e.g. `{"access_token": "<token>", "token_type": "bearer"}`.

- Authorize the OpenAPI UI:
  - Click the "Authorize" button in Swagger UI.
  - Enter `Bearer <token>` (where `<token>` is the `access_token` value from login).
  - After authorizing, subsequent requests from the Swagger UI will include the token.

- Create a calculation: `POST /calculations`
  - Request body example (JSON):

```json
{
  "a": 10,
  "b": 5,
  "type": "add"
}
```

- List calculations: `GET /calculations`
- Read a calculation: `GET /calculations/{id}`
- Update a calculation: `PUT /calculations/{id}` (body similar to create)
- Delete a calculation: `DELETE /calculations/{id}`

The application also exposes legacy endpoints for single operations (may accept optional authentication), but the `/calculations` endpoints provide full CRUD.

**Division-by-zero validation**

The API prevents division-by-zero at validation time. Attempting to create a calculation with `type: "divide"` and `b: 0` will return a validation error (HTTP 422).

**Debugging tips**

- If you see errors about missing tables during tests or server start, ensure that `DATABASE_URL` is set before the app imports (the tests rely on `conftest.py` to set defaults) and that `test.db` isn't stale.
- To clear local test DB state: `rm -f test.db` then re-run tests or `python reset_db.py`.

**CI / GitHub Actions**

- The repository includes a CI workflow that runs unit and integration tests and an e2e job that starts `uvicorn` and runs Playwright tests.
- For the CI to fully run and push Docker images you must add repository secrets:
  - `JWT_SECRET` — required for JWT-based tests.
  - `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` — required for the `build_and_push` job to publish images.

**Useful commands summary**

```bash
# create + activate virtualenv
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# export JWT secret
export JWT_SECRET="replace-with-a-random-secret"

# run integration tests
pytest tests/integration -q

# run full tests
pytest -q

# start server for manual OpenAPI checks
uvicorn app.main:app --reload
```

**Contact / Next steps**

If you'd like, I can:
- Add a short `make` or `invoke` task to automate these commands.
- Add a `.env.example` with recommended env values.
- Remove `test.db` from the repo and add it to `.gitignore` (recommended for cleanliness).

-----

Generated on: December 1, 2025
