from __future__ import annotations

import fitz


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF as one continuous string.

    No layout reconstruction.
    No table parsing.
    No medical interpretation.
    """
    document = fitz.open(stream=file_bytes, filetype="pdf")

    try:
        pages = []

        for page in document:
            text = page.get_text("text")
            if text:
                pages.append(text)

        return "\n".join(pages).strip()

    finally:
        document.close()