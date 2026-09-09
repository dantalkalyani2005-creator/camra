from app.schemas.report import AnalysisResult


sample_analysis = {
    "summary": "The CBC shows a low hemoglobin level.",
    "key_findings": [
        "Hemoglobin is below the provided reference range."
    ],
    "abnormal_results": [
        {
            "test": "hemoglobin",
            "value": 10.2,
            "unit": "g/dL",
            "reference_range": "12.0 - 15.5",
            "status": "low"
        }
    ],
    "possible_explanations": [
        "Low hemoglobin can have several possible causes."
    ],
    "questions_to_discuss_with_doctor": [
        "What could be contributing to the low hemoglobin level?"
    ],
    "general_guidance": [
        "Discuss the result with a qualified healthcare professional."
    ],
    "disclaimer": (
        "This analysis is for educational purposes and "
        "does not provide a diagnosis or medical prescription."
    )
}


analysis = AnalysisResult(**sample_analysis)

print("========== VALIDATED ANALYSIS ==========")
print(analysis.model_dump())