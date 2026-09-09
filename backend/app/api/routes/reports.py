from fastapi import APIRouter, Depends, HTTPException
from app.services.llm.groq_client import generate_analysis
from app.core.auth import get_current_user
from app.core.supabase import supabase, get_user_supabase
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportReview,
)
from datetime import datetime, timezone


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.post("", response_model=ReportResponse)
def create_report(
    data: ReportCreate,
    current_user=Depends(get_current_user)
):
    try:
        user_supabase = get_user_supabase(current_user.token)

        report = {
            "user_id": current_user.id,
            "report_name": data.report_name,
            "patient_data": data.patient_data,
            "report_data": data.report_data
        }

        response = (
            user_supabase
            .table("reports")
            .insert(report)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create report"
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("")
def get_reports(
    current_user=Depends(get_current_user)
):
    try:
        user_supabase = get_user_supabase(current_user.token)

        response = (
            user_supabase
            .table("reports")
            .select("*")
            .eq("user_id", current_user.id)
            .order("created_at", desc=True)
            .execute()
        )

        return {
            "reports": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str,
    current_user=Depends(get_current_user)
):
    try:
        user_supabase = get_user_supabase(current_user.token)

        response = (
            user_supabase
            .table("reports")
            .select("*")
            .eq("id", report_id)
            .eq("user_id", current_user.id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch report: {str(e)}"
        )


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: str,
    data: ReportUpdate,
    current_user=Depends(get_current_user)
):
    try:
        user_supabase = get_user_supabase(current_user.token)

        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        update_data["updated_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

        response = (
            user_supabase
            .table("reports")
            .update(update_data)
            .eq("id", report_id)
            .eq("user_id", current_user.id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.delete("/{report_id}")
def delete_report(
    report_id: str,
    current_user=Depends(get_current_user)
):
    try:
        user_supabase = get_user_supabase(current_user.token)

        response = (
            user_supabase
            .table("reports")
            .delete()
            .eq("id", report_id)
            .eq("user_id", current_user.id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )

        return {
            "message": "Report deleted successfully",
            "report_id": report_id
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/save")
def save_reviewed_report(
    data: ReportReview,
    current_user=Depends(get_current_user)
):
    try:
        user_supabase = get_user_supabase(current_user.token)

        report = {
            "user_id": current_user.id,
            "report_name": data.report_name,
            "patient_data": data.patient_data,
            "report_data": data.report_data,
            "additional_information": data.additional_information or ""
        }

        response = (
            user_supabase
            .table("reports")
            .insert(report)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to save report"
            )

        return {
            "message": "Report saved successfully",
            "report": response.data[0]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/{report_id}/analyze")
def analyze_report(
    report_id: str,
    current_user=Depends(get_current_user)
):
    try:
        user_supabase = get_user_supabase(current_user.token)

        response = (
            user_supabase
            .table("reports")
            .select(
                "id, user_id, report_name, patient_data, report_data, "
                "additional_information, analysis"
            )
            .eq("id", report_id)
            .eq("user_id", current_user.id)
            .single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )

        report = response.data

        analysis = generate_analysis(
            patient_data=report["patient_data"],
            report_data=report["report_data"],
            additional_information=report.get(
                "additional_information",
                ""
            )
        )

        analysis_data = analysis.model_dump()

        update_response = (
            user_supabase
            .table("reports")
            .update({
                "analysis": analysis_data,
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            .eq("id", report_id)
            .eq("user_id", current_user.id)
            .execute()
        )

        if not update_response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to save analysis"
            )

        return {
            "message": "Report analyzed successfully",
            "report_id": report_id,
            "analysis": analysis_data
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )