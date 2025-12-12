FastAPI Calculator — README
===========================

This project is a FastAPI application that supports user registration/login (JWT-based authentication) and calculation resources (create/list/read/update/delete). The repository includes unit, integration, and e2e tests (Playwright) with **94% test coverage**.

**Docker Hub Repository**

Pre-built Docker images are available at:
- 🐳 [https://hub.docker.com/repository/docker/anvith123/fastapi-calculator-user-model](https://hub.docker.com/repository/docker/anvith123/fastapi-calculator-user-model)

**Prerequisites**

- Python 3.10+ (3.11 or 3.12 recommended)
- `git` and network access to GitHub (optional)
- Optional: Docker & Docker Compose (for containerized deployment)

---

## 🚀 Running the Application

### Option 1: Local Development (Recommended)

1. **Clone the repository:**

```bash
git clone https://github.com/AnvithAnvi/Calculation-Model-with-Optional-Factory-Pattern.git
cd Calculation-Model-with-Optional-Factory-Pattern
```

2. **Create and activate a virtual environment:**

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing
```

4. **Set environment variables:**

```bash
export JWT_SECRET="your-secret-key-here"
export ACCESS_TOKEN_EXPIRE_MINUTES=60
```

5. **Start the application:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the application:**
   - API Documentation (Swagger UI): http://127.0.0.1:8000/docs
   - Alternative Docs (ReDoc): http://127.0.0.1:8000/redoc
   - Web UI: http://127.0.0.1:8000/static/login.html

### Option 2: Using Docker

1. **Pull the image from Docker Hub:**

```bash
docker pull anvith123/fastapi-calculator-user-model:latest
```

2. **Run the container:**

```bash
docker run -d \
  -p 8000:8000 \
  -e JWT_SECRET="your-secret-key-here" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=60 \
  --name fastapi-calculator \
  anvith123/fastapi-calculator-user-model:latest
```

3. **Access the application at http://localhost:8000**

### Option 3: Using Docker Compose

1. **Start the services:**

```bash
docker-compose up -d
```

2. **Stop the services:**

```bash
docker-compose down
```

---

## 🧪 Running Tests Locally

### Run All Tests

```bash
# Ensure environment variables are set
export JWT_SECRET="test-secret-key"

# Run all tests (unit + integration + e2e)
pytest -v

# Run all tests with coverage report
pytest --cov=app --cov-report=term-missing --cov-report=html
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# E2E tests only (requires Playwright)
python -m playwright install chromium  # First time only
pytest tests/e2e -v
```

### Quick Test Run (No Verbose Output)

```bash
pytest -q
```

### Coverage Report

After running tests with coverage, view the HTML report:

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open in browser (macOS)
open htmlcov/index.html

# Or on Linux
xdg-open htmlcov/index.html
```

**Current Test Coverage: 94%** (94 passing tests)

---

## 📋 Environment Variables

- `JWT_SECRET` — **Required** for JWT token creation/verification. Example:

```bash
export JWT_SECRET="replace-with-a-random-secret"
```

- `ACCESS_TOKEN_EXPIRE_MINUTES` — Optional. Default is 60 minutes. Example:

```bash
export ACCESS_TOKEN_EXPIRE_MINUTES=60
```

- `DATABASE_URL` — Optional. By default uses SQLite at `sqlite:///./tmp_test.db`. For PostgreSQL:

```bash
export DATABASE_URL="postgresql://postgres:password@localhost:5432/fastapi_db"
```

---

## 🔧 API Usage Examples

### Manual Testing with Swagger UI

1. **Start the application** (see Running the Application section)

2. **Open Swagger UI:** http://127.0.0.1:8000/docs

3. **Register a new user:**
   - Endpoint: `POST /users/`
   - Request body:

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "password123"
}
```

4. **Login:**
   - Endpoint: `POST /users/login`
   - Request body:

```json
{
  "username_or_email": "alice",
  "password": "password123"
}
```

   - Copy the `access_token` from the response

5. **Authorize in Swagger UI:**
   - Click the "Authorize" button (🔓)
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize"

6. **Create a calculation:**
   - Endpoint: `POST /calculations`
   - Request body:

```json
{
  "a": 10,
  "b": 5,
  "type": "add"
}
```

7. **List all calculations:** `GET /calculations`

8. **Get calculation by ID:** `GET /calculations/{id}`

9. **Update a calculation:** `PUT /calculations/{id}`

10. **Delete a calculation:** `DELETE /calculations/{id}`

### Available Operations

- **add** - Addition
- **subtract** - Subtraction  
- **multiply** - Multiplication
- **divide** - Division (validates against division by zero)

---

## 🗄️ Database Management

**Resetting local test database:**

```bash
rm -f test.db tmp_test.db
python reset_db.py
```

**Note:** If you encounter "readonly database" errors, remove any committed `test.db`:

```bash
git rm --cached test.db || true
echo "test.db" >> .gitignore
rm -f test.db
```

---

## 🚢 CI/CD & GitHub Actions

The repository includes automated CI/CD workflows:

- **Automated Testing:** Runs unit, integration, and e2e tests on every push
- **PostgreSQL Integration:** Tests against PostgreSQL 16 in CI environment
- **Code Coverage:** Generates coverage reports (currently 94%)
- **Docker Build:** Automatically builds and pushes images to Docker Hub

**Required Repository Secrets:**
- `JWT_SECRET` — Required for JWT-based tests
- `DOCKERHUB_USERNAME` — For pushing Docker images
- `DOCKERHUB_TOKEN` — Docker Hub access token

---

## 📦 Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application & endpoints
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database configuration
│   ├── security.py             # JWT authentication
│   ├── operations.py           # Calculation operations
│   ├── calculation_factory.py # Factory pattern implementation
│   ├── stats.py                # Statistics utilities
│   └── logger_config.py        # Logging configuration
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end Playwright tests
├── static/                     # Frontend HTML/CSS/JS
├── .github/workflows/          # GitHub Actions CI/CD
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker build instructions
└── README.md                   # This file
```

---

## 🔍 Troubleshooting

**"No such table" errors:**
- Ensure `DATABASE_URL` is set correctly before starting the app
- Clear the database: `rm -f test.db tmp_test.db && python reset_db.py`

**"Readonly database" errors:**
- Remove committed test.db: `git rm --cached test.db && rm -f test.db`
- Add to .gitignore: `echo "test.db" >> .gitignore`

**E2E tests failing:**
- Install Playwright browsers: `python -m playwright install chromium`
- Ensure port 8000 is not in use: `lsof -i :8000`

**Import errors:**
- Verify virtual environment is activated: `which python`
- Reinstall dependencies: `pip install -r requirements.txt -r requirements-dev.txt`

---

## 📊 Test Coverage

Current coverage: **94%** with **94 passing tests**

**100% Coverage:**
- calculation_factory.py
- models.py
- operations.py
- schemas.py
- stats.py
- logger_config.py

**High Coverage:**
- main.py: 93%
- security.py: 97%
- database.py: 80%

---

## 📝 Quick Command Reference

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Environment
export JWT_SECRET="your-secret-key"
export ACCESS_TOKEN_EXPIRE_MINUTES=60

# Run Application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
pytest -v                                                    # All tests
pytest tests/unit -v                                         # Unit tests only
pytest tests/integration -v                                  # Integration tests only
pytest tests/e2e -v                                          # E2E tests only
pytest --cov=app --cov-report=term-missing --cov-report=html # With coverage

# Docker
docker pull anvith123/fastapi-calculator-user-model:latest
docker run -d -p 8000:8000 -e JWT_SECRET="secret" anvith123/fastapi-calculator-user-model:latest
docker-compose up -d

# Database
python reset_db.py                                           # Reset database
rm -f test.db tmp_test.db                                    # Clean test databases
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Ensure tests pass: `pytest -v`
5. Commit your changes: `git commit -m "Add your feature"`
6. Push to the branch: `git push origin feature/your-feature`
7. Create a Pull Request

---

## 🔗 Links

- **Docker Hub:** https://hub.docker.com/repository/docker/anvith123/fastapi-calculator-user-model
- **GitHub Repository:** https://github.com/AnvithAnvi/Calculation-Model-with-Optional-Factory-Pattern
- **API Documentation:** http://localhost:8000/docs (when running locally)

