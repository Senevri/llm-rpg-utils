import keyboard
import pyperclip
import time
import os

CONFIG_FILE = "pinned.txt"
INPUT_LOG_FILE = "userinput.log"
TRIGGER_KEY = "ctrl+å"  # Change this to your desired key combination
TRIGGER_KEY_CAPTURE = "ctrl+enter"


def load_header_footer_from_file():
    """
    Loads multiline header and footer from the configuration file using delimiters.
    Returns a tuple (header, footer) or None if there's an error.
    """
    header = None
    footer = None
    try:
        if not os.path.exists(CONFIG_FILE):
            print(
                f"Configuration file '{CONFIG_FILE}' not found. Creating a default file with multiline example."
            )
            with open(CONFIG_FILE, "w") as f:
                f.write("[HEADER_START]\n")
                f.write("This is the default multiline header.\n")
                f.write("You can have multiple lines here.\n")
                f.write("[HEADER_END]\n")
                f.write("[FOOTER_START]\n")
                f.write("This is the default multiline footer.\n")
                f.write("It can also span across lines.\n")
                f.write("[FOOTER_END]\n")
            print(f"Please edit '{CONFIG_FILE}' to customize your multiline header and footer.")
            return None

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
            header = content[header_start_index + len(header_start_tag) : header_end_index].strip()
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
            footer = content[footer_start_index + len(footer_start_tag) : footer_end_index].strip()
        else:
            print(
                f"Error parsing '{CONFIG_FILE}' for footer. Check for '{footer_start_tag}' and '{footer_end_tag}' tags. Using default footer."
            )
            footer = "--- DEFAULT FOOTER ---\n(Multiline Default)"

        return header, footer

    except Exception as e:
        print(f"Error reading configuration file '{CONFIG_FILE}': {e}")
        return "--- DEFAULT HEADER ---\n(Error Default)", "--- DEFAULT FOOTER ---\n(Error Default)"


def add_header_footer():
    """
    Performs Ctrl+A, Ctrl+X, adds the provided header and footer (can be multiline), and pastes.
    """
    try:
        header, footer = load_header_footer_from_file()
        # Simulate Ctrl+A (Select All)
        keyboard.press_and_release("ctrl+a")
        time.sleep(0.05)

        # Simulate Ctrl+X (Cut)
        keyboard.press_and_release("ctrl+x")
        time.sleep(0.05)

        # Get text from clipboard
        text_content = pyperclip.paste()

        if text_content:
            with open(INPUT_LOG_FILE, "at", encoding="UTF-8") as file:
                file.write(f"{text_content}\n---\n")
            # Add header and footer
            modified_text = f"{header}\n{text_content}\n{footer}"

            # Copy modified text to clipboard
            pyperclip.copy(modified_text)

            # Simulate Ctrl+V (Paste)
            keyboard.press_and_release("ctrl+v")
            print("Multiline header and footer added and pasted!")
        else:
            print(
                "No text found in clipboard after cut operation. Did Ctrl+A+Ctrl+X work correctly?"
            )

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure you have selected text in the textarea before pressing the hotkey.")


def capture_input():
    try:
        # Simulate Ctrl+A (Select All)
        keyboard.press_and_release("ctrl+a")
        time.sleep(0.05)

        # Simulate Ctrl+X (Cut)
        keyboard.press_and_release("ctrl+c")
        time.sleep(0.05)
        keyboard.press_and_release("right")
        # Get text from clipboard
        text_content = pyperclip.paste()

        if text_content:
            with open(INPUT_LOG_FILE, "at", encoding="UTF-8") as file:
                file.write(f"{text_content}\n---\n")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    header_footer_values = load_header_footer_from_file()

    if header_footer_values:
        header, footer = header_footer_values
        print(
            f"Script started. Press '{TRIGGER_KEY}' to add multiline header and footer from '{CONFIG_FILE}' to selected text."
        )
        print(f"Header:\n---\n{header}\n---\nFooter:\n---\n{footer}\n---")
    else:
        print(
            f"Script started with default multiline header and footer as configuration file could not be loaded properly or was just created."
        )
        header = "--- DEFAULT HEADER ---\n(Multiline Default)"
        footer = "--- DEFAULT FOOTER ---\n(Multiline Default)"

    print(
        "Make sure you have installed 'keyboard' and 'pyperclip' libraries (pip install keyboard pyperclip)"
    )

    keyboard.add_hotkey(TRIGGER_KEY, lambda: add_header_footer())
    keyboard.add_hotkey(TRIGGER_KEY_CAPTURE, lambda: capture_input())

    keyboard.wait()
