"""Optional local voice feedback, initialized only when first used."""

import logging

logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(self, enabled=True, engine_factory=None):
        self.enabled = enabled
        self._engine_factory = engine_factory
        self._engine = None

    def speak(self, text: str):
        if not self.enabled:
            return
        try:
            if self._engine is None:
                if self._engine_factory is None:
                    import pyttsx3

                    self._engine_factory = pyttsx3.init
                self._engine = self._engine_factory()
                self._engine.setProperty("rate", 150)
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception:
            # Speech is an enhancement; a missing OS voice must not break the UI.
            logger.warning("Speech is unavailable. Continuing with on-screen feedback.")
            self.enabled = False

    def close(self):
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                logger.warning("Could not stop the speech engine cleanly.")
