"""
Text chunking utilities for long training materials (PDF/transcripts/notes).
"""

from typing import List, Dict, Any
import re


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> List[Dict[str, Any]]:
    """
    Split long text into overlapping chunks.
    chunk_size/overlap are character-based for simplicity and language neutrality.
    """
    text = (text or "").strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [{"index": 0, "content": text}]

    # Prefer splitting on paragraph/sentence boundaries when possible
    parts = re.split(r"\n{2,}|(?<=[.!?؟])\s+", text)
    parts = [p.strip() for p in parts if p and p.strip()]

    chunks: List[str] = []
    buf = ""

    for part in parts:
        if not buf:
            buf = part
            continue

        if len(buf) + 1 + len(part) <= chunk_size:
            buf = f"{buf} {part}".strip()
        else:
            chunks.append(buf)
            # overlap from end of previous buffer
            if overlap > 0 and len(buf) > overlap:
                tail = buf[-overlap:]
                buf = f"{tail} {part}".strip()
            else:
                buf = part

    if buf:
        chunks.append(buf)

    # Final hard split for any oversized chunk
    final: List[Dict[str, Any]] = []
    idx = 0
    for ch in chunks:
        if len(ch) <= chunk_size:
            final.append({"index": idx, "content": ch})
            idx += 1
        else:
            start = 0
            while start < len(ch):
                end = min(len(ch), start + chunk_size)
                final.append({"index": idx, "content": ch[start:end]})
                idx += 1
                if end >= len(ch):
                    break
                start = max(0, end - overlap)

    return final
