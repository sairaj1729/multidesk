from fastapi import APIRouter
from services.risk_service import run_risk_analysis
from db import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/risks",
    tags=["Risks"]
)

@router.get("/check")
async def check_risks():
    """Trigger risk analysis - NO AUTH for testing"""
    logger.info("🔍 Starting risk analysis...")
    risks = await run_risk_analysis()
    logger.info(f"✅ Risk analysis completed: {len(risks)} risks found")

    return {
        "message": "Risk analysis completed",
        "new_risks_created": len(risks),
        "data": risks
    }


@router.get("")
async def get_all_risks():
    """Get all risk alerts - NO AUTH for testing"""
    logger.info("📋 Fetching all risk alerts...")
    db = get_database()
    risks = []

    async for doc in db.risk_alerts.find().sort("created_at", -1):
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
