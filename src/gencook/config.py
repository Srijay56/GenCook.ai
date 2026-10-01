"""Read application settings without embedding credentials in source code."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    api_key: str = field(default="", repr=False)
    model: str = "gpt-3.5-turbo"
    speech_enabled: bool = True

    @classmethod
    def from_env(cls):
        # Only read the launch directory's file, not an unrelated parent .env.
        load_dotenv(Path.cwd() / ".env", override=False)
        return cls(
            api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo").strip() or "gpt-3.5-turbo",
            speech_enabled=os.getenv("GENCOOK_SPEECH_ENABLED", "true").lower()
            not in {"0", "false", "no", "off"},
        )
