from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    report_name: str = Field(..., min_length=1, max_length=200)
    patient_data: Dict[str, Any] = {}
    report_data: Dict[str, Any] = {}
    additional_information: Optional[str] = ""


class ReportUpdate(BaseModel):
    report_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200
    )
    patient_data: Optional[Dict[str, Any]] = None
    report_data: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    additional_information: Optional[str] = None


class ReportResponse(BaseModel):
    id: str
    user_id: str
    report_name: str
    patient_data: Dict[str, Any]
    report_data: Dict[str, Any]
    analysis: Optional[Dict[str, Any]] = None
    additional_information: Optional[str] = ""
    created_at: str
    updated_at: str
    
class ReportReview(BaseModel):

    report_name: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    patient_data: Dict[str, Any]

    report_data: Dict[str, Any]

    additional_information: Optional[str] = ""
    
class AbnormalResult(BaseModel):
    test: str
    value: float
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: str


class PossibleExplanation(BaseModel):
    finding: str
    explanation: str
    basis: str


class AnalysisResult(BaseModel):
    summary: str
    key_findings: list[str]
    abnormal_results: list[AbnormalResult]
    possible_explanations: list[PossibleExplanation]
    questions_to_discuss_with_doctor: list[str]
    general_guidance: list[str]
    disclaimer: str