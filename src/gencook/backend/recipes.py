"""OpenAI recipe generation, independent of desktop widgets and speech."""

import json
from collections.abc import Sequence

from openai import OpenAI

from gencook.config import Settings


class RecipeService:
    def __init__(self, settings: Settings, client=None):
        self.settings = settings
        self._client = client

    def _get_client(self):
        if self._client is None:
            if not self.settings.api_key or self.settings.api_key == "your-api-key-here":
                raise ValueError(
                    "Set OPENAI_API_KEY in your environment or .env file, then restart."
                )
            self._client = OpenAI(api_key=self.settings.api_key, timeout=30.0, max_retries=1)
        return self._client

    def _complete(self, prompt: str, *, json_output=False, max_tokens=500):
        options = {"response_format": {"type": "json_object"}} if json_output else {}
        response = self._get_client().chat.completions.create(
            model=self.settings.model,
            messages=[
                {"role": "system", "content": "You are a helpful cooking assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            **options,
        )
        if not response.choices or response.choices[0].finish_reason != "stop":
            raise ValueError("Recipe generation did not complete. Please try again.")
        content = response.choices[0].message.content
        if not content or not content.strip():
            raise ValueError("No recipe text was returned. Please try again.")
        return content.strip()

    def generate_ideas(self, ingredients: Sequence[str]) -> list[str]:
        cleaned = [ingredient.strip() for ingredient in ingredients if ingredient.strip()]
        if not cleaned:
            raise ValueError("Please add ingredients to generate a recipe.")
        content = self._complete(
            "Generate exactly 3 recipe ideas using these ingredients: "
            + ", ".join(cleaned)
            + '. Return a JSON object with a "recipes" array of exactly 3 objects, '
            'each containing a nonempty "title" and a brief "description" string.',
            json_output=True,
        )
        try:
            payload = json.loads(content)
            recipes = payload["recipes"]
            if not isinstance(recipes, list) or len(recipes) != 3:
                raise ValueError
            ideas = []
            for recipe in recipes:
                title, description = recipe["title"], recipe["description"]
                if not isinstance(title, str) or not isinstance(description, str):
                    raise ValueError
                if not title.strip() or not description.strip():
                    raise ValueError
                ideas.append(f"{title.strip()} — {description.strip()}")
            return ideas
        except (ValueError, TypeError, KeyError):
            raise ValueError(
                "Recipe ideas were not in the expected format. Please try again."
            ) from None

    def generate_guide(self, recipe: str) -> str:
        if not recipe.strip():
            raise ValueError("Select a recipe first.")
        return self._complete(
            "Provide detailed step-by-step cooking instructions for the following recipe: "
            + recipe.strip(),
            max_tokens=1000,
        )

    def close(self):
        if self._client is not None:
            self._client.close()
