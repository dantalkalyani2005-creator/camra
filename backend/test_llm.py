from app.services.llm.groq_client import generate_analysis


patient_data = {
    "age": 45,
    "sex": "female",
    "height_cm": 165.0,
    "weight_kg": 68.0,
    "symptoms": [
        "fatigue",
        "dizziness"
    ],
    "medical_history": [
        "diabetes",
        "hypertension"
    ],
    "medications": [
        "metformin 500 mg",
        "amlodipine 5 mg"
    ],
    "additional_information": (
        "Patient reports feeling tired for the past few days."
    )
}


report_data = {
    "report_type": "blood_test",
    "test_name": "Complete Blood Count",
    "results": {
        "hemoglobin": {
            "value": 10.2,
            "unit": "g/dL",
            "reference_range": "12.0 - 15.5",
            "status": "low"
        },
        "wbc": {
            "value": 7200,
            "unit": "/µL",
            "reference_range": "4000 - 11000",
            "status": "normal"
        }
    }
}


print("Sending structured data to Llama...\n")

response = generate_analysis(
    patient_data,
    report_data
)

print("========== RAW LLAMA RESPONSE ==========")
print(response)