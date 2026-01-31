from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models.tasks import TaskResponse, TaskFilter, TaskCreate, TaskUpdate
from services.tasks_service import tasks_service
from utils.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("/", response_model=TaskResponse)
async def get_tasks(
    search: Optional[str] = Query(None, description="Search in task summary or key"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    project: Optional[str] = Query(None, description="Filter by project key"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user = Depends(get_current_user)
):
    """Get tasks for the current user with filtering and pagination"""
    try:
        filter_params = TaskFilter(
            search=search,
            status=status,
            priority=priority,
            project=project,
            assignee=assignee
        )
        
        result = await tasks_service.get_tasks(current_user.id, filter_params, page, size)
        return TaskResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to get tasks for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tasks"
        )

@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: str, current_user = Depends(get_current_user)):
    """Get a specific task by ID"""
    try:
        task = await tasks_service.get_task_by_id(current_user.id, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task {task_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task"
        )

@router.get("/debug/all", response_model=dict)
async def debug_all_tasks(current_user = Depends(get_current_user)):
    """Debug endpoint to see all tasks and assignees"""
    try:
        from db import get_database
        db = get_database()
        tasks_collection = db.jira_tasks
        
        # Get all tasks for this user
        tasks = await tasks_collection.find({"user_id": current_user.id}).to_list(length=100)
        
        # Extract unique assignees
        assignees = {}
        for task in tasks:
            account_id = task.get("assignee_account_id")
            if account_id:
                if account_id not in assignees:
                    assignees[account_id] = {
                        "account_id": account_id,
                        "name": task.get("assignee", "Unknown"),
                        "email": task.get("assignee_email", "Unknown"),
                        "task_count": 0
                    }
                assignees[account_id]["task_count"] += 1
        
        return {
            "total_tasks": len(tasks),
            "assignees": list(assignees.values()),
            "sample_tasks": tasks[:5]  # First 5 tasks for inspection
        }
    except Exception as e:
        logger.error(f"Debug endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Debug failed"
        )