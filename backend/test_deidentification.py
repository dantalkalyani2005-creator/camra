from app.services.deidentification.sanitizer import sanitize_text


sample_text = """
PATIENT INFORMATION

Patient Name: Rahul Sharma
Age: 45
Sex: Male

Address
Nashik, Maharashtra - 422001

Phone
9876543210

Email
rahul.sharma@example.com

Date of Birth: 15/08/1981

Medical Record Number: MRN-2026-00125

Invoice #: VRV-0001-2026-27

GSTIN
27ABCDE1234F1Z5

Website: https://example.com/patient/12345

Server IP: 192.168.1.100

Hemoglobin: 14.2 g/dL
WBC: 7200 /µL
"""


sanitized_text, detected = sanitize_text(sample_text)


print("========== ORIGINAL TEXT ==========")
print(sample_text)

print("\n========== SANITIZED TEXT ==========")
print(sanitized_text)

print("\n========== DETECTED IDENTIFIERS ==========")
print(detected)