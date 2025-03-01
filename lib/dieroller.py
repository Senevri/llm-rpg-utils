import tkinter as tk
import random
import math
from tkinter import font

try:
    from lib.dieroller_utils import roll_dice
except ImportError:
    from dieroller_utils import roll_dice


class DieRoller(tk.Tk):
    def __init__(self):
        super().__init__()
        # Create the main window
        self.title("Dice Roller")

        # Define a larger font
        large_font = font.Font(size=14)

        # Create and place widgets with larger font and padding
        tk.Label(self, text="Target Number:", font=large_font).grid(
            row=0, column=0, padx=10, pady=10
        )
        self.target_entry = tk.Entry(self, font=large_font)
        self.target_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self, text="Additional Difficulty:", font=large_font).grid(
            row=1, column=0, padx=10, pady=10
        )
        self.difficulty_entry = tk.Entry(self, font=large_font)
        self.difficulty_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self, text="Bonuses:", font=large_font).grid(row=2, column=0, padx=10, pady=10)
        self.bonus_entry = tk.Entry(self, font=large_font)
        self.bonus_entry.grid(row=2, column=1, padx=10, pady=10)

        roll_button = tk.Button(
            self, text="Roll Dice", font=large_font, command=self.click_roll_dice
        )
        roll_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.die1_label = tk.Label(self, text="Die 1:", font=large_font)
        self.die1_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.die2_label = tk.Label(self, text="Die 2:", font=large_font)
        self.die2_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.total_label = tk.Label(self, text="Total:", font=large_font)
        self.total_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        self.modified_total_label = tk.Label(self, text="Modified Total:", font=large_font)
        self.modified_total_label.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        self.difference_label = tk.Label(self, text="Difference:", font=large_font)
        self.difference_label.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

        self.result_label = tk.Label(self, text="Result:", font=large_font)
        self.result_label.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

        # Run the application

    def click_roll_dice(self):
        target = int(self.target_entry.get())
        difficulty = int(self.difficulty_entry.get() or 0)
        bonus = int(self.bonus_entry.get() or 0)
        result = roll_dice(target, difficulty, bonus)
        self.update_ui(result)

    def update_ui(self, roll_result):
        die1, die2, total, modified_total, difference, result_description = roll_result
        self.die1_label.config(text=f"Die 1: {die1}")
        self.die2_label.config(text=f"Die 2: {die2}")
        self.total_label.config(text=f"Total: {total}")
        self.modified_total_label.config(text=f"Modified Total: {modified_total}")
        self.difference_label.config(text=f"Difference: {difference}")
        self.result_label.config(text=f"Result: {result_description}")


if __name__ == "__main__":
    app = DieRoller()
    app.mainloop()
