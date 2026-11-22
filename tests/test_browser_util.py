from time import sleep
import sys
from pathlib import Path
import html

src = Path.cwd().resolve()
if src not in sys.path:
    sys.path.append(str(src))

from lib.browser_util import (
    get_active_browser_content,
    is_browser_window,
    get_active_window,
    get_active_browser_documents,
    get_window_as_markdown
    )
from html_to_markdown import convert

print("Ready!")
sleep(2)
active_window = get_active_window()
print("is browser: %s", is_browser_window(active_window))
#content = get_active_browser_content()
import inspect
from pprint import pprint

import html
print(get_window_as_markdown(active_window))

#hacktime