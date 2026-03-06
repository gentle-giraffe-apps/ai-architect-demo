# Example System Spec

This is a concrete example of a spec that could drive an AI agent loop. It's the kind of artifact an engineer places in a repo to define a unit of work.

---

## Goal

Build a URL shortener API with persistent storage, input validation, and analytics tracking.

## Scope

Create a Python Flask application with the following endpoints:

- `POST /shorten` — accepts a URL, returns a short code
- `GET /<code>` — redirects to the original URL
- `GET /stats/<code>` — returns click count and creation timestamp

## File Targets

```
src/
  app.py          # Flask application and route handlers
  models.py       # SQLite database models and queries
  validators.py   # URL validation logic
  analytics.py    # Click tracking and stats
tests/
  test_shorten.py    # Tests for URL shortening
  test_redirect.py   # Tests for redirect behavior
  test_stats.py      # Tests for analytics endpoint
  test_validators.py # Tests for input validation
requirements.txt     # Project dependencies
```

## Constraints

- Use SQLite for storage (no external database required)
- Use only packages available via pip
- Short codes must be URL-safe and at least 6 characters
- Reject URLs that are not valid HTTP/HTTPS
- Return appropriate HTTP status codes (201, 301, 404, 422)
- No authentication required for this version

## Quality Gates

- All tests pass with `pytest`
- No test uses mocking for database calls — use a real test database
- Every endpoint has at least two test cases (happy path + error case)
- Input validation rejects malformed URLs with a clear error message

## Completion Criteria

- All files in the file targets list exist
- `pytest` runs with 0 failures
- Each endpoint behaves as described in the scope
- Code is clean enough to read without comments explaining the obvious
- No TODO or placeholder comments remain
