from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models.projects import ProjectListResponse, ProjectFilter, JiraProjectResponse
from services.jira_service import jira_service
from utils.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    search: Optional[str] = Query(None, description="Search in project name or key"),
    lead: Optional[str] = Query(None, description="Filter by project lead"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user = Depends(get_current_user)
):
    """Get projects for the current user with filtering and pagination"""
    try:
        # Fetch projects from database
        projects = await jira_service.get_user_projects(current_user.id)
        
        # Apply search filter if provided
        if search:
            projects = [p for p in projects if 
                       search.lower() in p.name.lower() or 
                       search.lower() in p.key.lower()]
        
        # Apply lead filter if provided
        if lead:
            projects = [p for p in projects if lead.lower() in p.lead.lower()]
        
        # Calculate pagination
        total = len(projects)
        start = (page - 1) * size
        end = start + size
        paginated_projects = projects[start:end]
        
        return ProjectListResponse(
            projects=paginated_projects,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"Failed to get projects for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get projects"
        )

@router.get("/keys", response_model=dict)
async def get_project_keys(current_user = Depends(get_current_user)):
    """Get list of project keys for the current user"""
    try:
        # Fetch projects from database
        projects = await jira_service.get_user_projects(current_user.id)
        
        # Extract project keys
        project_keys = [{"key": p.key, "name": p.name} for p in projects]
        
        return {"project_keys": project_keys}
        
    except Exception as e:
        logger.error(f"Failed to get project keys for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project keys"
        )