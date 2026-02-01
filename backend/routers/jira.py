from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from models.jira import JiraCredentialsCreate
from services.jira_service import jira_service
from utils.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jira", tags=["Jira Integration"])

@router.post("/connect", response_model=dict)
async def connect_jira(credentials: JiraCredentialsCreate, current_user = Depends(get_current_user)):
    """Connect Jira account for the current user"""
    try:
        # Store Jira credentials
        stored_credentials = await jira_service.store_jira_credentials(current_user.id, credentials)
        if not stored_credentials:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store Jira credentials"
            )
        
        # Validate connection
        is_valid = await jira_service.validate_jira_connection(stored_credentials)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Jira credentials"
            )
        
        # Sync initial data
        sync_success = await jira_service.sync_jira_data(current_user.id)
        if not sync_success:
            logger.warning(f"Initial sync failed for user {current_user.id}")
        
        if sync_success:
            # Trigger risk analysis after successful initial sync
            from services.risk_service import run_risk_analysis
            logger.info(f"Triggering risk analysis after initial Jira sync for user {current_user.id}")
            try:
                risk_result = await run_risk_analysis(current_user.id)
                logger.info(f"Risk analysis completed after initial sync: {risk_result['count']} risks processed")
            except Exception as risk_error:
                logger.error(f"Risk analysis failed after initial sync: {risk_error}")
        
        return {
            "message": "Jira connected successfully",
            "sync_status": "success" if sync_success else "failed",
            "risks_analyzed": sync_success  # Indicate if risk analysis was attempted
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Jira connection failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect Jira"
        )

@router.post("/validate", response_model=dict)
async def validate_jira_connection(current_user = Depends(get_current_user)):
    """Validate Jira connection for the current user"""
    try:
        # Get Jira credentials
        credentials = await jira_service.get_jira_credentials(current_user.id)
        if not credentials or not credentials.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jira credentials not found"
            )
        
        # Validate connection
        is_valid = await jira_service.validate_jira_connection(credentials)
        
        return {
            "is_valid": is_valid,
            "message": "Connection valid" if is_valid else "Connection invalid"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Jira validation failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate Jira connection"
        )

@router.post("/sync", response_model=dict)
async def sync_jira_data(current_user = Depends(get_current_user)):
    """Sync Jira data for the current user - NO AUTH for testing"""
    # test_user_id = "test_user_123"
    
    try:
        success = await jira_service.sync_jira_data(current_user.id)
        
        if success:
            # Trigger risk analysis after successful sync
            from services.risk_service import run_risk_analysis
            logger.info(f"Triggering risk analysis after Jira sync for user {current_user.id}")
            try:
                risk_result = await run_risk_analysis(current_user.id)
                logger.info(f"Risk analysis completed after sync: {risk_result['count']} risks processed")
            except Exception as risk_error:
                logger.error(f"Risk analysis failed after sync: {risk_error}")
            
            return {"message": "Jira data synced successfully", "risks_analyzed": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync Jira data"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Jira sync failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync Jira data"
        )

@router.get("/connection-status", response_model=dict)
async def get_connection_status(current_user = Depends(get_current_user)):
    """Get Jira connection status for the current user"""
    try:
        # Get Jira credentials
        credentials = await jira_service.get_jira_credentials(current_user.id)
        
        if not credentials:
            return {
                "connected": False,
                "message": "Jira not connected"
            }
        
        return {
            "connected": credentials.is_active,
            "domain": credentials.domain,
            "email": credentials.email,
            "created_at": credentials.created_at,
            "updated_at": credentials.updated_at
        }
        
    except Exception as e:
        logger.error(f"Failed to get connection status for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get connection status"
        )

# New endpoints matching the updated API structure
@router.get("/connect/check")
async def check_jira_connection(current_user = Depends(get_current_user)):
    """Quick health-check: returns the account linked to the API token"""
    try:
        credentials = await jira_service.get_jira_credentials(current_user.id)
        if not credentials or not credentials.is_active:
            return {"connected": False, "message": "Jira credentials not found"}
        
        is_valid = await jira_service.validate_jira_connection(credentials)
        if not is_valid:
            return {"connected": False, "message": "Invalid Jira credentials"}
        
        # Return success response
        return {"connected": True, "message": "Jira connection is valid"}
        
    except Exception as e:
        logger.error(f"Jira connection check failed for user {current_user.id}: {e}")
        return {"connected": False, "message": "Failed to check Jira connection"}

@router.get("/issues/all/{project_key}")
async def get_all_issues(project_key: str, current_user = Depends(get_current_user)):
    """Get all issues for a specific project"""
    try:
        credentials = await jira_service.get_jira_credentials(current_user.id)
        if not credentials or not credentials.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jira credentials not found"
            )
        
        # Validate connection before fetching issues
        is_valid = await jira_service.validate_jira_connection(credentials)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Jira connection"
            )
        
        issues = await jira_service.fetch_issues_by_jql(credentials, f"project={project_key}")
        return JSONResponse(content=issues)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch all issues for project {project_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch issues"
        )

@router.get("/issues/epics/{project_key}")
async def get_epics(project_key: str, current_user = Depends(get_current_user)):
    """Get epics for a specific project"""
    try:
        credentials = await jira_service.get_jira_credentials(current_user.id)
        if not credentials or not credentials.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jira credentials not found"
            )
        
        # Validate connection before fetching issues
        is_valid = await jira_service.validate_jira_connection(credentials)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Jira connection"
            )
        
        issues = await jira_service.fetch_epics(credentials, project_key)
        return JSONResponse(content=issues)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch epics for project {project_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch epics"
        )

@router.get("/issues/stories/{project_key}")
async def get_stories(project_key: str, current_user = Depends(get_current_user)):
    """Get stories for a specific project"""
    try:
        credentials = await jira_service.get_jira_credentials(current_user.id)
        if not credentials or not credentials.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jira credentials not found"
            )
        
        # Validate connection before fetching issues
        is_valid = await jira_service.validate_jira_connection(credentials)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Jira connection"
            )
        
        issues = await jira_service.fetch_stories(credentials, project_key)
        return JSONResponse(content=issues)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch stories for project {project_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stories"
        )

@router.get("/issues/tasks/{project_key}")
async def get_tasks(project_key: str, current_user = Depends(get_current_user)):
    """Get tasks for a specific project"""
    try:
        credentials = await jira_service.get_jira_credentials(current_user.id)
        if not credentials or not credentials.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jira credentials not found"
            )
        
        # Validate connection before fetching issues
        is_valid = await jira_service.validate_jira_connection(credentials)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Jira connection"
            )
        
        issues = await jira_service.fetch_tasks(credentials, project_key)
        return JSONResponse(content=issues)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch tasks for project {project_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tasks"
        )

@router.get("/issues/bugs/{project_key}")
async def get_bugs(project_key: str, current_user = Depends(get_current_user)):
    """Get bugs for a specific project"""
    try:
        credentials = await jira_service.get_jira_credentials(current_user.id)
        if not credentials or not credentials.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jira credentials not found"
            )
        
        # Validate connection before fetching issues
        is_valid = await jira_service.validate_jira_connection(credentials)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Jira connection"
            )
        
        issues = await jira_service.fetch_bugs(credentials, project_key)
        return JSONResponse(content=issues)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch bugs for project {project_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bugs"
        )

@router.get("/users")
async def get_jira_users(project_key: str = None, current_user = Depends(get_current_user)):
    """Get all users from Jira instance or users in a specific project"""
    try:
        credentials = await jira_service.get_jira_credentials(current_user.id)
        if not credentials or not credentials.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jira credentials not found"
            )
        
        # Validate connection before fetching users
        is_valid = await jira_service.validate_jira_connection(credentials)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Jira connection"
            )
        
        users = await jira_service.fetch_jira_users(credentials, project_key)
        return JSONResponse(content=users)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch Jira users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )

@router.get("/users/assignable")
async def get_assignable_users(project_key: str = None, current_user = Depends(get_current_user)):
    """Get users that can be assigned to issues (assignable users)"""
    try:
        credentials = await jira_service.get_jira_credentials(current_user.id)
        if not credentials or not credentials.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jira credentials not found"
            )
        
        # Validate connection before fetching users
        is_valid = await jira_service.validate_jira_connection(credentials)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Jira connection"
            )
        
        users = await jira_service.fetch_assignable_users(credentials, project_key)
        return JSONResponse(content=users)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch assignable Jira users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assignable users"
        )

@router.get("/users/from-tasks")
async def get_unique_assignees_from_tasks(current_user = Depends(get_current_user)):
    """Get unique assignees from stored Jira tasks (database-based approach)"""
    try:
        assignees = await jira_service.get_unique_assignees_from_tasks(current_user.id)
        return JSONResponse(content=assignees)
        
    except Exception as e:
        logger.error(f"Failed to get unique assignees from tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assignees from tasks"
        )