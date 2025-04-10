from enum import Enum
import keyboard
import pyperclip
import time
import os

from regex import T

try:
    from lib.dieroller_utils import (
        roll_dice,
        roll_4df,
        get_fate_ladder_descriptor,
        get_success_description,
    )
except ImportError:
    from dieroller_utils import (
        roll_dice,
        roll_4df,
        get_fate_ladder_descriptor,
        get_success_description,
    )

SYS_MODE = "BESM"
CONFIG_FILE = "pinned.txt"
INPUT_LOG_FILE = "userinput.log"
# Fixme: localizations for different systems
TRIGGER_KEY = {"HEADERS": "oikea ctrl+å", "CAPTURE": "oikea ctrl+enter", "ROLL": "oikea ctrl+ö"}


class DotDict:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __getattr__(self, item):
        return self.__dict__.get(item)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def from_dict(self, dictionary):
        self.__dict__.update(dictionary)
        return self


class KeyboardListener:

    def __init__(
        self,
        mode=SYS_MODE,
        config_file=CONFIG_FILE,
        input_log_file=INPUT_LOG_FILE,
    ):
        self.SYS_MODE = mode
        self.CONFIG_FILE = config_file
        self.INPUT_LOG_FILE = input_log_file
        self.TRIGGER_KEY = DotDict().from_dict(TRIGGER_KEY)

    def generate_h_f_file(self):
        print(
            f"Configuration file '{self.CONFIG_FILE}' not found. Creating a default file with multiline example."
        )
        with open(self.CONFIG_FILE, "w") as f:
            f.write("[HEADER_START]\n")
            f.write("This is the default multiline header.\n")
            f.write("You can have multiple lines here.\n")
            f.write("[HEADER_END]\n")
            f.write("[FOOTER_START]\n")
            f.write("This is the default multiline footer.\n")
            f.write("It can also span across lines.\n")
            f.write("[FOOTER_END]\n")
        print(f"Please edit '{self.CONFIG_FILE}' to customize your multiline header and footer.")
        return ("", "")

    def load_header_footer_from_file(self):
        """
        Loads multiline header and footer from the configuration file using delimiters.
        Returns a tuple (header, footer) or None if there's an error.
        """
        header = None
        footer = None
        CONFIG_FILE = self.CONFIG_FILE
        try:

            if not os.path.exists(CONFIG_FILE):
                return self.generate_h_f_file()
            with open(CONFIG_FILE, "r", encoding="UTF-8") as f:
                content = f.read()

            header_start_tag = "[HEADER_START]"
            header_end_tag = "[HEADER_END]"
            footer_start_tag = "[FOOTER_START]"
            footer_end_tag = "[FOOTER_END]"

            header_start_index = content.find(header_start_tag)
            header_end_index = content.find(header_end_tag)
            footer_start_index = content.find(footer_start_tag)
            footer_end_index = content.find(footer_end_tag)

            if (
                header_start_index != -1
                and header_end_index != -1
                and header_start_index < header_end_index
            ):
                header = content[
                    header_start_index + len(header_start_tag) : header_end_index
                ].strip()
            else:
                print(
                    f"Error parsing '{CONFIG_FILE}' for header. Check for '{header_start_tag}' and '{header_end_tag}' tags. Using default header."
                )
                header = "--- DEFAULT HEADER ---\n(Multiline Default)"

            if (
                footer_start_index != -1
                and footer_end_index != -1
                and footer_start_index < footer_end_index
            ):
                footer = content[
                    footer_start_index + len(footer_start_tag) : footer_end_index
                ].strip()
            else:
                print(
                    f"Error parsing '{CONFIG_FILE}' for footer. Check for '{footer_start_tag}' and '{footer_end_tag}' tags. Using default footer."
                )
                footer = "--- DEFAULT FOOTER ---\n(Multiline Default)"
            self.header, self.footer = header, footer
            return header, footer

        except Exception as e:
            print(f"Error reading configuration file '{CONFIG_FILE}': {e}")
            return (
                "--- DEFAULT HEADER ---\n(Error Default)",
                "--- DEFAULT FOOTER ---\n(Error Default)",
            )

    def add_header_footer(self):
        """
        Performs Ctrl+A, Ctrl+X, adds the provided header and footer (can be multiline), and pastes.
        """
        try:
            header, footer = self.load_header_footer_from_file()

            if text_content := self.capture_input():
                # Add header and footer
                modified_text = f"{header}\n{text_content}\n{footer}"

                # Copy modified text to clipboard
                pyperclip.copy(modified_text)

                # Simulate Ctrl+V (Paste)
                keyboard.press_and_release("ctrl+v")
                time.sleep(0.05)
                print("Multiline header and footer added and pasted!")
            else:
                print(
                    "No text found in clipboard after cut operation. Did Ctrl+A+Ctrl+X work correctly?"
                )

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Make sure you have selected text in the textarea before pressing the hotkey.")

    def capture_input(self, deselect=False):
        try:
            # Simulate Ctrl+A (Select All)
            keyboard.press_and_release("ctrl+a")
            time.sleep(0.05)

            # Simulate Ctrl+X (Cut)
            keyboard.press_and_release("ctrl+c")
            time.sleep(0.05)
            if deselect:
                keyboard.press_and_release("right")
            # Get text from clipboard
            text_content = pyperclip.paste()

            if text_content:
                with open(self.INPUT_LOG_FILE, "at", encoding="UTF-8") as file:
                    file.write(f"{text_content}\n---\n")
            return text_content
        except Exception as e:
            print(f"An error occurred: {e}")

    def insert_roll_result(self):
        try:
            if text_content := self.capture_input():
                print(text_content)
                begin = text_content.index("{")
                if begin == -1:
                    return
                end = begin + text_content[begin + 1 :].index("}")
                rollcmd = text_content[begin + 1 : end + 1]
                # print(f"rolling... {rollcmd}")
                target, difficulty, bonus = (int(x) for x in rollcmd.split(","))

                if self.SYS_MODE == "BESM":
                    die1, die2, total, modified_total, difference, result_description = roll_dice(
                        target, difficulty, bonus
                    )
                if self.SYS_MODE == "Fate":
                    # target ==
                    result = roll_4df()
                    total_result = target + bonus + result
                    quality = get_fate_ladder_descriptor(total_result)
                    outcome = get_success_description((target + bonus + result), difficulty)
                    result_description = f"{quality} ({total_result}: {outcome})"
                modified_text = text_content[:begin] + result_description + text_content[end + 2 :]
                # Copy modified text to clipboard
                pyperclip.copy(modified_text)

                # Simulate Ctrl+V (Paste)
                keyboard.press_and_release("ctrl+v")
        except Exception as e:
            print(f"An error occurred: {e}")

    def add_hotkey(self, key, func):
        keyboard.add_hotkey(key, func)

    def start_listener(self):
        keyboard.add_hotkey(self.TRIGGER_KEY.HEADERS, lambda: self.add_header_footer())
        keyboard.add_hotkey(self.TRIGGER_KEY.CAPTURE, lambda: self.capture_input(deselect=True))
        keyboard.add_hotkey(self.TRIGGER_KEY.ROLL, lambda: self.insert_roll_result())
        keyboard.wait()

    def stop_listener(self):
        for key in self.TRIGGER_KEY.entries:
            keyboard.remove_hotkey(key)

    def print_help(self):
        if self.header or self.footer:
            header, footer = self.header, self.footer
            print(self.TRIGGER_KEY)
            print(
                (
                    "Script started. ",
                    f"['{self.TRIGGER_KEY.HEADERS}']adds multiline header ",
                    f"and footer from '{CONFIG_FILE}' to selected text.\n",
                    f"['{self.TRIGGER_KEY.CAPTURE}']captures selected text to a file.\n",
                    f"['{self.TRIGGER_KEY.ROLL}']rolls dice based on the selected text.\n",
                    "Hotkeys can be changed in the script.\n",
                )
            )
            print(f"Header:\n---\n{header}\n---\nFooter:\n---\n{footer}\n---")
        else:
            print(
                f"Script started with default multiline header and footer as configuration file could not be loaded properly or was just created."
            )
            header = "--- DEFAULT HEADER ---\n(Multiline Default)"
            footer = "--- DEFAULT FOOTER ---\n(Multiline Default)"


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if ".txt" in arg:
                CONFIG_FILE = arg
            if arg == "-f":
                SYS_MODE = "Fate"

    listener = KeyboardListener()

    header_footer_values = listener.load_header_footer_from_file()
    listener.print_help()

    listener.start_listener()
