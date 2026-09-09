from __future__ import annotations

from io import BytesIO
from typing import List

import pytesseract
from PIL import Image
from pytesseract import Output

from app.services.ocr.layout import DocumentLine, DocumentWord


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Backwards-compatible OCR function.

    Returns plain text while keeping the existing API used elsewhere
    in the backend.
    """

    image = Image.open(BytesIO(file_bytes))

    text = pytesseract.image_to_string(
        image,
        config="--psm 6",
    )

    return text.strip()


def extract_layout_from_image(
    file_bytes: bytes,
    page_number: int = 1,
) -> List[DocumentLine]:
    """
    OCR an image while preserving word positions.

    This is the image equivalent of the PDF layout extractor.
    """

    image = Image.open(BytesIO(file_bytes))

    data = pytesseract.image_to_data(
        image,
        config="--psm 6",
        output_type=Output.DICT,
    )

    grouped = {}

    count = len(data["text"])

    for i in range(count):

        text = data["text"][i].strip()

        if not text:
            continue

        try:
            confidence = float(data["conf"][i])
        except (ValueError, TypeError):
            confidence = -1

        if confidence < 0:
            continue

        block_num = data["block_num"][i]
        par_num = data["par_num"][i]
        line_num = data["line_num"][i]

        key = (
            block_num,
            par_num,
            line_num,
        )

        x = float(data["left"][i])
        y = float(data["top"][i])
        width = float(data["width"][i])
        height = float(data["height"][i])

        word = DocumentWord(
            text=text,
            x0=x,
            y0=y,
            x1=x + width,
            y1=y + height,
        )

        grouped.setdefault(key, []).append(word)

    lines: List[DocumentLine] = []

    for words in grouped.values():

        if not words:
            continue

        words.sort(key=lambda word: word.x0)

        text = " ".join(
            word.text for word in words
        ).strip()

        if not text:
            continue

        lines.append(
            DocumentLine(
                page=page_number,
                text=text,
                x0=min(word.x0 for word in words),
                y0=min(word.y0 for word in words),
                x1=max(word.x1 for word in words),
                y1=max(word.y1 for word in words),
                words=words,
            )
        )

    lines.sort(
        key=lambda line: (
            line.y0,
            line.x0,
        )
    )

    return lines