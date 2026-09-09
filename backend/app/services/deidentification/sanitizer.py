from __future__ import annotations

import re


# ============================================================
# Direct identifiers
# ============================================================

EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.I,
)

URL_RE = re.compile(
    r"\b(?:https?://|www\.)[^\s]+",
    re.I,
)

IP_RE = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)

SSN_RE = re.compile(
    r"\b\d{3}-\d{2}-\d{4}\b"
)


# ============================================================
# Dates
# ============================================================

DATE_RE = re.compile(
    r"\b(?:"
    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
    r"|"
    r"\d{1,2}\s+"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|"
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s+\d{2,4}"
    r"|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|"
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s+\d{1,2},?\s+\d{2,4}"
    r")\b",
    re.I,
)


LABELED_IDENTIFIER_RE = re.compile(
    r"(?i)"
    r"("
    r"\b(?:"
    r"Patient|Sample|Specimen|Medical\s+Record|MRN|Lab|"
    r"Case|Registration|Certificate|License|Account|Member|"
    r"Beneficiary|Policy|Claim|Health\s+Plan|Insurance|"
    r"Device|Serial|Vehicle"
    r")"
    r"\s*(?:Code|ID|No\.?|Number)"
    r"\s*[:#-]?\s*"
    r")"
    r"([A-Za-z0-9./_-]+)"
)


NAME_RE = re.compile(
    r"(?i)"
    r"("
    r"\b(?:Patient\s+Name|Name\s+of\s+Patient|Billing\s+To)"
    r"\s*[:\-]?\s*"
    r")"
    r"([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,4})"
)


ADDRESS_RE = re.compile(
    r"(?i)"
    r"("
    r"\b(?:Address|Residential\s+Address|Home\s+Address|"
    r"Permanent\s+Address)"
    r"\s*[:\-]?\s*"
    r")"
    r"([^\n]+)"
)


PHONE_RE = re.compile(
    r"(?i)"
    r"("
    r"\b(?:Phone|Telephone|Mobile|Contact)"
    r"\s*[:\-]?\s*"
    r")"
    r"(\+?\d[\d\s().-]{7,}\d)"
)


FAX_RE = re.compile(
    r"(?i)"
    r"("
    r"\b(?:Fax|Facsimile)"
    r"\s*[:\-]?\s*"
    r")"
    r"(\+?\d[\d\s().-]{5,}\d)"
)


# ============================================================
# Other obvious identifier values
# ============================================================

# Common medical/report identifiers such as:
# P26000012
# S26000009
# MR123456
IDENTIFIER_VALUE_RE = re.compile(
    r"\b[A-Za-z]{1,6}\d{5,}\b"
)

# Long standalone numeric identifiers.
LONG_NUMBER_RE = re.compile(
    r"\b\d{7,}\b"
)


# ============================================================
# Document noise
# ============================================================

PAGE_NUMBER_RE = re.compile(
    r"(?im)^\s*Page\s+\d+\s+of\s+\d+\s*$"
)


# ============================================================
# Sanitizer
# ============================================================

def sanitize_text(text: str) -> str:
    """
    Sanitize the complete extracted report text.

    The input is treated as one text string.
    No layout reconstruction.
    No medical interpretation.
    No section categorization.
    """

    text = str(text or "")

    # Direct identifiers
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = URL_RE.sub("[URL]", text)
    text = IP_RE.sub("[IP]", text)
    text = SSN_RE.sub("[IDENTIFIER]", text)

    # Labeled identifiers
    text = LABELED_IDENTIFIER_RE.sub(
        lambda m: m.group(1) + "[IDENTIFIER]",
        text,
    )
    
    text = NAME_RE.sub(
        lambda m: m.group(1) + "[NAME]",
        text,
    )
    
    text = ADDRESS_RE.sub(
        lambda m: m.group(1) + "[ADDRESS]",
        text,
    )
    
    text = PHONE_RE.sub(
        lambda m: m.group(1) + "[PHONE]",
        text,
    )
    
    text = FAX_RE.sub(
        lambda m: m.group(1) + "[FAX]",
        text,
    )

    # Dates
    text = DATE_RE.sub("[DATE]", text)

    # Obvious identifier values
    text = IDENTIFIER_VALUE_RE.sub("[IDENTIFIER]", text)
    text = LONG_NUMBER_RE.sub("[IDENTIFIER]", text)

    # Document noise
    text = PAGE_NUMBER_RE.sub("", text)

    # Clean excessive blank lines only.
    text = re.sub(r"\n[ \t]*\n+", "\n\n", text)

    return text.strip()