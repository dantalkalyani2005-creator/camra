from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class DocumentWord:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass
class DocumentLine:
    page: int
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    words: List[DocumentWord] = field(default_factory=list)


def _group_words_into_lines(
    words: List[DocumentWord],
    page_number: int,
) -> List[DocumentLine]:

    if not words:
        return []

    words = sorted(
        words,
        key=lambda word: (
            word.y0,
            word.x0,
        ),
    )

    groups: List[List[DocumentWord]] = []

    for word in words:

        center_y = (
            word.y0 + word.y1
        ) / 2

        best_group = None
        best_distance = None

        for group in groups:

            group_y = sum(
                (item.y0 + item.y1) / 2
                for item in group
            ) / len(group)

            distance = abs(
                center_y - group_y
            )

            # Medical PDFs normally keep words belonging
            # to the same visual row very close vertically.
            tolerance = max(
                4.0,
                min(
                    word.y1 - word.y0,
                    14.0,
                ),
            )

            if distance <= tolerance:

                if (
                    best_distance is None
                    or distance < best_distance
                ):
                    best_group = group
                    best_distance = distance

        if best_group is None:
            groups.append([word])
        else:
            best_group.append(word)

    lines: List[DocumentLine] = []

    for group in groups:

        group.sort(
            key=lambda word: word.x0
        )

        text = " ".join(
            word.text
            for word in group
        ).strip()

        if not text:
            continue

        lines.append(
            DocumentLine(
                page=page_number,
                text=text,
                x0=min(word.x0 for word in group),
                y0=min(word.y0 for word in group),
                x1=max(word.x1 for word in group),
                y1=max(word.y1 for word in group),
                words=group,
            )
        )

    lines.sort(
        key=lambda line: (
            line.y0,
            line.x0,
        )
    )

    return lines


def build_document_lines_from_pdf(
    file_bytes: bytes,
) -> List[DocumentLine]:

    """
    Convert a PDF into layout-aware lines.

    Important:
    Text is reconstructed from individual PDF words instead
    of trusting the PDF's internal block/line ordering.

    This is critical for reports where a row is visually:

        Parameter        Result        Unit        Reference

    but the PDF internally stores each column separately.
    """

    import fitz

    document = fitz.open(
        stream=file_bytes,
        filetype="pdf",
    )

    all_lines: List[DocumentLine] = []

    try:

        for page_number, page in enumerate(
            document,
            start=1,
        ):

            words = []

            raw_words = page.get_text(
                "words"
            )

            for item in raw_words:

                if len(item) < 5:
                    continue

                x0, y0, x1, y1, text = item[:5]

                text = str(text).strip()

                if not text:
                    continue

                words.append(
                    DocumentWord(
                        text=text,
                        x0=float(x0),
                        y0=float(y0),
                        x1=float(x1),
                        y1=float(y1),
                    )
                )

            page_lines = _group_words_into_lines(
                words,
                page_number,
            )

            all_lines.extend(
                page_lines
            )

    finally:
        document.close()

    all_lines.sort(
        key=lambda line: (
            line.page,
            line.y0,
            line.x0,
        )
    )

    return all_lines