from pprint import pprint
from click import clear
import keyboard


def cb(event):
    # print(event)
    # print(dir(event))
    print("testing")
    print((event.name, event.scan_code, event.time, event.is_keypad, event.modifiers))
    if event.name == "esc":
        exit()


def clear_sticky_keys():
    # Release all modifier keys
    keyboard.release("shift")
    keyboard.release("ctrl")
    keyboard.release("oikea ctrl")
    keyboard.release("§")
    keyboard.release("esc")


keyboard.hook(cb)
keyboard.register_hotkey("ctrl+§", print, args=["hello, world"])
keyboard.wait("esc")
