# Architecture

`app.py`, `python -m gencook`, and the `gencook` command all call `main.main()`.
Startup reads settings, composes recipe and speech services, creates the window,
and enters Tk's event loop. Services are closed when the event loop exits.

| Module | Responsibility |
| --- | --- |
| `config.py` | Read launch-directory `.env` and environment settings |
| `backend/recipes.py` | Lazy OpenAI client, prompts, recipe parsing and validation |
| `backend/speech.py` | Lazy pyttsx3 initialization and graceful voice fallback |
| `ui/app.py` | Ingredient input, recipe selection, output, and visible status |
| `ui/styles.py` | Colors and shared ttk styles |

Backend modules do not import Tkinter. The window receives its services as
constructor arguments. No module starts the app or creates external resources
on import. All user data is held in memory.

## Migration notes

- Split `GenCook Python Code` into an installable package and thin launcher.
- Replaced `ADDITIONAL LIBRARIES TO INSTALL FOR IDE` with declared dependencies.
- Replaced legacy `openai.ChatCompletion.create` with the instance-based
  `OpenAI().chat.completions.create` client, following the
  [official Python reference](https://developers.openai.com/api/reference/python/resources/chat/subresources/completions/methods/create).
- Preserved the original model through a configurable default.
- Replaced the hardcoded key placeholder with environment / `.env` configuration.
- Request and validate three recipe objects in JSON mode so blank lines and
  separate description paragraphs do not become extra selectable recipes.
- Clear the recipe list and details when ingredients are cleared, and clear old
  instructions after successfully generating a new list.
- Show errors in the window and keep speech failures from breaking the app.
- Preserve synchronous interactions; background requests and persistent storage
  are possible follow-up work.

## Testing

Backend tests use the real SDK with a mock HTTP transport, covering request
construction, output validation, configuration, and voice fallback. UI tests
create withdrawn Tk windows with fake services and exercise actual widgets.
No test reads a real API key or calls OpenAI. Physical audio playback and live
model generation require separate manual verification with the user's setup.
