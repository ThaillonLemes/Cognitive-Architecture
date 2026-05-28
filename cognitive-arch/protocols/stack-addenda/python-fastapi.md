# Stack addendum: Python / FastAPI

BRIEF: Convention overlay for Python + FastAPI projects using the cognitive architecture. Read after PROTOCOLS.md and RETROFIT.md/BOOTSTRAP.md. Overrides and supplements generic conventions where Python specifics apply.

as_of: 2026-05-22
applies_to: Python 3.9+, FastAPI (any version)

---

## 1. Setup

```bash
# Create virtual environment (always)
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# If using cognitive-arch SDK
pip install -r cognitive-arch/sdk/requirements.txt
```

Add to `PROJECT.md` frontmatter:
```yaml
build_cmd: "N/A"
test_cmd: "pytest"
lint_cmd: "ruff check ."
```

---

## 2. Naming conventions

| Item | Convention | Example |
|------|-----------|---------|
| Module files | `snake_case.py` | `user_service.py` |
| Classes | `PascalCase` | `UserService` |
| Functions / variables | `snake_case` | `get_current_user` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| FastAPI routers | `router.py` in feature folder | `auth/router.py` |
| Pydantic models | Separate `schemas.py` per feature | `auth/schemas.py` |
| DB models | `models.py` per feature | `auth/models.py` |
| Tests | `test_<module>.py` | `test_user_service.py` |
| Fixtures | `conftest.py` at relevant scope | |

---

## 3. Project structure

```
src/
  app/
    main.py            # FastAPI app factory
    config.py          # Settings (pydantic BaseSettings)
    database.py        # DB engine / session
    <feature>/
      router.py        # APIRouter for this feature
      schemas.py       # Pydantic request/response models
      models.py        # SQLAlchemy (or other ORM) models
      service.py       # Business logic
      dependencies.py  # FastAPI Depends() functions
tests/
  conftest.py
  <feature>/
    test_router.py
    test_service.py
cognitive-arch/        # Architecture scaffold
requirements.txt
pyproject.toml (or setup.cfg)
.env.example
```

---

## 4. Test command

```bash
pytest                          # run all tests
pytest -x                       # stop on first failure
pytest tests/auth/              # run a feature
pytest --cov=src --cov-report=term-missing  # with coverage
```

Set in `PROJECT.md`: `test_cmd: "pytest"`

---

## 5. Lint command

```bash
ruff check .                    # lint
ruff format .                   # format (replaces black)
```

Set in `PROJECT.md`: `lint_cmd: "ruff check ."`

---

## 6. HOT file additions for FastAPI projects

Add to `INDEX.md` WARM section:

| File | Brief |
|------|-------|
| `src/app/main.py` | FastAPI app factory; lifespan, routers, middleware |
| `src/app/config.py` | Pydantic settings; reads .env |
| `src/app/database.py` | DB engine + session dependency |
| `requirements.txt` | Runtime dependencies |
| `.env.example` | Required env vars with example values |

---

## 7. Code header example (Python)

```python
# PURPOSE: <what this module does in one sentence>
# INPUTS:  <main inputs — request models, DB session, etc.>
# OUTPUTS: <main outputs — response models, side effects>
# DEPS:    <key dependencies — SQLAlchemy, Redis, etc.>
# SEE:     design/<relevant-doc>.md
```

---

## 8. FastAPI-specific cognitive-arch notes

- `[code-only]` axioms (P1, C1–C6) apply to all `.py` files; Q-axioms apply to architecture decisions
- `design/api-contracts.md` is the natural home for endpoint specs and request/response schemas
- `design/domain-entities.md` maps to Pydantic + ORM model design
- Block manifests that touch multiple features should be Tier M or L (not Tier S)

End of python-fastapi addendum.
