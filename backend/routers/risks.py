from fastapi import APIRouter, Depends
from services.risk_service import run_risk_analysis
from db import get_database
from utils.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/risks",
    tags=["Risks"]
)

@router.get("/check")
async def check_risks(current_user: dict = Depends(get_current_user)):
    """Trigger risk analysis for current user"""
    user_id = getattr(current_user, "id", "unknown_user")
    logger.info(f"🔍 Starting risk analysis for user {user_id}...")
    risks = await run_risk_analysis(user_id)
    logger.info(f"✅ Risk analysis completed: {len(risks)} risks found")

    return {
        "message": "Risk analysis completed",
        "new_risks_created": len(risks),
        "data": risks
    }


@router.get("")
async def get_all_risks(current_user: dict = Depends(get_current_user)):
    """Get risk alerts for current user"""
    user_id = getattr(current_user, "id", "unknown_user")
    logger.info(f"📋 Fetching risk alerts for user {user_id}...")
    db = get_database()
    risks = []

    async for doc in db.risk_alerts.find({"user_id": user_id}).sort("created_at", -1):
        doc["_id"] = str(doc["_id"])
        # Convert date objects to strings for JSON serialization
        if "due_date" in doc:
            doc["due_date"] = str(doc["due_date"])
        if "leave_start" in doc:
            doc["leave_start"] = str(doc["leave_start"])
        if "leave_end" in doc:
            doc["leave_end"] = str(doc["leave_end"])
        risks.append(doc)
    
    logger.info(f"✅ Found {len(risks)} risk alerts")
    return risks
