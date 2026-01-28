from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models.reports import (
    ReportListResponse,
    ReportResponse,
    ReportGenerationRequest,
    ReportExportRequest
)
from services.reports_service import reports_service
from services.jira_service import jira_service
from services.users_service import users_service
from utils.dependencies import get_current_user
from models.users import UserFilter
from models.projects import ProjectListResponse, ProjectFilter
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/reports", tags=["Reports"])

# Define specific routes BEFORE the generic report_id route

@router.get("/", response_model=ReportListResponse)
async def get_reports(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    current_user = Depends(get_current_user)
):
    """Get available reports for the current user"""
    try:
        result = await reports_service.get_available_reports(current_user.id, page, size)
        return result
    except Exception as e:
        logger.error(f"Failed to get reports for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reports"
        )

@router.get("/projects", response_model=dict)
async def get_reportable_projects(current_user = Depends(get_current_user)):
    """Get list of projects available for reporting"""
    try:
        # Fetch projects from database
        projects = await jira_service.get_user_projects(current_user.id)
        
        # Extract project keys and names
        project_list = [{"key": p.key, "name": p.name} for p in projects]
        
        return {"projects": project_list}
        
    except Exception as e:
        logger.error(f"Failed to get reportable projects for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get projects"
        )

@router.get("/users", response_model=dict)
async def get_reportable_users(current_user = Depends(get_current_user)):
    """Get list of users available for reporting"""
    try:
        # Get all users for the current account
        filter_params = UserFilter()
        result = await users_service.get_users(filter_params, 1, 1000)  # Get all users
        
        # Format users for dropdown
        user_list = [
            {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email
            }
            for user in result["users"]
        ]
        
        return {"users": user_list}
        
    except Exception as e:
        logger.error(f"Failed to get reportable users for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: ReportGenerationRequest, current_user = Depends(get_current_user)):
    """Generate a new report"""
    try:
        report = await reports_service.generate_report(current_user.id, request)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate report"
            )
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )

# Generic routes should be defined AFTER specific routes

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, current_user = Depends(get_current_user)):
    """Get a specific report by ID"""
    try:
        report = await reports_service.get_report_by_id(current_user.id, report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report {report_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get report"
        )

@router.delete("/{report_id}", response_model=dict)
async def delete_report(report_id: str, current_user = Depends(get_current_user)):
    """Delete a report"""
    try:
        success = await reports_service.delete_report(current_user.id, report_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found or deletion failed"
            )
        return {"message": "Report deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete report {report_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )

@router.post("/{report_id}/export", response_model=dict)
async def export_report(report_id: str, request: ReportExportRequest, current_user = Depends(get_current_user)):
    """Export a report in the specified format"""
    try:
        # For now, we'll return a placeholder response
        # In a real implementation, this would generate and return the actual file
        return {
            "message": f"Report {report_id} exported successfully",
            "format": request.format,
            "download_url": f"/api/reports/{report_id}/download/{request.format}"
        }
    except Exception as e:
        logger.error(f"Failed to export report {report_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export report"
        )