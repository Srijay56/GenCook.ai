# GenCook.ai

A Python desktop cooking assistant. Add ingredients, generate three recipe ideas,
and select one for step-by-step cooking instructions. Tkinter provides the UI,
OpenAI generates recipes, and pyttsx3 provides optional voice feedback.

## Quick start

Requires **Python 3.11+ with Tkinter**, internet access, and an OpenAI API key with
access to the configured model. API requests use your account's billing.

```bash
git clone https://github.com/Srijay56/GenCook.ai.git
cd GenCook.ai
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install the application:

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` in the repository root and replace the placeholder
with your API key. Keep `.env` private; Git ignores it. Environment variables take
precedence over `.env` values.

```dotenv
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
GENCOOK_SPEECH_ENABLED=true
```

Launch from the repository root:

```bash
python -m gencook
```

`python app.py` and the installed `gencook` command also launch the application.
The window opens without credentials; generation displays a configuration
message until a key is supplied and the app is restarted.

For reproducible development with [uv](https://docs.astral.sh/uv/):

```bash
uv sync --frozen --extra dev
uv run --frozen python -m gencook
```

### Desktop requirements

- Tkinter is part of Python's standard library, but Tcl/Tk must be installed with
  Python. Check with `python -m tkinter`; do not `pip install tkinter`.
- Linux may provide Tk separately (for example, `python3-tk` on Debian/Ubuntu).
  A graphical desktop/display is required.
- Speech uses operating-system voices. If unavailable, the app falls back to
  on-screen messages. Set `GENCOOK_SPEECH_ENABLED=false` to disable speech.

## Repository layout

```text
GenCook.ai/
├── app.py                       # Convenience launcher
├── src/gencook/
│   ├── __main__.py               # python -m gencook
│   ├── main.py                   # Compose services and start Tkinter
│   ├── config.py                 # Environment / .env settings
│   ├── backend/
│   │   ├── recipes.py            # OpenAI client, prompts, validation
│   │   └── speech.py             # Optional local voice feedback
│   └── ui/
│       ├── app.py                # Window, widgets, interaction callbacks
│       └── styles.py             # Shared colors and ttk styles
├── tests/                       # Service tests and real Tk widget tests
├── docs/architecture.md         # Boundaries and migration notes
├── .github/workflows/ci.yml      # Lint, format, test, build
├── .env.example                 # Configuration template
├── pyproject.toml               # Package, dependencies, tool settings
├── requirements.txt             # pip installation entry point
└── uv.lock                      # Reproducible dependency resolution
```

UI and backend run in one desktop process. No web server or database is required.
Imports do not open windows, initialize speech, or send API requests.

## Development

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m pytest
python -m build
```

Tests mock API requests and speech, so they need no API key and incur no API
charges. UI tests use withdrawn Tk windows and require Tcl/Tk and a display.
CI runs on Windows with Python 3.11 and 3.12.

See [CONTRIBUTING.md](CONTRIBUTING.md) and
[docs/architecture.md](docs/architecture.md).

## Current limitations

- Recipe and speech calls remain synchronous, as in the original application.
  The window may pause during generation or voice playback. Wait for completion
  before selecting another recipe. API calls have a 30-second timeout per attempt
  and one automatic retry.
- Ingredients and recipes live in memory and are not saved on exit.
- The default model remains `gpt-3.5-turbo` from the original project. Availability
  depends on your account. `OPENAI_MODEL` can select a Chat Completions model that
  supports JSON mode, `temperature`, and `max_tokens`.
- Review generated suggestions and cooking instructions before use.

The original extensionless code and library-list files were replaced by this
package and dependency metadata. They remain recoverable in Git history.
No license has been added; the owner should choose one before granting reuse rights.
