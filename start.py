#!/usr/bin/env python3
from textwrap import dedent
import sys
import os
from lib.textarea_util import KeyboardListener

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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if ".txt" in arg:
                CONFIG_FILE = arg
            if arg == "-f":
                SYS_MODE = "Fate"

            if arg == "-h":
                print_help()
                exit()

    listener = KeyboardListener()
    header, footer = listener.load_header_footer_from_file()
    if header and footer:
        listener.start_listener()
