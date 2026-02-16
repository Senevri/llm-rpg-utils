

import win32clipboard, win32con, re
from bs4 import BeautifulSoup
from pathlib import Path


def _strip_html_clipboard(raw_bytes: bytes) -> str:
    """
    The HTML clipboard format contains a header with StartHTML/EndHTML offsets.
    This function extracts the pure HTML payload.
    """
    header, _, _ = raw_bytes.partition(b'\r\n\r\n')
    start = int(re.search(br'StartHTML:(\d+)', header).group(1))
    end   = int(re.search(br'EndHTML:(\d+)', header).group(1))
    return raw_bytes[start:end].decode('utf-8', errors='replace')


def get_html_from_clipboard() -> str:
    win32clipboard.OpenClipboard()
    try:
        html_fmt = win32clipboard.RegisterClipboardFormat('HTML Format')
        if win32clipboard.IsClipboardFormatAvailable(html_fmt):
            raw = win32clipboard.GetClipboardData(html_fmt)  # bytes
            return convert_to_markdown(_strip_html_clipboard(raw))
        # Fallback to plain‑text if HTML isn’t present
        txt = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        return convert_to_markdown(txt)
    finally:
        win32clipboard.CloseClipboard()

def convert_to_markdown(html: str) -> str:
    # Placeholder for HTML to Markdown conversion logic
    # html=html.read_text(encoding="utf-8")
    plain = "\n\n".join(p.get_text(strip=True) for p in BeautifulSoup(html, "html.parser").select("p"))
    return plain

if __name__ == '__main__':
    # Save to file
    html = get_html_from_clipboard()
    output_path = Path("clipboard_output.md")
    output_path.write_text(html)