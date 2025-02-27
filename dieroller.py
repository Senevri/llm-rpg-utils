import tkinter as tk
import random
from tkinter import font


def roll_dice():
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    total = die1 + die2

    target = int(target_entry.get())
    difficulty = int(difficulty_entry.get() or 0)
    bonus = int(bonus_entry.get() or 0)

    modified_total = total + difficulty + bonus
    difference = target - modified_total

    result_description = parse_result(difference, total)

    die1_label.config(text=f"Die 1: {die1}")
    die2_label.config(text=f"Die 2: {die2}")
    total_label.config(text=f"Total: {total}")
    modified_total_label.config(text=f"Modified Total: {modified_total}")
    difference_label.config(text=f"Difference: {difference}")
    result_label.config(text=f"Result: {result_description}")


def parse_result(difference, total):
    if total == 2:
        if difference < 0:
            difference == 0
    if difference >= 7:
        return "Perfect Success"
    elif 4 <= difference < 7:
        return "Great Success"
    elif 2 <= difference < 4:
        return "Good Success"
    elif 1 <= difference < 2:
        return "Success"
    elif 0 <= difference < 1:
        return "Marginal Success"
    elif -1 <= difference < 0:
        return "Marginal Failure"
    elif -2 <= difference < -1:
        return "Failure"
    elif -4 <= difference < -2:
        return "Bad Failure"
    elif -7 <= difference < -4:
        return "Terrible Failure"
    else:
        return "Absolute Failure"


# Create the main window
root = tk.Tk()
root.title("Dice Roller")

# Define a larger font
large_font = font.Font(size=14)

# Create and place widgets with larger font and padding
tk.Label(root, text="Target Number:", font=large_font).grid(row=0, column=0, padx=10, pady=10)
target_entry = tk.Entry(root, font=large_font)
target_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Additional Difficulty:", font=large_font).grid(
    row=1, column=0, padx=10, pady=10
)
difficulty_entry = tk.Entry(root, font=large_font)
difficulty_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Bonuses:", font=large_font).grid(row=2, column=0, padx=10, pady=10)
bonus_entry = tk.Entry(root, font=large_font)
bonus_entry.grid(row=2, column=1, padx=10, pady=10)

roll_button = tk.Button(root, text="Roll Dice", font=large_font, command=roll_dice)
roll_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

die1_label = tk.Label(root, text="Die 1:", font=large_font)
die1_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

die2_label = tk.Label(root, text="Die 2:", font=large_font)
die2_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

total_label = tk.Label(root, text="Total:", font=large_font)
total_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

modified_total_label = tk.Label(root, text="Modified Total:", font=large_font)
modified_total_label.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

difference_label = tk.Label(root, text="Difference:", font=large_font)
difference_label.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

result_label = tk.Label(root, text="Result:", font=large_font)
result_label.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

# Run the application
root.mainloop()
