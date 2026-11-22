#automatically type into browser window
from time import sleep
import sys
from pathlib import Path
import html
import keyboard

src = Path.cwd().resolve()
if src not in sys.path:
    sys.path.append(str(src))

from pywinauto.application import Application
import pywinauto.mouse as mouse
from pywinauto.controls.uiawrapper import UIAWrapper
from lib.browser_util import (
    get_active_window, get_active_browser_documents, find_window,
    find_browser
    )

test_str = (
    "Things, also stuff."
    )

print("Ready?")
sleep(2)

original_window = get_active_window()

# keyboard.press_and_release("ctrl+a")
# keyboard.press_and_release("ctrl+c")

window = find_browser("thorium")
window.minimize()
window.restore()
window.activate()
content = get_active_browser_documents()
for doc in content:
    for elem in doc.descendants():
        info = elem.element_info
        placeholders = [
            "Ask ChatGPT",
            "Send a Message",
            "Message DeepSeek",
            "Kysy Geminiltä",
            "Ask Qwen",
            "Type / for quick access",
            "How can I help you today?"
        ]

        if info.name in placeholders:
            coords = elem.rectangle().mid_point()
            mouse.click(coords=(coords.x, coords.y))
            break
#for l in test_str:
keyboard.write(test_str, 0.02)
#keyboard.press_and_release("return")
#keyboard.press_and_release("ctrl+v")

original_window.minimize()
original_window.restore()
original_window.activate()