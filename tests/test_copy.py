import sys
from pathlib import Path
import keyboard
from time import sleep


src = Path.cwd().resolve()
if src not in sys.path:
    sys.path.append(str(src))

from lib.clipboard_helper import get_transcript_from_clipboard, get_markdown_from_clipboard

sleep(2)  # Focus the browser manually

keyboard.press_and_release("ctrl+a")
sleep(1)

keyboard.press_and_release("ctrl+c")
sleep(0.5)
keyboard.press_and_release("ctrl+f")
sleep(0.5)
keyboard.press_and_release("escape")
sleep(1)



print("Done. Check clipboard contents.")

contents = get_markdown_from_clipboard()
# contents = get_transcript_from_clipboard()
print(contents)
