"""Exercise real Tk widgets using fake API and voice services."""

import tkinter as tk
from unittest.mock import Mock

import pytest

from gencook.ui.app import CookingAssistant


@pytest.fixture(scope="module")
def tk_root():
    # Keep one Tcl interpreter alive, as the real desktop application does.
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def app(tk_root):
    root = tk.Toplevel(tk_root)
    root.withdraw()
    recipes = Mock()
    recipes.generate_ideas.return_value = ["Soup — Warm", "Rice — Quick", "Salad — Fresh"]
    recipes.generate_guide.return_value = "1. Chop.\n2. Cook."
    window = CookingAssistant(root, recipes, Mock())
    yield window
    root.destroy()


def add_ingredient(app, text):
    app.ingredient_entry.delete(0, tk.END)
    app.ingredient_entry.insert(0, text)
    app.add_ing()


def test_add_normalizes_and_deduplicates_ingredients(app):
    add_ingredient(app, " Rice ")
    add_ingredient(app, "rice")
    add_ingredient(app, " ")
    assert app.ingredients == ["rice"]
    assert app.ingredients_listbox.get(0, tk.END) == ("rice",)


def test_generation_and_selection_populate_widgets(app):
    add_ingredient(app, "rice")
    app.gen_recipe()
    app.recipes.generate_ideas.assert_called_once_with(["rice"])
    assert app.recipes_listbox.size() == 3
    app.recipes_listbox.selection_set(0)
    app.recipe_selected()
    app.recipes.generate_guide.assert_called_once_with("Soup — Warm")
    assert app.recipe_textbox.get("1.0", "end-1c") == "1. Chop.\n2. Cook."


def test_clear_removes_ingredients_ideas_and_instructions(app):
    add_ingredient(app, "rice")
    app.gen_recipe()
    app.display_recipe_guide("Soup")
    app.clear_ing()
    assert app.ingredients == []
    assert app.generated_recipes == []
    assert app.ingredients_listbox.size() == app.recipes_listbox.size() == 0
    assert app.recipe_textbox.get("1.0", "end-1c") == ""


def test_empty_ingredients_do_not_request_recipes(app):
    app.gen_recipe()
    app.recipes.generate_ideas.assert_not_called()
    assert "add ingredients" in app.status.get()


def test_api_failure_is_visible_without_exposing_exception_details(app):
    add_ingredient(app, "rice")
    app.recipes.generate_ideas.side_effect = RuntimeError("sensitive response details")
    app.gen_recipe()
    assert "Could not generate" in app.status.get()
    assert "sensitive" not in app.status.get()


def test_configuration_error_is_visible(app):
    add_ingredient(app, "rice")
    app.recipes.generate_ideas.side_effect = ValueError("Set OPENAI_API_KEY")
    app.gen_recipe()
    assert app.status.get() == "Set OPENAI_API_KEY"
