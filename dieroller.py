import tkinter as tk
import random
import math
from tkinter import font


def get_success_description(roll_result, difficulty):

    if roll_result < difficulty:
        return "fail"
    if roll_result > difficulty:
        description = "succeed"
        if roll_result - difficulty >= 3:
            times = math.floor((roll_result - difficulty) / 3)
            times_str = ""
            if times > 1:
                times_str = f" x{times}"
            description += f" with style{times_str}"
        return description
    return "tie"


def get_fate_ladder_descriptor(roll_result):
    """Translates a 4dF roll result to a Fate Ladder descriptor using a data-driven approach
    based on the provided ladder: +8Legendary+7Epic+6Fantastic+5Superb+4Great+3Good+2Fair+1Average+0Mediocre-1Poor-2Terrible.
    Args:
        roll_result (int): The total result of a 4dF roll.
    Returns:
        str: The Fate Ladder descriptor.
    """
    fate_ladder_map = [
        (8, None, "Legendary"),  # 8 and above
        (7, 7, "Epic"),
        (6, 6, "Fantastic"),
        (5, 5, "Superb"),
        (4, 4, "Great"),
        (3, 3, "Good"),
        (2, 2, "Fair"),
        (1, 1, "Average"),
        (0, 0, "Mediocre"),
        (-1, -1, "Poor"),
        (None, -2, "Terrible"),  # -2 and below
    ]

    for lower_bound, upper_bound, descriptor in fate_ladder_map:
        if lower_bound is not None and upper_bound is not None:  # Bounded range
            if lower_bound <= roll_result <= upper_bound:
                return descriptor
        elif lower_bound is not None:  # Unbounded upper range (and above)
            if roll_result >= lower_bound:
                return descriptor
        elif upper_bound is not None:  # Unbounded lower range (and below)
            if roll_result <= upper_bound:
                return descriptor

    return "Unknown"  # Fallback


def roll_fudge_die():
    """Simulates rolling a single Fudge die (dF).
    Returns:
        str: '+', '-', or ' ' representing the die result.
    """
    outcomes = ["+", "-", " "]  # Fudge die faces: +, -, blank
    return random.choice(outcomes)


def fudge_to_int(fudge_result):
    """Converts a Fudge die result symbol to an integer.
    Args:
        fudge_result (str): '+', '-', or ' '.
    Returns:
        int: 1 for '+', -1 for '-', 0 for ' '.
    """
    if fudge_result == "+":
        return 1
    elif fudge_result == "-":
        return -1
    else:  # ' ' (blank)
        return 0


def roll_4df():
    """Simulates rolling 4 Fudge dice (4dF).
    Prints the individual die results and the total.
    Returns:
        int: The total result of the 4dF roll.
    """
    dice_results_symbolic = []
    dice_results_numeric = []

    print("Rolling 4dF...")
    for _ in range(4):
        result_symbolic = roll_fudge_die()
        dice_results_symbolic.append(result_symbolic)
        result_numeric = fudge_to_int(result_symbolic)
        dice_results_numeric.append(result_numeric)

    total = sum(dice_results_numeric)

    print("\nIndividual die results:")
    for i in range(4):
        print(f"Die {i+1}: {dice_results_symbolic[i]} ({dice_results_numeric[i]})")

    print(f"\nTotal 4dF result: {total}")
    return total


def roll_dice(target, difficulty, bonus):
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    total = die1 + die2

    modified_total = total + difficulty + bonus
    difference = target - modified_total

    result_description = parse_result(difference, total)
    return (die1, die2, total, modified_total, difference, result_description)


def click_roll_dice():
    target = int(target_entry.get())
    difficulty = int(difficulty_entry.get() or 0)
    bonus = int(bonus_entry.get() or 0)
    result = roll_dice(target, difficulty, bonus)
    update_ui(result)


def update_ui(roll_result):
    die1, die2, total, modified_total, difference, result_description = roll_result
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


if __name__ == "__main__":
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

    roll_button = tk.Button(root, text="Roll Dice", font=large_font, command=click_roll_dice)
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
