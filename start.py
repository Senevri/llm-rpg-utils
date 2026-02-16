#!/usr/bin/env python3
from textwrap import dedent
import sys
import os
from lib.textarea_util import KeyboardListener
from lib.browser_util import (
    get_active_browser_content,
    get_active_window,
    is_browser_window,
    split_app_content,
)
from lib.clipboard_helper import get_transcript_from_clipboard

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# try:
#     pass
# except ImportError:
#     pass

# from lib.dieroller_utils import (
#     roll_dice,
#     roll_4df,
#     get_fate_ladder_descriptor,
#     get_success_description,
# )


def print_help():
    print(
        dedent(
            """Usage: python start.py [-f] [-h] [filename]
            Options:")
                -f: Use Fate mode")
                -h: Print this help")
                filename: Load header and footer from filename
            """
        )
    )


# def test_ensure_dialog_newlines():
#     input_text = 'Hello. "How are you?" I asked. "I\'m fine!" she replied.'
#     expected_output = 'Hello. \n\n"How are you?" I asked. \n\n"I\'m fine!" she replied.'
#     print(ensure_dialog_newlines(input_text))
#     print(expected_output)
#     assert ensure_dialog_newlines(input_text) == expected_output
#     print("Test passed!")

def get_title():
    title = str(get_active_window().title).replace(" ", "_")
    title = title.replace(",", "")
    title = title.replace(":", "_")
    return title

def capture_from_clipboard():
    print("capture from clipboard")
    content = get_transcript_from_clipboard()
    title = get_title()
    with open(f"{title}_content.txt", "w", encoding="UTF-8") as f:
        f.write(content)

def capture_content():
    print("capture browser content")

    browser = is_browser_window(get_active_window())
    content = get_active_browser_content()
    title = get_title()
    if content:
        with open(f"{title}_content.txt", "w", encoding="UTF-8") as f:
            blocks = split_app_content(content, app="chatgpt", ensure_newlines=True)
            for name, text, index in blocks:
                f.write(f"## {index}: {name}:\n{text}\n\n---\n")


if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if ".txt" in arg:
                CONFIG_FILE = arg
            if arg == "-f":
                SYS_MODE = "Fate"

            if arg == "-h":
                print_help()
                exit()

    # test_ensure_dialog_newlines()
    # exit()

    listener = KeyboardListener()
    listener.add_hotkey("oikea ctrl+§", capture_content)
    listener.add_hotkey("oikea ctrl+shift+§", capture_from_clipboard)
    header, footer = listener.load_header_footer_from_file()
    print("Trigger keys:", listener.TRIGGER_KEY)
    listener.print_help()
    if header and footer:
        try:
            listener.start_listener()
        except KeyboardInterrupt:
            print("Caught KeyboardInterrupt (Ctrl+C).")
            listener.stop_listener()
            raise  # Re-raise the exception to pass it on
