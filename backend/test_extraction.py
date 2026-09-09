from app.services.extraction.medical import extract_medical_data


sample_text = """
Patient Name: [NAME]
Age: 45
Sex: Female
Height: 165 cm
Weight: 68 kg

Symptoms: fatigue, dizziness
Medical History: diabetes, hypertension
Medications: metformin 500 mg, amlodipine 5 mg

Test Name: Complete Blood Count

Hemoglobin: 10.2 g/dL 12.0 - 15.5
WBC: 7200 /µL 4000 - 11000
RBC: 4.5 million/µL 3.8 - 5.2
Platelets: 250000 /µL 150000 - 450000
"""


result = extract_medical_data(sample_text)


print("========== PATIENT DATA ==========")
print(result["patient_data"])


print("\n========== REPORT DATA ==========")
print(result["report_data"])