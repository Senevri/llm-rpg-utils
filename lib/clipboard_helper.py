#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extract a ChatGPT conversation (assistant + user) from the Windows clipboard
and write a readable Markdown transcript.

Requirements:
    pip install beautifulsoup4 pywin32
"""

import re
import win32clipboard
import win32con
from pathlib import Path
from bs4 import BeautifulSoup


# ----------------------------------------------------------------------
# 1️⃣ Helper: turn the raw HTML clipboard payload into a plain HTML string
# ----------------------------------------------------------------------
def _strip_html_clipboard(raw_bytes: bytes) -> str:
    """
    The Windows “HTML Format” clipboard contains a small header that tells
    where the actual HTML starts and ends.  This function extracts the
    substring between those offsets and decodes it as UTF‑8.
    """
    header, _, _ = raw_bytes.partition(b'\r\n\r\n')
    start_match = re.search(br'StartHTML:(\d+)', header)
    end_match   = re.search(br'EndHTML:(\d+)', header)

    if not (start_match and end_match):
        raise ValueError("Malformed HTML clipboard header")

    start = int(start_match.group(1))
    end   = int(end_match.group(1))
    return raw_bytes[start:end].decode('utf-8', errors='replace')


# ----------------------------------------------------------------------
# 2️⃣ Main clipboard‑reading routine
# ----------------------------------------------------------------------
def get_transcript_from_clipboard() -> str:
    """
    Returns the **Markdown transcript** of the most recent ChatGPT export
    that lives on the clipboard.  If the clipboard only contains plain text,
    that text is returned unchanged (still wrapped in our transcript format).
    """
    win32clipboard.OpenClipboard()
    try:
        html_fmt = win32clipboard.RegisterClipboardFormat('HTML Format')
        if win32clipboard.IsClipboardFormatAvailable(html_fmt):
            raw = win32clipboard.GetClipboardData(html_fmt)          # bytes
            html = _strip_html_clipboard(raw)
        else:
            # Fallback – plain Unicode text (no HTML markup)
            html = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)

        # Convert the HTML (or plain text) into a transcript
        return _html_to_transcript(html)
    finally:
        win32clipboard.CloseClipboard()


# ----------------------------------------------------------------------
# 3️⃣ Core extraction logic – walks the soup **once** and respects order
# ----------------------------------------------------------------------
def _html_to_transcript(html: str, keep_offsets: bool = False) -> str:
    """
    Takes the raw HTML string produced by ChatGPT’s export and returns a
    Markdown‑style transcript:

        🤖 ASSISTANT:
        …assistant text…

        🗨️ USER:
        …user text…

    Parameters
    ----------
    html : str
        The full HTML page (or a fragment) copied from ChatGPT.
    keep_offsets : bool
        If True, prepend each assistant paragraph with its `[start‑end]`
        offset that appears in the original `data-start` / `data-end`
        attributes.  Handy for debugging or aligning with the source file.

    Returns
    -------
    str
        The assembled transcript.
    """
    soup = BeautifulSoup(html, "html.parser")

    # The final ordered list of (speaker, text) tuples
    conversation: list[tuple[str, str]] = []
    current_assistant_div= None
    assistant_conversation_block = None

    # Walk the tree depth‑first; this respects the natural document order.
    for elem in soup.descendants:
        if not getattr(elem, "attrs", None):
            # print(elem)
            continue  # skip NavigableString objects – we only care about tags


        classes = elem.get("class", [])
        # --------------------------------------------------------------
        # Assistant paragraphs – they live inside <div class="markdown prose …">
        # --------------------------------------------------------------
        if "markdown" in classes and "prose" in classes and elem.name == "div":
            current_assistant_div = elem
            assistant_conversation_block = ("assistant", "")  # placeholder; we'll fill in the text later
            continue

        if elem.name == "p" and current_assistant_div is not None:
            # Collapse inner whitespace to a single space (so line‑breaks inside <p> become normal spaces)
            txt = elem.get_text(separator=" ", strip=True)

            if keep_offsets:
                start = elem.get("data-start")
                end   = elem.get("data-end")
                if start and end:
                    txt = f"[{start}-{end}] {txt}"
            assistant_conversation_block = ("assistant", assistant_conversation_block[1] + txt + "\n")
            continue

        # --------------------------------------------------------------
        # User messages – the inner <div class="whitespace-pre-wrap">
        # --------------------------------------------------------------
        elif "whitespace-pre-wrap" in classes:
            if assistant_conversation_block is not None:
                conversation.append(assistant_conversation_block)
                assistant_conversation_block = None
            current_assistant_div = None
            # Preserve line breaks that were originally rendered as   or actual \n
            txt = elem.get_text(separator="\n", strip=True)
            conversation.append(("user", txt))

    # ------------------------------------------------------------------
    # Assemble the final Markdown transcript
    # ------------------------------------------------------------------
    out_lines: list[str] = []
    for speaker, text in conversation:
        prefix = "🗨️ USER:" if speaker == "user" else "🤖 ASSISTANT:"
        out_lines.append(f"{prefix}\n{text}\n")
    return "\n".join(out_lines)


# ----------------------------------------------------------------------
# 4️⃣ Command‑line entry point – write the transcript to a file
# ----------------------------------------------------------------------
if __name__ == "__main__":
    transcript = get_transcript_from_clipboard()

    # Choose where you want the output; change the path as needed.
    output_path = Path("clipboard_output.md")
    output_path.write_text(transcript, encoding="utf-8")
    print(f"✅ Transcript written to {output_path.resolve()}")