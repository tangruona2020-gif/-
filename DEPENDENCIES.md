# Dependency inventory

All selected versions are exact. No dependency has been installed as part of
this review.

## Runtime dependencies

| Package | Version | Purpose |
|---|---:|---|
| Alembic | 1.16.4 | Versioned SQLAlchemy database migrations. |
| Beautiful Soup 4 | 4.13.4 | Defensive HTML parsing for site adapters and fixtures. |
| FastAPI | 0.116.1 | HTTP API and administrative web application. |
| HTTPX | 0.28.1 | Timeout-aware asynchronous HTTP client. |
| Jinja2 | 3.1.6 | Server-rendered administration templates. |
| Pillow | 11.3.0 | Image validation, dimensions and format detection. |
| Playwright | 1.54.0 | Optional browser fallback for JavaScript-rendered pages. Its Chromium binary is a separate, approval-gated download. |
| Pydantic Settings | 2.10.1 | Typed `.env` and application configuration. |
| python-dateutil | 2.9.0.post0 | Date parsing where strict site-specific parsing is insufficient. |
| python-multipart | 0.0.20 | FastAPI HTML form decoding. |
| SQLAlchemy | 2.0.42 | ORM, sessions and SQLite persistence. |
| Tenacity | 9.1.2 | Bounded retry with exponential backoff. |
| Uvicorn | 0.35.0 | Local ASGI development server. |

## Development dependencies

| Package | Version | Purpose |
|---|---:|---|
| mypy | 1.17.1 | Static type checking. |
| pre-commit | 4.2.0 | Optional local quality hooks; installing hooks remains a separate manual action. |
| pytest | 8.4.1 | Unit and fixture-based test runner. |
| pytest-asyncio | 1.1.0 | Async scan/service tests. |
| Ruff | 0.12.7 | Linting and formatting checks. |

## Build dependency

| Package | Version | Purpose |
|---|---:|---|
| setuptools | 80.9.0 | Builds the local editable project. Pinning it prevents pip from resolving an unconstrained build backend. |

## Transitive dependency policy

Indirect packages are not project choices until the resolver produces
`uv.lock`. Likely families include Pydantic Core, Starlette, AnyIO, HTTP Core,
Greenlet, Mako, MarkupSafe and testing-tool dependencies, but their versions
must come from the reviewed resolver output rather than manual guesses.
