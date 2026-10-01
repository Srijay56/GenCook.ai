"""Compose services and start the desktop application."""

import tkinter as tk

from gencook.backend.recipes import RecipeService
from gencook.backend.speech import SpeechService
from gencook.config import Settings
from gencook.ui.app import CookingAssistant


def main():
    settings = Settings.from_env()
    recipes = RecipeService(settings)
    speech = SpeechService(enabled=settings.speech_enabled)
    root = tk.Tk()
    try:
        CookingAssistant(root, recipes, speech)
        root.mainloop()
    finally:
        speech.close()
        recipes.close()
