from fastapi import APIRouter, Depends
from services.risk_service import run_risk_analysis
from db import get_database
from utils.dependencies import get_current_user
from datetime import datetime
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
    risk_result = await run_risk_analysis(user_id)
    logger.info(f"✅ Risk analysis completed: {risk_result['count']} risks created")

    return {
        "message": "Risk analysis completed",
        "new_risks_created": risk_result['count'],
        "data": risk_result
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
        if "due_date" in doc and doc["due_date"]:
            if isinstance(doc["due_date"], datetime):
                doc["due_date"] = doc["due_date"].date().isoformat()
            elif hasattr(doc["due_date"], 'date'):
                doc["due_date"] = doc["due_date"].date().isoformat()
            else:
                doc["due_date"] = str(doc["due_date"])
        if "start_date" in doc and doc["start_date"]:
            if isinstance(doc["start_date"], datetime):
                doc["start_date"] = doc["start_date"].date().isoformat()
            elif hasattr(doc["start_date"], 'date'):
                doc["start_date"] = doc["start_date"].date().isoformat()
            else:
                doc["start_date"] = str(doc["start_date"])
        if "leave_start" in doc and doc["leave_start"]:
            if isinstance(doc["leave_start"], datetime):
                doc["leave_start"] = doc["leave_start"].date().isoformat()
            elif hasattr(doc["leave_start"], 'date'):
                doc["leave_start"] = doc["leave_start"].date().isoformat()
            else:
                doc["leave_start"] = str(doc["leave_start"])
        if "leave_end" in doc and doc["leave_end"]:
            if isinstance(doc["leave_end"], datetime):
                doc["leave_end"] = doc["leave_end"].date().isoformat()
            elif hasattr(doc["leave_end"], 'date'):
                doc["leave_end"] = doc["leave_end"].date().isoformat()
            else:
                doc["leave_end"] = str(doc["leave_end"])
        risks.append(doc)
    
    logger.info(f"✅ Found {len(risks)} risk alerts")
    return risks
