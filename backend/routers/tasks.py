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