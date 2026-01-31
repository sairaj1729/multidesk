from fastapi import APIRouter, Depends
from models.dashboard import DashboardResponse
from services.dashboard_service import dashboard_service
from utils.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/test")
async def test_endpoint(current_user = Depends(get_current_user)):
    """Test endpoint to verify authentication works"""
    logger.info(f"🧪 TEST endpoint called by: {current_user.email}")
    return {
        "message": "Test successful",
        "user": current_user.email,
        "user_id": current_user.id,
        "verified": current_user.is_verified
    }

@router.get("/stats", response_model=dict)
async def get_dashboard_stats(current_user = Depends(get_current_user)):
    """Get dashboard statistics for the current user"""
    try:
        logger.info(f"📊 Getting dashboard stats for user: {current_user.id}")
        stats = await dashboard_service.get_dashboard_stats(current_user.id)
        # Convert Pydantic model to dictionary
        result = stats.dict()
        logger.info(f"✅ Dashboard stats retrieved successfully for {current_user.id}")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to get dashboard stats for user {current_user.id}: {e}", exc_info=True)
        raise

@router.get("/eisenhower", response_model=dict)
async def get_eisenhower_matrix(current_user = Depends(get_current_user)):
    """Get Eisenhower Matrix data for the current user"""
    try:
        eisenhower = await dashboard_service.get_eisenhower_matrix(current_user.id)
        # Convert Pydantic model to dictionary
        return eisenhower.dict()
    except Exception as e:
        logger.error(f"Failed to get Eisenhower Matrix for user {current_user.id}: {e}")
        raise

@router.get("/analytics", response_model=dict)
async def get_analytics_data(current_user = Depends(get_current_user)):
    """Get analytics data for the current user"""
    try:
        analytics = await dashboard_service.get_analytics_data(current_user.id)
        # Convert Pydantic model to dictionary
        return {
            "tasks_by_status": [item.dict() for item in analytics.tasks_by_status],
            "task_velocity": [item.dict() for item in analytics.task_velocity],
            "issue_type_distribution": [item.dict() for item in analytics.issue_type_distribution]
        }
    except Exception as e:
        logger.error(f"Failed to get analytics data for user {current_user.id}: {e}")
        raise

@router.get("/", response_model=DashboardResponse)
async def get_dashboard_data(current_user = Depends(get_current_user)):
    """Get all dashboard data for the current user"""
    try:
        stats = await dashboard_service.get_dashboard_stats(current_user.id)
        eisenhower = await dashboard_service.get_eisenhower_matrix(current_user.id)
        analytics = await dashboard_service.get_analytics_data(current_user.id)
        
        return DashboardResponse(
            stats=stats.dict(),
            eisenhower=eisenhower.dict(),
            analytics=analytics.dict()
        )
    except Exception as e:
        logger.error(f"Failed to get dashboard data for user {current_user.id}: {e}")
        raise

@router.get("/eisenhower/view-all")
async def view_all_eisenhower(
        quadrant: str,
        current_user=Depends(get_current_user)
    ):
        return await dashboard_service.get_eisenhower_tasks_by_quadrant(
            current_user.id,
            quadrant
        )

@router.get("/debug-velocity")
async def debug_task_velocity(current_user = Depends(get_current_user)):
    """Debug endpoint to check task velocity calculation"""
    try:
        logger.info(f"Debugging task velocity for user: {current_user.id}")
        velocity_data = await dashboard_service._calculate_real_task_velocity(current_user.id)
        return {"velocity_data": [item.dict() for item in velocity_data]}
    except Exception as e:
        logger.error(f"Debug failed: {e}", exc_info=True)
        raise
