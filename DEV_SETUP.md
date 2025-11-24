Developer setup and running tests

1) Create and activate a virtual environment (macOS / zsh):

```zsh
python3 -m venv .venv
source .venv/bin/activate
```

2) Install project dependencies and dev/test dependencies:

```zsh
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3) Install Playwright browsers (required if tests use Playwright):

```zsh
python -m playwright install
```

4) Run the test suite:

```zsh
pytest -q
```

If pytest is not found in your shell after activation, ensure the venv is activated and that `pip` installs to the same Python interpreter (`python -m pip install ...`).
