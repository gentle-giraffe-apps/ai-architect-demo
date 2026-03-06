# CLAUDE.md — Example AI Operating Instructions

This is an example of a `CLAUDE.md` file that acts as architecture for an AI coding agent. Place this in the root of a repository to define how AI agents should behave when working on the project.

---

## Project Purpose

This is a production API service for internal tools. Reliability and clarity matter more than speed of delivery. When in doubt, choose the simpler approach.

## Coding Standards

- Python 3.11+
- Use type hints on all function signatures
- Use `pathlib` instead of `os.path`
- Prefer standard library over third-party packages when the functionality is equivalent
- Keep functions focused — one function, one job
- Name variables and functions clearly enough that comments are rarely needed
- No wildcard imports
- No mutable default arguments

## Testing Expectations

- Write tests before implementation when building new features
- Use `pytest` as the test runner
- Every public function must have at least one test
- Test both the happy path and at least one failure case
- Use real dependencies (SQLite, filesystem) in tests — avoid mocks unless testing external API calls
- Tests must pass before any commit

## File Organization

```
src/           Application source code
tests/         All test files, mirroring src/ structure
docs/          Documentation if needed
requirements.txt  Pinned dependencies
```

Do not create files outside this structure without explicit instruction.

## Git and Commit Behavior

- Create small, focused commits
- Write commit messages that explain why, not what
- Never commit to `main` directly — use feature branches
- Never force-push
- Never commit `.env`, credentials, or API keys
- Run tests before committing — do not commit if tests fail

## Safety Rules

- Never read or write `.env` files or anything in `secrets/`
- Never make network requests unless the task explicitly requires it
- Never install packages without confirming they're in `requirements.txt`
- Never delete files unless the task explicitly asks for it
- If something seems wrong or ambiguous, stop and ask rather than guessing

## How to Know When a Task Is Complete

A task is complete when all of the following are true:

1. All files specified in the task exist and contain meaningful content
2. All tests pass with `pytest`
3. No TODO, FIXME, or placeholder comments remain in the code
4. The code is clean enough to review without explanation
5. The commit history tells a clear story of what was done and why

If any of these conditions are not met, the task is not done.
