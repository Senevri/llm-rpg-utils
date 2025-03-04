from math import e
import re
import pygetwindow as gw
import logging
import keyboard
from time import sleep
from pywinauto import Application, WindowSpecification, Desktop
from pprint import pformat, pprint
from gettext import find
from custom_logger import get_custom_logger
from bs4 import BeautifulSoup

logger = get_custom_logger(__file__, "browser_util", add_date=False, console=True)

browsers = ["chrome", "firefox", "edge", "opera", "thorium", "brave", "safari", "joplin"]


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
    )
    return split_app_text(text, begin_tags, end_tags, removable_content)


def get_name_by_app(app, **kwargs):
    name = ">>>"
    if app == "chatgpt":
        if "index" in kwargs:
            i = kwargs["index"]
            name = "User" if is_even(i) else "LLM"

    return name


def split_app_content(content, app="chatgpt", custom_function=None):
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
