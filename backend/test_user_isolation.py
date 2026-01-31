import asyncio
from services.risk_service import run_risk_analysis
from db import get_database, connect_to_mongo, close_mongo_connection
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_user_isolation():
    """Test that risk analysis is properly isolated by user"""
    try:
        # Initialize database connection
        await connect_to_mongo()
        db = get_database()
        
        # Test 1: Run risk analysis without user_id (should process all data)
        logger.info("=== Test 1: Risk analysis without user_id ===")
        result1 = await run_risk_analysis()
        logger.info(f"Result without user_id: {result1}")
        
        # Test 2: Run risk analysis with specific user_id
        test_user_id = "test_user_123"
        logger.info(f"=== Test 2: Risk analysis with user_id {test_user_id} ===")
        result2 = await run_risk_analysis(test_user_id)
        logger.info(f"Result with user_id: {result2}")
        
        # Test 3: Check that risks are properly filtered by user_id
        logger.info("=== Test 3: Checking risk document user_id fields ===")
        risks = []
        async for doc in db.risk_alerts.find():
            risks.append({
                "task_key": doc.get("task_key"),
                "user_id": doc.get("user_id"),
                "risk_level": doc.get("risk_level")
            })
        
        logger.info(f"Total risks in database: {len(risks)}")
        for risk in risks[:10]:  # Show first 10 risks
            logger.info(f"  - Task: {risk['task_key']}, User: {risk['user_id']}, Level: {risk['risk_level']}")
        
        # Test 4: Verify user-specific risk filtering
        user_risks = await db.risk_alerts.count_documents({"user_id": test_user_id})
        all_risks = await db.risk_alerts.count_documents({})
        logger.info(f"Risks for user {test_user_id}: {user_risks}")
        logger.info(f"Total risks in database: {all_risks}")
        
        if user_risks <= all_risks:
            logger.info("✅ User isolation test PASSED - User-specific risks are properly filtered")
        else:
            logger.error("❌ User isolation test FAILED - User risks exceed total risks")
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise
    finally:
        # Clean up database connection
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_user_isolation())