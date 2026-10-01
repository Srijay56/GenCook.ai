"""Shared desktop colors and widget styles."""

from tkinter import ttk

BACKGROUND = "#e8f5e9"


def configure_styles():
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12), padding=10, relief="raised")
    style.configure("TLabel", font=("Arial", 14, "bold"), background=BACKGROUND, foreground="#333")
    style.configure("TEntry", font=("Arial", 12), padding=5)
