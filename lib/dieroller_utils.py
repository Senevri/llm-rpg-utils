import random
import math

MODIFIER_MAP = {
    -6: "Trivial",
    -5: "Nearly Trivial",
    -4: "Outrageously Easy",
    -3: "Extremely Easy",
    -2: "Quite Easy",
    -1: "Easy",
    0: "Average Difficulty",
    1: "Slightly Difficult",
    2: "Difficult",
    3: "Quite Difficult",
    4: "Extremely Difficult",
    5: "Outrageously Difficult",
    6: "Practically Impossible",
}

def get_modifier_description(modifier):
    """Returns the descriptor for a given modifier value."""
    return MODIFIER_MAP.get(modifier, "Unknown Difficulty")

def parse_result(difference, total):
    """
    Analyzes the roll result based on roll-under rules.
    Difference = Target Number - Modified Total.
    """
    # Standard roll-under success degrees
    if total == 2:
        if difference < 0:
            # Handle critical success case if needed, 
            # but usually 2 is an automatic success in some systems.
            # For now, we follow the difference logic.
            pass
    
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

def roll_dice(target, difficulty, bonus):
    """
    Rolls 2d6 and compares against target number.
    target: The base target number.
    difficulty: The modifier from the difficulty map.
    bonus: Any additional bonuses/penalties.
    """
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    total = die1 + die2

    # In roll-under systems, difficulty usually increases the roll 
    # or decreases the target. 
    # Based on the original code: modified_total = total + difficulty + bonus
    # If roll_under target: success is total + diff + bonus <= target
    # So: Target - (total + diff + bonus) = difference.
    
    modified_total = total + difficulty + bonus
    difference = target - modified_total

    result_description = parse_result(difference, total)
    modifier_desc = get_modifier_description(difficulty)
    
    return (die1, die2, total, modified_total, difference, result_description, modifier_desc)

# Legacy functions kept for compatibility if used elsewhere
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
    fate_ladder_map = [
        (8, None, "Legendary"),
        (7, 7, "Epic"),
        (6, 6, "Fantastic"),
        (5, 5, "Superb"),
        (4, 4, "Great"),
        (3, 3, "Good"),
        (2, 2, "Fair"),
        (1, 1, "Average"),
        (0, 0, "Mediocre"),
        (-1, -1, "Poor"),
        (None, -2, "Terrible"),
    ]
    for lower_bound, upper_bound, descriptor in fate_ladder_map:
        if lower_bound is not None and upper_bound is not None:
            if lower_bound <= roll_result <= upper_bound:
                return descriptor
        elif lower_bound is not None:
            if roll_result >= lower_bound:
                return descriptor
        elif upper_bound is not None:
            if roll_result <= upper_bound:
                return descriptor
    return "Unknown"

def roll_fudge_die():
    outcomes = ["+", "-", " "]
    return random.choice(outcomes)

def fudge_to_int(fudge_result):
    if fudge_result == "+":
        return 1
    elif fudge_result == "-":
        return -1
    else:
        return 0

def roll_4df():
    dice_results_symbolic = []
    dice_results_numeric = []
    for _ in range(4):
        result_symbolic = roll_fudge_die()
        dice_results_symbolic.append(result_symbolic)
        result_numeric = fudge_to_int(result_symbolic)
        dice_results_numeric.append(result_numeric)
    total = sum(dice_results_numeric)
    return total
