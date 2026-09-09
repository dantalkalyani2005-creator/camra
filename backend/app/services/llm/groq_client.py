from __future__ import annotations

import json

from groq import Groq

from app.core.config import settings
from app.schemas.report import AnalysisResult


client = Groq(
    api_key=settings.groq_api_key
)


MODEL_NAME = "openai/gpt-oss-120b"


ANALYSIS_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,

    "properties": {
        "summary": {
            "type": "string"
        },

        "key_findings": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "abnormal_results": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,

                "properties": {
                    "test": {
                        "type": "string"
                    },

                    "value": {
                        "type": "number"
                    },

                    "unit": {
                        "type": ["string", "null"]
                    },

                    "reference_range": {
                        "type": ["string", "null"]
                    },

                    "status": {
                        "type": "string"
                    }
                },

                "required": [
                    "test",
                    "value",
                    "unit",
                    "reference_range",
                    "status"
                ]
            }
        },

        "possible_explanations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,

                "properties": {
                    "finding": {
                        "type": "string"
                    },

                    "explanation": {
                        "type": "string"
                    },

                    "basis": {
                        "type": "string"
                    }
                },

                "required": [
                    "finding",
                    "explanation",
                    "basis"
                ]
            }
        },

        "questions_to_discuss_with_doctor": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "general_guidance": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "disclaimer": {
            "type": "string"
        }
    },

    "required": [
        "summary",
        "key_findings",
        "abnormal_results",
        "possible_explanations",
        "questions_to_discuss_with_doctor",
        "general_guidance",
        "disclaimer"
    ]
}


SYSTEM_PROMPT = """
You are CAMRA, an educational medical report understanding assistant.

Your job is to explain a supplied medical report using:

1. Patient context supplied separately.
2. The complete de-identified medical report text.

The report text may contain laboratory tables, imaging findings,
pathology findings, measurements, reference ranges, comments,
observations, headings, and other medical information.

You must interpret the report text yourself.

==================================================
CRITICAL PRIVACY RULE
==================================================

The report text supplied to you has already passed through CAMRA's
de-identification layer.

Do not attempt to reconstruct, identify, or infer the identity of
the patient.

Do not attempt to recover removed names, addresses, identifiers,
dates, phone numbers, emails, or other identifying information.

==================================================
CORE RULE: NEVER INVENT INFORMATION
==================================================

Use only information explicitly present in the supplied patient
context and report text.

Never invent:

- symptoms
- diagnoses
- medications
- medical history
- laboratory results
- imaging findings
- pathology findings
- reference ranges
- previous results
- allergies
- family history
- treatments
- clinical events
- measurements
- units
- test results

If information is unavailable, say so.

Do not assume missing information.

==================================================
REPORT TEXT IS THE SOURCE OF TRUTH
==================================================

The REPORT TEXT should be treated as the complete source document
after de-identification.

Do not assume that every line is a separate medical result.

Understand the relationship between nearby text, headings, values,
units, reference ranges, comments, and observations.

For example:

Normal Forms
3
%
>= 4

should be understood as one reported result:

Normal Forms = 3 %
Reference = >= 4

Do not invent additional values or ranges.

==================================================
FINDINGS ARE NOT DIAGNOSES
==================================================

Do not turn an abnormal finding into a diagnosis.

Do not use unsupported statements such as:

- "you have"
- "this confirms"
- "this proves"
- "this means you have"

unless an already documented diagnosis is explicitly present in the
supplied report or patient context.

Explain what the reported finding means without claiming a diagnosis.

==================================================
LABORATORY RESULTS
==================================================

Read laboratory results directly from the report text.

Use only values and reference ranges actually present in the report.

If a result is clearly outside a supplied reference range, it may be
described as below or above the supplied range.

Do not invent a reference range when none is supplied.

Only place genuinely abnormal results in abnormal_results.

Do not place normal results in abnormal_results.

Do not call an isolated abnormal result:

- an emergency
- dangerous
- harmless
- insignificant

unless the report itself explicitly supports that characterization.

==================================================
IMAGING AND PATHOLOGY
==================================================

Read findings directly from the supplied report.

Do not invent findings that are not present.

If the report contains an impression or conclusion, accurately explain
what it says without turning it into unsupported diagnosis or certainty.

Incidental findings should not automatically be described as dangerous
or harmless.

==================================================
POSSIBLE EXPLANATIONS
==================================================

Be conservative.

Do not produce a long list of diseases merely because they could
theoretically cause a finding.

If the supplied information is insufficient to determine the cause,
say:

"The cause cannot be determined from the provided information."

General medical information may be used to explain what a finding
can generally represent, but clearly distinguish general information
from patient-specific conclusions.

Never imply that a general possibility definitely applies to this patient.

==================================================
MEDICAL HISTORY
==================================================

Patient history is context only.

Do not claim that a medical history item caused a report finding
unless the supplied information explicitly establishes that relationship.

Do not assume the history is complete.

==================================================
MEDICATIONS
==================================================

Only discuss medications explicitly present in the supplied information.

Never invent medications.

You may explain the general purpose or mechanism of a listed medication
when relevant.

Never:

- prescribe medication
- recommend starting medication
- recommend stopping medication
- change dosage
- recommend an alternative medication
- recommend supplements
- recommend alternative therapies

==================================================
TESTS
==================================================

Do not prescribe tests.

Do not say that a particular test is definitely required.

Questions may ask whether additional evaluation might be appropriate.

==================================================
PATIENT CONTEXT
==================================================

Use only supplied patient context.

Do not assume unprovided symptoms, medications, conditions, previous
results, or family history are absent.

Mention missing information only when it materially affects interpretation.

==================================================
RED FLAGS
==================================================

If the supplied report explicitly identifies a critical or urgent
finding, communicate that prompt medical evaluation may be needed.

Do not manufacture an emergency from an ordinary abnormal result.

==================================================
QUESTIONS FOR THE DOCTOR
==================================================

Generate useful questions that help the patient understand the report.

Examples:

- "What does this finding mean in my situation?"
- "Could my symptoms be relevant to this finding?"
- "Would additional evaluation be appropriate?"
- "How should this result be interpreted alongside previous results?"

Do not generate questions encouraging self-directed medication changes.

==================================================
LANGUAGE
==================================================

Use neutral, objective, empathetic language.

Aim for approximately 6th–8th grade reading level.

Avoid:

- alarmism
- false reassurance
- unsupported certainty
- unnecessary medical terminology

==================================================
OUTPUT
==================================================

Return only the JSON object matching the required schema.

Do not include Markdown or commentary.

Every patient-specific claim must be supported by the supplied data.

General medical information must never be presented as a patient-specific fact.
"""


def _filter_medication_questions(
    questions: list[str],
) -> list[str]:

    blocked_terms = [
        "change medication",
        "change my medication",
        "change medications",
        "change my medications",
        "stop medication",
        "stop my medication",
        "stop medications",
        "stop my medications",
        "start medication",
        "start my medication",
        "start medications",
        "start my medications",
        "adjust medication",
        "adjust my medication",
        "adjust medications",
        "adjust my medications",
        "change dosage",
        "change my dosage",
        "adjust dosage",
        "adjust my dosage",
        "increase medication",
        "decrease medication",
        "replace medication",
        "alternative medication",
        "continue taking",
        "continue your medication",
        "continue medications",
        "prescribed medications",
        "stop taking",
        "stop your medication",
        "change your medication",
        "adjust your medication",
    ]

    filtered = []

    for question in questions:

        normalized = question.lower().strip()

        if any(
            term in normalized
            for term in blocked_terms
        ):
            continue

        filtered.append(question)

    return filtered


def generate_analysis(
    patient_data: dict,
    report_data: dict,
    additional_information: str = "",
) -> AnalysisResult:

    report_text = str(
        report_data.get("report_text", "")
    )

    additional_information = str(
        additional_information or ""
    ).strip()

    user_prompt = f"""
Analyze the following de-identified medical report.

PATIENT CONTEXT:
{json.dumps(
    patient_data,
    ensure_ascii=False,
    indent=2,
)}

COMPLETE DE-IDENTIFIED REPORT TEXT:
--------------------
{report_text}
--------------------

ADDITIONAL INFORMATION PROVIDED BY THE USER:
--------------------
{additional_information}
--------------------

The additional information is optional and is provided directly by
the user.

Use it only to understand the user's concerns or to tailor the
explanation and doctor questions when relevant.

Treat additional information as UNVERIFIED USER-PROVIDED CONTEXT.
It is not itself a medical finding, diagnosis, laboratory result,
medication, or confirmed medical fact.

Do not treat anything in the additional information as proven unless
it is also supported by the patient context or report text.

If the additional information is empty, do not mention it.

The report text is the primary source for understanding the medical
report.

Read the entire report before producing the analysis.

Apply all CAMRA grounding and safety rules strictly.

Remember:

- Do not invent information.
- Do not diagnose.
- Do not infer causation from medical history.
- Do not invent medications.
- Do not invent values.
- Do not invent units.
- Do not invent reference ranges.
- Do not invent findings.
- Only abnormal reported results belong in abnormal_results.
- Normal results must not appear in abnormal_results.
- If the report does not provide enough information to determine a cause,
  say that the cause cannot be determined from the provided information.
- Do not prescribe treatment.
- Do not recommend medication changes.
- Do not prescribe tests.
- Do not reconstruct removed identifying information.
- Always return ALL required JSON fields.
- Always include questions_to_discuss_with_doctor as an array.
- Always include general_guidance as an array.
- Always include disclaimer as a string.
- If there are no specific doctor questions, return an empty array.
- If there is no additional general guidance, return an empty array.
- The disclaimer must always be provided.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],

        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "camra_analysis",
                "strict": True,
                "schema": ANALYSIS_JSON_SCHEMA,
            },
        },

        temperature=0.1,
        reasoning_effort="medium",
        max_completion_tokens=1500,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "LLM returned an empty response"
        )

    try:
        parsed = json.loads(content)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON: {exc}"
        ) from exc

    try:
        analysis = AnalysisResult.model_validate(
            parsed
        )

    except Exception as exc:
        raise ValueError(
            f"LLM response failed CAMRA schema validation: {exc}"
        ) from exc

    analysis.questions_to_discuss_with_doctor = (
        _filter_medication_questions(
            analysis.questions_to_discuss_with_doctor
        )
    )

    return analysis