"""Tkinter presentation, with recipe and speech services injected at startup."""

import tkinter as tk
from tkinter import ttk

from gencook.ui.styles import BACKGROUND, configure_styles


class CookingAssistant:
    def __init__(self, root, recipes, speech):
        self.recipes = recipes
        self.speech = speech
        self.root = root
        self.root.title("GenCook")
        self.root.geometry("700x800")
        self.root.minsize(650, 650)
        self.root.configure(bg=BACKGROUND)  # Light green background

        self.ingredients = []
        self.generated_recipes = []

        configure_styles()

        # Header
        header_label = ttk.Label(root, text="GenCook.ai", style="TLabel")
        header_label.pack(pady=10)

        # Input Section
        input_frame = ttk.Frame(root)
        input_frame.pack(pady=10)

        ingredient_label = ttk.Label(input_frame, text="Enter an ingredient:", style="TLabel")
        ingredient_label.grid(row=0, column=0, padx=5, pady=5)

        self.ingredient_entry = ttk.Entry(input_frame, width=30)
        self.ingredient_entry.grid(row=0, column=1, padx=5, pady=5)

        add_button = ttk.Button(input_frame, text="Add Ingredient", command=self.add_ing)
        add_button.grid(row=0, column=2, padx=5, pady=5)

        # Ingredients List
        self.ingredients_listbox = tk.Listbox(
            root, font=("Arial", 12), width=40, height=6, bg="#fff", bd=2, relief="sunken"
        )
        self.ingredients_listbox.pack(pady=10)

        clear_button = ttk.Button(root, text="Clear Ingredients", command=self.clear_ing)
        clear_button.pack(pady=10)

        # Recipe Generation Section
        generate_frame = ttk.Frame(root)
        generate_frame.pack(pady=10, fill="x")  # Center horizontally

        generate_button = ttk.Button(
            generate_frame, text="Generate Recipe", command=self.gen_recipe
        )
        generate_button.pack(pady=10)  # Automatically centers within the frame

        # Recipes List Section
        recipe_label = ttk.Label(root, text="Select a Recipe:", style="TLabel")
        recipe_label.pack(pady=10)

        self.recipes_listbox = tk.Listbox(
            root, font=("Arial", 12), width=40, height=6, bg="#fff", bd=2, relief="sunken"
        )
        self.recipes_listbox.pack(pady=10)
        self.recipes_listbox.bind(
            "<<ListboxSelect>>", self.recipe_selected
        )  # Bind the selection event

        # Recipe Details Section
        details_label = ttk.Label(root, text="Generated Recipe Details:", style="TLabel")
        details_label.pack(pady=10)

        # Reserve space for feedback before the expanding recipe panel.
        self.status = tk.StringVar(value="Add ingredients to get started.")
        ttk.Label(root, textvariable=self.status, wraplength=650).pack(
            side="bottom", fill="x", pady=8
        )

        # Frame for recipe details with scrollbar
        recipe_frame = tk.Frame(root, bg=BACKGROUND)
        recipe_frame.pack(pady=10, fill="both", expand=True)

        self.recipe_textbox = tk.Text(
            recipe_frame,
            wrap="word",
            font=("Arial", 12),
            width=70,
            height=20,
            bg="#fff",
            bd=2,
            relief="sunken",
        )
        self.recipe_textbox.pack(side="left", fill="both", expand=True)

        recipe_scrollbar = ttk.Scrollbar(
            recipe_frame, orient="vertical", command=self.recipe_textbox.yview
        )
        recipe_scrollbar.pack(side="right", fill="y")

        self.recipe_textbox.config(yscrollcommand=recipe_scrollbar.set)

    def add_ing(self):
        ingredient = self.ingredient_entry.get().strip().lower()
        if ingredient and ingredient not in self.ingredients:
            self.ingredients.append(ingredient)
            self.ingredients_listbox.insert(tk.END, ingredient)
            self.ingredient_entry.delete(0, tk.END)

    def clear_ing(self):
        self.ingredients.clear()
        self.generated_recipes.clear()
        self.ingredients_listbox.delete(0, tk.END)
        self.recipes_listbox.delete(0, tk.END)
        self.recipe_textbox.delete("1.0", tk.END)
        self._notify("Ingredients cleared successfully.")

    def _notify(self, text):
        self.status.set(text)
        self.speech.speak(text)

    def gen_recipe(self):
        if not self.ingredients:
            self._notify("Please add ingredients to generate a recipe.")
            return
        self.status.set("Generating recipe ideas...")
        self.root.update_idletasks()
        try:
            ideas = self.recipes.generate_ideas(self.ingredients)
        except ValueError as error:
            self._notify(str(error))
            return
        except Exception:
            self._notify(
                "Could not generate recipes. Check your connection, API key, and model access."
            )
            return
        self.generated_recipes = ideas
        self.recipes_listbox.delete(0, tk.END)
        self.recipe_textbox.delete("1.0", tk.END)
        for recipe in ideas:
            self.recipes_listbox.insert(tk.END, recipe)
        self._notify("Here are three recipe ideas for you. Select one.")

    def recipe_selected(self, event=None):
        selection = self.recipes_listbox.curselection()
        if selection:
            self.display_recipe_guide(self.generated_recipes[selection[0]])

    def display_recipe_guide(self, selected_recipe):
        self.status.set("Generating cooking instructions...")
        self.root.update_idletasks()
        try:
            guide = self.recipes.generate_guide(selected_recipe)
        except ValueError as error:
            self._notify(str(error))
            return
        except Exception:
            self._notify(
                "Could not generate instructions. Check your connection, API key, and model access."
            )
            return
        self.recipe_textbox.delete("1.0", tk.END)
        self.recipe_textbox.insert(tk.END, guide)
        self._notify("Here are the instructions to prepare the recipe.")
