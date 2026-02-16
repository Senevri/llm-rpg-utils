from math import e
import re
import pygetwindow as gw
import logging
import keyboard
from time import sleep, time
from pywinauto import Application, WindowSpecification, Desktop
from pprint import pformat, pprint
from gettext import find
from custom_logger import get_custom_logger
from bs4 import BeautifulSoup

from clipboard_helper import get_transcript_from_clipboard

logger = get_custom_logger(__file__, "browser_util", add_date=False, console=True)

browsers = ["chrome", "firefox", "edge", "opera", "thorium", "brave", "safari", "joplin"]


def capture_from_clipboard():
    # _copy_all_and_deselect()
    return get_transcript_from_clipboard()

# ----------------------------------------------------------------------
# 3️⃣ Automation: Ctrl+A → Ctrl+C → Esc (deselect)
# ----------------------------------------------------------------------
def _copy_all_and_deselect(pause: float = 0.15) -> None:
    """
    Simulate the keystrokes that a human would use:

        1. Ctrl+A   – select everything on the page
        2. Ctrl+C   – copy the selection to the clipboard
        3. Esc      – clear the visual selection (optional but nice)

    `pause` is the tiny delay between each key event; increase it if
    your machine is slow or the browser needs a moment to react.
    """
    # Make sure no other modifier keys are stuck
    keys = 'ctrl+shift+alt+win'
    while any(keyboard.is_pressed(k) for k in keys.split('+')):
        print(".", end="", flush=True)
        sleep(pause)   # tiny sleep to avoid busy‑waiting

    keyboard.release('ctrl')
    keyboard.release('shift')
    keyboard.release('alt')
    keyboard.release('win')

    # 1️⃣ Ctrl+A
    keyboard.press_and_release('ctrl+a', do_press=True)
    sleep(pause)

    # 2️⃣ Ctrl+C
    keyboard.press_and_release('ctrl+c', do_press=True)
    sleep(pause)

    keyboard.release('ctrl')

    # 3️⃣ Esc – clears the highlight
    keyboard.press_and_release('esc')
    sleep(pause)

def get_active_window():
    # Get the title of the active window
    active_window = gw.getActiveWindow()

    if active_window is None:
        return "No active window found."
    return active_window


def is_browser_window(active_window):
    title = str(active_window.title)

    for browser in browsers:
        if browser in title.lower():
            logger.info(f"Recognized {browser} window.")
            return browser
    return False


def get_active_browser_content():
    active_window = get_active_window()
    # Check if the active window is a browser
    if is_browser_window(active_window):
        # Print all available window titles
        # windows = Desktop(backend="uia").windows()
        # for w in windows:
        #     print(w.window_text())
        # Connect to the browser window
        app = Application(backend="uia").connect(handle=active_window._hWnd)

        # Get the top-level window
        dlg: WindowSpecification = app.top_window()

        documents = dlg.descendants(control_type="Document")
        # Get the HTML content of the page
        doc_texts = [document.window_text() for document in documents]
        return doc_texts
    else:
        return ""




def find_first_tag(content, begin_tag):
    """
    Finds the first occurrence of the begin tag in the content.
    content: text content to search
    begin_tag: tag to search for
    """
    # find first begin tag
    if isinstance(begin_tag, list):
        for tag in begin_tag:
            index = content.find(tag)
            if index != -1:
                return tag
    else:
        index = content.find(begin_tag)
        if index != -1:
            return begin_tag
    return None


# def split_blocks(content, begin_tag, end_tag):
#     """
#     Splits the content into blocks based on the begin and end tags; content can
#     have multiple begin and end tags.
#     content: text content to split
#     """
#     blocks = []

#     begin_tag = find_first_tag(content, begin_tag)
#     end_tag = find_first_tag(content, end_tag)
#     if not begin_tag or not end_tag:
#         return content
#     index = content.find(begin_tag)
#     end_index = content.find(end_tag)
#     if index > end_index:
#         begin_tag, end_tag = end_tag, begin_tag

#     index = end_index
#     while index != -1:
#         # find the end tag
#         end_index = content.find(end_tag, index)
#         if end_index != -1:
#             blocks.append(content[index:end_index])
#             index = end_index + len(end_tag)
#             content = content[index:]
#             index = content.find(begin_tag)
#             blocks.append(content[:index])
#         else:
#             break


#     return blocks


def create_pattern(tags):
    pattern = "|".join(re.escape(tag) for tag in tags)
    return pattern


def split_text(text, tags):
    pattern = create_pattern(tags)
    chunks = re.split(pattern, text)
    return chunks


def split_blocks(content, begin_tag, end_tags):
    if isinstance(end_tags, str):
        end_tags = [end_tags]
    if isinstance(begin_tag, str):
        begin_tag = [begin_tag]
    tags = list(set(begin_tag + end_tags))
    pattern = create_pattern(tags)
    chunks = re.split(pattern, content)
    return chunks


def split_app_text(text, begin_tags, end_tags, removable_content, ignore_until_begin=False):
    # logger.info(f"Splitting text: \n{text[:80]}...")
    logger.info(f"Splitting with tags: {begin_tags}, {end_tags}")
    try:
        if ignore_until_begin:
            tags = begin_tags + end_tags
            tag = find_first_tag(text, tags)
            if tag:
                logger.warning(f"Ignoring content until tag: {tag}")
                text = text[text.find(tag) :]
        blocks = split_blocks(text, begin_tags, end_tags)
        removable_content_set = set(removable_content)
        blocks = [
            block
            for block in blocks
            if not any(content in block for content in removable_content_set)
        ]
        blocks = [block for block in blocks if block.strip()]
        return blocks
    except Exception as e:
        logger.error(f"Error splitting text: {text} with tags: {begin_tags}, {end_tags}")
        raise e


def split_joplin_text(text):
    begin_tags = "<begin>"
    end_tags = "<end>"
    removable_content = [
        "          Click to add tags...        ",
        " en             \uf60f \uf044",
    ]  # "          Click to add tags...        "

    return split_app_text(text, begin_tags, end_tags, removable_content, ignore_until_begin=True)

import re
_DIALOG_RE = re.compile(r'([.!?])\s+(["\u201C])')

def add_newlines_before_quotes(text: str) -> str:

    """
    Insert a blank line before a quoted dialogue that follows a period,
    question mark or exclamation mark.

    Example:
        He said. "Hello!" -> He said.\n\n"Hello!"
    """
    # The replacement keeps the punctuation (group 1) and inserts two newlines before the quote.
    return _DIALOG_RE.sub(r'\1\n\n\2', text)

def split_chatgpt_text(text):
    """
    Splits the text into blocks based on the begin and end tags; content can
    have multiple begin and end tags.
    text: text content to split
    """
    end_tags = ["ChatGPT said:", "4o mini    "]
    begin_tags = "You said:"

    removable_content = (
        "Ask anything            Search    Reason         ChatGPT can make mistakes.",
        "ChatGPT  Share      ",
        "Skip to content Chat history      New chat Ctrl +  Shift +  O  Search chats Ctrl +  K  Images   Apps  Codex   Projects  New project   Elissa    Recent Demon Lord Elissa Theory     Cosmic Horror Character Evolution     Ontological Carryover and Souls     Elissa Skylark memory     Ugh Moments      Aria    Your chats  !Uncommon Talents Wanted     Buffyverse part 3     Worm PbP RPG Guide     The Vanishing Noodles     Solo PBP Cold Open     Elissa BtvS 1     Elissa in YJ Part 4     Mutants & Masterminds Game     Elissa Skylark Character Analysis     Aria Skylark in WH40k     Elissa in Alien scenario     Game postmortem analysis     Dark Fantasy Worldbuilding     Multidimensional Chaos Encounter     Elissa Skylark Inference     Elissa: Rainbow Rift Arrival- Gravity Falls     Conversation greeting     Elissa in A!MS     Supernatural Part 2     Elissa Fate Hazbin Hotel     Sword of Choice DF 3     Body Sharing Dynamics Analysis     Boost Converter for Solar     Magic System Workarounds     FSK Transmission Debugging     Re-add routes Windows Server     Pysdl3 sine wave example     Summarize conversation request     Mains hum noise reduction     Dynamic Sorcery Power Scaling     Fractal Gem Hero Journey     Sailor Moon SI 2     Session reuse with Playwright     Python 3.6 dotenv module     Dockerfile Optimization Help     Energy Expenditure and Speed     Aria, Tenchi Muyo 2     Aria, NGE ...3     GeoServer CSRF 400 Error     Character Analysis and Comedy     Harley Meets Soulbird     Elissa in YJ Part 3     Character Description Request     BESM Deal with Devil     Aiden's Escape Investigation     Elissa Skylark in YJ part 2     Elissa Skylark Character Review     Elissa Skylark in YJ     Character Breakdown RPG Analysis     Elissa Skylark CoC Adventure     Spacetime Entity Containment     Hellsing RPG Setup     Fractal Waveform SI Suggestions     Elissa Skylark Power Struggle     Funny LitRPG Abridged Help     Dresden Files SI part 2     Dresden Files SI Adventure     Vampire Hunt Collaboration     BESM Character Evaluation     Story to Script Conversion     Script Formatting Request     Tenth Doctor Encounter     Sailor Moon SI Setup     Divergent Tenchi Muyo Plot     Elissa Tenchi Muyo Locations     Elissa Meets the Winchesters     Elissa's Buffyverse Journey     Aria Skylark Choices     Tekoälyn dementia Solomon-asemalla     Artifact Encounter Design     Cyberpunk Cthulhu RPG Adventure     Aria Skylark in EVA     Good Bad Card Events     Washuu's New Creation     Improving Story Continuity     Comprehensible Echo Character Breakdown     Nexus Adventure Proposal     Echo Fanfic Settings     Divergent Tenchi Muyo Summary     Echo's Emergence and Growth     Falling Into Tenchi Muyo     Story Draft Summary     Isekai Character Analysis     Aria's Dimensional Disorientation     Aria Self Discovery Summary     Aria's Galactic Adventure     Tenko's Origins and Growth         Esa Karjalainen Free  Upgrade       Free offer     ChatGPT  Share     "
    )
    return split_app_text(text, begin_tags, end_tags, removable_content)


def get_name_by_app(app, **kwargs):
    name = ">>>"
    if app == "chatgpt":
        if "index" in kwargs:
            i = kwargs["index"]
            name = "User" if not is_even(i) else "LLM"

    return name


def split_app_content(content, app="chatgpt", custom_function=None, ensure_newlines=False):
    functions = {
        "chatgpt": split_chatgpt_text,
        "joplin": split_joplin_text,
    }
    if custom_function:  # add custom function
        functions[app] = custom_function

    logger.info("Content length: " + str(len(content)))
    for text in content:

        blocks = functions[app](text)
        blocks = [block for block in blocks if len(block) > 0]

        for i, block in enumerate(blocks):
            name = get_name_by_app(app, index=i)
            if ensure_newlines:
                text = add_newlines_before_quotes(text)
            yield (name, block, i)


def is_even(n):
    return n % 2 == 0


# Example usage
if __name__ == "__main__":
    # keyboard.add_hotkey("ctrl+shift+alt+a", get_active_window)
    # keyboard.add_hotkey("ctrl+shift+esc", exit)
    # foo = "a" if is_even(0) else "b"
    # assert foo == "a"
    # exit()

    sleep(1)
    browser = None
    while True:
        print(get_active_window().title.lower())
        sleep(3)
        title = str(get_active_window().title).replace(" ", "_")
        title = title.replace(",", "")
        print(title)
        if browser := is_browser_window(get_active_window()):
            break
    content = get_active_browser_content()
    print(content[:200])
    print("-" * 50)
    # for name, block, i in split_app_content(content, browser):
    #    print(f"{i}: {name}: {block[:80]}\n")
    # print("-" * 50)
