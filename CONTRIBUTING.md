# Contributing

Install development dependencies using `uv sync --frozen --extra dev` or
`python -m pip install -e ".[dev]"`. Use Python 3.11+ with Tcl/Tk installed.

- Keep widgets and layout in `src/gencook/ui/`.
- Keep API calls, response parsing, and speech in `src/gencook/backend/`.
- Inject services into the window so UI tests need no network access or voices.
- Read configuration through `config.py`. Never commit API keys or `.env` files.
- Add regression tests for changed behavior. Stub all paid external services.
- Declare dependencies in `pyproject.toml`; run `uv lock` and commit `uv.lock`
  when changing dependency requirements.

Before submitting a change:

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
python -m build
```

Use `python -m ruff format .` to apply formatting. Describe what changed, why it
changed, and which checks passed in your pull request.
