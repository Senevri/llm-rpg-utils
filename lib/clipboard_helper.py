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
from typing import List, Tuple
from html_to_markdown import convert as html_to_md

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

def put_content_on_clipboard(content):
    win32clipboard.OpenClipboard()
    try:
        _format = win32clipboard.RegisterClipboardFormat("HTML Format")
        win32clipboard.SetClipboardData(_format, content)
    finally:
        win32clipboard.CloseClipboard()

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

def get_markdown_from_clipboard():
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
        return html_to_md(html).content
    finally:
        win32clipboard.CloseClipboard()




def normalize_hr(md: str) -> str:
    """
    Ensure every ``---`` that separates blocks is surrounded by a blank line.
    If the rule already has two new‑lines before it, it is left untouched.

    The pattern works for both Unix (\\n) and Windows (\\r\\n) line endings.
    """
    # 1️⃣  Rule that is **not** already preceded by a blank line
    #     (?<!\\n\\n)   – negative look‑behind (no two newlines)
    #     (^|(?<=\\n))  – start of file or a single newline before the rule
    #     (?P<hr>---)   – capture the three dashes
    #     (\\r?\\n)     – the line‑break after the rule
    #     (?=#+)        – the next line must start with a heading (##, ### …)
    pattern = re.compile(
        r'(?<!\n\n)(^|(?<=\n))(?P<hr>---)(\r?\n)(?=#+)',
        flags=re.MULTILINE,
    )
    # Replace with two newlines + the rule + the original line‑break
    md = pattern.sub(r'\n\n\g<hr>\n', md)

    # 2️⃣  Catch the rare case where the rule is at the very end of the file
    #     (no heading after it).  We still want a blank line before it.
    md = re.sub(r'(?<!\n\n)(?P<hr>---)(\r?\n)$', r'\n\n\g<hr>\n', md, flags=re.MULTILINE)

    # Replace with: two newlines + the rule + the original line‑break

    user_txt = pattern.sub(r'\n\n\g<hr>\n', md)
    user_txt= re.sub(r'.\n---', '\n\n---', user_txt)
    hr_pattern="\n---\n"
    indexof_hr = user_txt.find(hr_pattern)

    if indexof_hr != -1:
        if user_txt[indexof_hr-1] != "\n":
            user_txt = user_txt.replace(hr_pattern, f"\n{hr_pattern}")

    return user_txt

# ----------------------------------------------------------------------
# 3️⃣ Core extraction logic – walks the soup **once** and respects order
# ----------------------------------------------------------------------


def _html_to_transcript(html: str, keep_offsets: bool = False) -> str:
    """
    Convert a ChatGPT export (HTML) into a numbered Markdown transcript.
    Handles:
        • bold (**), italic (*)
        • headings (# …)
        • ordered / unordered lists
        • horizontal rules (---)
        • line breaks ( )
        • optional [start‑end] offsets
    """
    soup = BeautifulSoup(html, "html.parser")

    conversation: List[Tuple[str, str]] = []          # (speaker, text)
    assistant_buf: List[str] = []                    # collects lines for the current assistant turn
    inside_assistant = False                         # are we inside <div class="markdown prose …"> ?

    # ------------------------------------------------------------------
    # Helper – flush the current assistant buffer into the conversation
    # ------------------------------------------------------------------
    def flush_assistant():
        if assistant_buf:
            conversation.append(("assistant", "".join(assistant_buf).rstrip()))
            assistant_buf.clear()


    # ------------------------------------------------------------------
    # Walk the tree in document order (depth‑first)
    # ------------------------------------------------------------------
    for elem in soup.descendants:
        # Skip plain strings – we only care about Tag objects
        prefix = ""

        if not getattr(elem, "attrs", None):
            continue

        classes = elem.get("class", [])
        role = elem.get("data-conversation-role", "") # Very chatgpt specific
        textstyle = elem.get("data-markdown-text-style")
        # --------------------------------------------------------------
        # 1️⃣  Detect the start of an assistant container
        # --------------------------------------------------------------

        if textstyle == "assistant-message":
        #     #find first div with paragraph
        #     #elem = elem.find("p").findParent("div")
        #     inside_assistant=True
        # if (elem.name=="div" and any("prose" in e.lower() for e in classes)
        #     and not any("user-message" in e.lower() for e in classes)):
            #or elem.name == "div" and "Markdown" in classes and "prose" in classes:)
        # if (elem.name == "div" and "prose" in classes):
            if not inside_assistant:
                flush_assistant()  # Close any pending assistant block before starting a new one
            inside_assistant=True

            transcript = html_to_md(elem.decode_contents()).content
            transcript = transcript.strip()
            if transcript:
                if len(conversation)>0:
                    if conversation[-1][0]=="assistant":
                        continue
                # transcript.replace(f".\n---", f".\n\n---")
                # transcript.replace("---\n", "\n---\n")
                transcript = normalize_hr(transcript)
            #    if transcript != conversation[-1]:
                conversation.append(("assistant", transcript))
            continue

        # --------------------------------------------------------------
        # 3️⃣  User bubbles – they are outside the assistant container
        # --------------------------------------------------------------
        #if "whitespace-pre-wrap" in classes or "user-message" in classes:
        if (any("user-message" in e.lower() for e in classes)
            or any("bubble" in e.lower() for e in classes)):
            # Close any pending assistant block before we record the user text
            if inside_assistant:
                flush_assistant()
            inside_assistant = False

            # Preserve line breaks exactly as they appear in the HTML
            user_md = elem.get_text(separator="\n", strip=False)

            if len(conversation)>0:
                if conversation[-1][0]=="user":
                    continue

            # Add paragraph breaks
            user_md = user_md.replace("\"  ", "\"\n\n")

            # Other formatting rules?

            # Ensure that horizontal rules (---) are on their own lines
            user_md = normalize_hr(user_md)
            #if len(conversation) < 1 or user_md != conversation[-1]:
            conversation.append(("user", user_md))
            continue

    # ------------------------------------------------------------------
    # End of document – flush any remaining assistant text
    # ------------------------------------------------------------------
    flush_assistant()

    # ------------------------------------------------------------------
    # 4️⃣  Assemble the final numbered Markdown transcript
    # ------------------------------------------------------------------
    out_lines: List[str] = []
    last_speaker = None
    idx = 1
    for speaker, text in conversation:
        if speaker != last_speaker:
            idx += 1
            prefix = "🗨️ USER:" if speaker == "user" else "🤖 ASSISTANT:"
            prefix = f"\n## {idx} " + prefix + "\n"
        else:
            prefix=""
        out_lines.append(f"{prefix}{text}\n")
        last_speaker=speaker

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