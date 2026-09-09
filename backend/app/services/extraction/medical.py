from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from app.services.ocr.layout import DocumentLine


NUMBER_RE = re.compile(r"[-+]?\d+(?:[.,]\d+)?")

AGE_RE = re.compile(
    r"(?i)\bage\s*[:\-]?\s*(\d{1,3})\s*(?:years?|yrs?)?"
)

SEX_RE = re.compile(
    r"(?i)\b(?:sex|gender)\s*[:\-]?\s*(male|female|m|f|other)\b"
)

HEIGHT_RE = re.compile(
    r"(?i)\bheight\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(cm|m|ft|feet|in|inch|inches)?"
)

WEIGHT_RE = re.compile(
    r"(?i)\bweight\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(kg|kgs|lb|lbs|pound|pounds)?"
)


# ============================================================
# BASIC HELPERS
# ============================================================

def clean(text: str) -> str:
    text = str(text or "")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def norm(text: str) -> str:
    return clean(text).lower().replace("–", "-").replace("—", "-")


def number(text: str) -> Optional[float]:
    try:
        return float(str(text).replace(",", "").strip())
    except Exception:
        return None


def first_number(text: str) -> Optional[float]:
    match = NUMBER_RE.search(text or "")
    if not match:
        return None
    return number(match.group(0))


def is_dash(text: str) -> bool:
    return norm(text) in {
        "",
        "-",
        "--",
        "—",
        "–",
        "n/a",
        "na",
    }


# ============================================================
# REFERENCE / STATUS
# ============================================================

def parse_reference(text: str) -> Optional[Dict[str, Any]]:
    text = clean(text)

    match = re.match(
        r"^\s*(>=|>|<=|<)\s*"
        r"([-+]?\d+(?:[.,]\d+)?)"
        r"\s*(.*)$",
        text,
    )

    if match:
        value = number(match.group(2))

        if value is None:
            return None

        return {
            "type": "threshold",
            "operator": match.group(1),
            "value": value,
            "raw": text,
        }

    match = re.match(
        r"^\s*"
        r"([-+]?\d+(?:[.,]\d+)?)"
        r"\s*(?:-|to)\s*"
        r"([-+]?\d+(?:[.,]\d+)?)"
        r"\s*(.*)$",
        text,
        re.I,
    )

    if match:
        low = number(match.group(1))
        high = number(match.group(2))

        if low is None or high is None:
            return None

        return {
            "type": "range",
            "low": low,
            "high": high,
            "raw": text,
        }

    return None


def calculate_status(
    value: Optional[float],
    reference: Optional[str],
) -> Optional[str]:

    if value is None or not reference:
        return None

    parsed = parse_reference(reference)

    if not parsed:
        return None

    if parsed["type"] == "range":

        if value < parsed["low"]:
            return "low"

        if value > parsed["high"]:
            return "high"

        return "normal"

    operator = parsed["operator"]
    target = parsed["value"]

    if operator == ">=":
        return "normal" if value >= target else "low"

    if operator == ">":
        return "normal" if value > target else "low"

    if operator == "<=":
        return "normal" if value <= target else "high"

    if operator == "<":
        return "normal" if value < target else "high"

    return None


# ============================================================
# PATIENT DATA
# ============================================================

def extract_patient_data(
    lines: List[DocumentLine],
) -> Dict[str, Any]:

    data = {
        "age": None,
        "sex": None,
        "height_cm": None,
        "weight_kg": None,
        "symptoms": [],
        "medical_history": [],
        "medications": [],
        "additional_information": "",
    }

    text = "\n".join(clean(line.text) for line in lines)

    match = AGE_RE.search(text)

    if match:
        value = number(match.group(1))

        if value is not None:
            data["age"] = int(value)

    match = SEX_RE.search(text)

    if match:
        value = match.group(1).lower()

        if value in {"m", "male"}:
            data["sex"] = "male"
        elif value in {"f", "female"}:
            data["sex"] = "female"
        else:
            data["sex"] = value

    match = HEIGHT_RE.search(text)

    if match:
        value = number(match.group(1))
        unit = (match.group(2) or "cm").lower()

        if value is not None:

            if unit == "m":
                value *= 100

            elif unit in {"ft", "feet"}:
                value *= 30.48

            elif unit in {"in", "inch", "inches"}:
                value *= 2.54

            data["height_cm"] = round(value, 2)

    match = WEIGHT_RE.search(text)

    if match:
        value = number(match.group(1))
        unit = (match.group(2) or "kg").lower()

        if value is not None:

            if unit in {"lb", "lbs", "pound", "pounds"}:
                value *= 0.45359237

            data["weight_kg"] = round(value, 2)

    return data


# ============================================================
# REPORT TITLE
# ============================================================

def find_title(lines: List[DocumentLine]) -> str:

    candidates = []

    for line in lines[:30]:

        text = clean(line.text)

        if not text:
            continue

        if ":" in text:
            continue

        if any(char.isdigit() for char in text):
            continue

        words = text.split()

        if len(words) < 2 or len(words) > 12:
            continue

        score = 0

        if text.upper() == text:
            score += 10

        if "report" in norm(text):
            score += 5

        if len(words) >= 3:
            score += 2

        candidates.append((score, text))

    if not candidates:
        return ""

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates[0][1]


# ============================================================
# REPORT TYPE
# ============================================================

def classify_report(
    title: str,
    lines: List[DocumentLine],
) -> str:

    text = (
        title
        + "\n"
        + "\n".join(clean(line.text) for line in lines[:150])
    ).lower()

    if any(
        x in text
        for x in [
            "x-ray",
            "xray",
            "ultrasound",
            "sonography",
            "ct scan",
            "mri",
            "radiology",
        ]
    ):
        return "imaging"

    if any(
        x in text
        for x in [
            "histopathology",
            "biopsy",
            "pathology",
        ]
    ):
        return "pathology"

    if any(
        x in text
        for x in [
            "ecg",
            "ekg",
            "echocardiogram",
            "cardiology",
        ]
    ):
        return "cardiology"

    if any(
        x in text
        for x in [
            "laboratory",
            "lab report",
            "blood",
            "urine",
            "sperm",
            "morphology",
            "dna fragmentation",
        ]
    ):
        return "laboratory"

    return "medical_report"


# ============================================================
# STRUCTURAL HEADINGS
# ============================================================

STRUCTURAL_HEADINGS = {
    "patient information",
    "sample information",
    "general information",
    "results",
    "result",
    "morphology examination",
    "vitality",
    "additional findings",
    "dna fragmentation",
    "dna fragmentation index reference",
    "halo classification",
    "comments",
    "laboratory remarks",
    "findings",
    "impression",
    "conclusion",
    "observations",
    "interpretation",
}


def is_heading(text: str) -> bool:

    value = norm(text)

    if value in STRUCTURAL_HEADINGS:
        return True

    return False


# ============================================================
# RESULT ROW RECOGNITION
# ============================================================

def is_result_name(text: str) -> bool:

    value = norm(text)

    if not value:
        return False

    if is_dash(value):
        return False

    if value in {
        "parameter",
        "result",
        "unit",
        "count",
        "cells",
        "normal",
        "excellent",
        "good",
        "fair",
        "poor",
    }:
        return False

    if value.startswith("page "):
        return False

    if value.startswith("patient's"):
        return False

    # A result name should not itself be numeric.
    if first_number(value) is not None:
        return False

    return True


def make_result(
    name: str,
    value_text: str,
    unit: Optional[str],
    reference: Optional[str],
) -> Optional[Dict[str, Any]]:

    name = clean(name)
    value_text = clean(value_text)

    if not name or not value_text:
        return None

    if is_dash(value_text):
        return None

    numeric = first_number(value_text)

    result = {
        "test": name,
        "value": numeric if numeric is not None else value_text,
        "unit": clean(unit) if unit else None,
        "reference_range": clean(reference) if reference else None,
    }

    status = calculate_status(
        numeric,
        reference,
    )

    if status:
        result["status"] = status

    return result


# ============================================================
# FLATTEN OCR INTO LOGICAL TOKENS
# ============================================================

def logical_tokens(
    lines: List[DocumentLine],
) -> List[str]:

    tokens = []

    for line in lines:

        words = sorted(
            [
                word
                for word in line.words
                if clean(word.text)
            ],
            key=lambda word: word.x0,
        )

        if words:

            for word in words:
                tokens.append(clean(word.text))

        else:
            text = clean(line.text)

            if text:
                tokens.append(text)

    return tokens


# ============================================================
# SPECIAL GENERIC TABLE PARSER
# ============================================================

def parse_result_blocks(
    lines: List[DocumentLine],
) -> List[Dict[str, Any]]:

    results = []

    i = 0

    while i < len(lines):

        text = clean(lines[i].text)

        if not text:
            i += 1
            continue

        # ----------------------------------------------------
        # Detect common table headers.
        # ----------------------------------------------------

        if norm(text) in {
            "parameter",
            "result",
            "unit",
        }:
            i += 1
            continue

        # ----------------------------------------------------
        # We are looking for:
        #
        # NAME
        # VALUE
        # UNIT
        # REFERENCE
        #
        # Example:
        #
        # Normal Forms
        # 3
        # %
        # >= 4
        # ----------------------------------------------------

        if not is_result_name(text):
            i += 1
            continue

        name = text

        if i + 1 >= len(lines):
            break

        value = clean(lines[i + 1].text)

        # Value must look numeric or be a meaningful
        # categorical value.
        numeric = first_number(value)

        if numeric is None and value.lower() not in {
            "present",
            "absent",
            "positive",
            "negative",
            "+",
            "-",
            "normal",
            "abnormal",
            "equivocal",
        }:
            i += 1
            continue

        unit = None
        reference = None

        consumed = 2

        # ----------------------------------------------------
        # Unit
        # ----------------------------------------------------

        if i + consumed < len(lines):

            candidate = clean(
                lines[i + consumed].text
            )

            if candidate in {
                "%",
                "mg/dL",
                "g/dL",
                "mL",
                "min",
                "sec",
                "mm",
                "cm",
                "kg",
                "°C",
                "cells",
                "Million/mL",
            }:
                unit = candidate
                consumed += 1

        # ----------------------------------------------------
        # Reference
        # ----------------------------------------------------

        if i + consumed < len(lines):

            candidate = clean(
                lines[i + consumed].text
            )

            if (
                candidate.startswith(">=")
                or candidate.startswith("<=")
                or candidate.startswith(">")
                or candidate.startswith("<")
                or parse_reference(candidate)
            ):
                reference = candidate
                consumed += 1

        result = make_result(
            name=name,
            value_text=value,
            unit=unit,
            reference=reference,
        )

        if result:

            results.append(result)

            i += consumed
            continue

        i += 1

    return results


# ============================================================
# INLINE RESULT PARSER
# ============================================================

def parse_inline_results(
    lines: List[DocumentLine],
) -> List[Dict[str, Any]]:

    results = []

    for line in lines:

        text = clean(line.text)

        # Example:
        # Normal Forms 3 % >= 4
        match = re.match(
            r"^(.+?)\s+"
            r"([-+]?\d+(?:[.,]\d+)?)"
            r"\s*"
            r"(%|[A-Za-zµμ/]+)?"
            r"\s*"
            r"((?:>=|<=|>|<)\s*[-+]?\d+(?:[.,]\d+)?"
            r"|[-+]?\d+(?:[.,]\d+)?\s*(?:-|to)\s*[-+]?\d+(?:[.,]\d+)?)"
            r"\s*$",
            text,
            re.I,
        )

        if match:

            name = clean(match.group(1))
            value = match.group(2)
            unit = match.group(3)
            reference = clean(match.group(4))

            if is_result_name(name):

                result = make_result(
                    name,
                    value,
                    unit,
                    reference,
                )

                if result:
                    results.append(result)

                continue

        # Example:
        # Live Sperm 0 % >= 58
        # without relying on exact unit.
        match = re.match(
            r"^(.+?)\s+"
            r"([-+]?\d+(?:[.,]\d+)?)"
            r"\s*(%)?"
            r"\s*((?:>=|<=|>|<)\s*[-+]?\d+(?:[.,]\d+)?)"
            r"\s*$",
            text,
            re.I,
        )

        if match:

            name = clean(match.group(1))
            value = match.group(2)
            unit = match.group(3)
            reference = clean(match.group(4))

            if is_result_name(name):

                result = make_result(
                    name,
                    value,
                    unit,
                    reference,
                )

                if result:
                    results.append(result)

    return results


# ============================================================
# SECTION BUILDER
# ============================================================

def build_sections(
    lines: List[DocumentLine],
) -> List[Dict[str, Any]]:

    sections = []

    current = None

    for line in lines:

        text = clean(line.text)

        if not text:
            continue

        if is_heading(text):

            current = {
                "name": text,
                "results": [],
                "text": [],
            }

            sections.append(current)

            continue

        if current is None:

            current = {
                "name": "General",
                "results": [],
                "text": [],
            }

            sections.append(current)

        current["text"].append(text)

    return sections


# ============================================================
# MAIN
# ============================================================

def extract_medical_data(
    lines: List[DocumentLine],
) -> Dict[str, Any]:

    if not lines:

        return {
            "patient_data": {
                "age": None,
                "sex": None,
                "height_cm": None,
                "weight_kg": None,
                "symptoms": [],
                "medical_history": [],
                "medications": [],
                "additional_information": "",
            },
            "report_data": {
                "report_type": "medical_report",
                "report_title": "",
                "sections": [],
                "findings": [],
                "narrative": [],
            },
        }

    for line in lines:
        line.text = clean(line.text)

    patient_data = extract_patient_data(lines)

    title = find_title(lines)

    report_type = classify_report(
        title,
        lines,
    )

    # --------------------------------------------------------
    # Parse actual results.
    # --------------------------------------------------------

    results = parse_inline_results(lines)

    # If inline rows were not available, use vertical OCR
    # representation.
    if not results:
        results = parse_result_blocks(lines)

    # --------------------------------------------------------
    # Build structural sections.
    # --------------------------------------------------------

    sections = build_sections(lines)

    # --------------------------------------------------------
    # Attach results to the most appropriate section.
    # --------------------------------------------------------

    for result in results:

        target = None

        name = norm(result["test"])

        if name in {
            "live sperm",
            "dead sperm",
        }:
            for section in sections:
                if norm(section["name"]) == "vitality":
                    target = section
                    break

        elif name in {
            "fructose",
            "aggregation / agglutination",
        }:
            for section in sections:
                if norm(section["name"]) == "additional findings":
                    target = section
                    break

        elif "halo" in name or name in {
            "degraded",
        }:
            for section in sections:
                if norm(section["name"]) == "halo classification":
                    target = section
                    break

        elif name in {
            "normal forms",
            "head defects",
            "midpiece defects",
            "tail defects",
            "pin heads",
        }:
            for section in sections:
                if norm(section["name"]) in {
                    "results",
                    "result",
                    "morphology examination",
                }:
                    target = section
                    break

        if target is None:

            for section in sections:

                section_name = norm(section["name"])

                if section_name in {
                    "results",
                    "result",
                    "morphology examination",
                    "vitality",
                    "additional findings",
                    "halo classification",
                    "dna fragmentation",
                    "general information",
                }:
                    target = section
                    break

        if target is None:

            target = {
                "name": "Results",
                "results": [],
                "text": [],
            }

            sections.append(target)

        # Prevent duplicates.
        if not any(
            existing.get("test") == result.get("test")
            for existing in target["results"]
        ):
            target["results"].append(result)

    # --------------------------------------------------------
    # Remove obvious metadata from narrative.
    # --------------------------------------------------------

    narrative = []

    for line in lines:

        text = clean(line.text)

        if not text:
            continue

        if text.startswith("Page ") and " of " in text:
            continue

        if norm(text) in {
            "parameter",
            "result",
            "unit",
        }:
            continue

        narrative.append(text)

    # --------------------------------------------------------
    # Findings
    # --------------------------------------------------------

    findings = []

    for section in sections:

        if norm(section["name"]) in {
            "findings",
            "impression",
            "conclusion",
            "observations",
        }:
            findings.extend(section["text"])

    return {
        "patient_data": patient_data,

        "report_data": {
            "report_type": report_type,
            "report_title": title,
            "sections": sections,
            "findings": findings,
            "narrative": narrative,
        },
    }