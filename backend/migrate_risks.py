import asyncio
from db import get_database, connect_to_mongo, close_mongo_connection
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_existing_risks():
    """Migrate existing risk documents to add user_id field"""
    try:
        # Initialize database connection
        await connect_to_mongo()
        db = get_database()
        
        logger.info("Starting migration of existing risk documents...")
        
        # Count existing risks without user_id
        risks_without_user = await db.risk_alerts.count_documents({"user_id": {"$exists": False}})
        logger.info(f"Found {risks_without_user} risk documents without user_id field")
        
        if risks_without_user == 0:
            logger.info("No migration needed - all risk documents already have user_id")
            return
            
        # For existing risks, we'll need to determine the user_id based on the task data
        # Since we don't have the original user context, we'll use a default value
        # In a production environment, you might want to implement more sophisticated logic
        default_user_id = "unknown_user_migrated"
        
        # Update all existing risk documents to add user_id field
        result = await db.risk_alerts.update_many(
            {"user_id": {"$exists": False}},
            {"$set": {"user_id": default_user_id}}
        )
        
        logger.info(f"Updated {result.modified_count} risk documents with user_id: {default_user_id}")
        
        # Verify the migration
        total_risks = await db.risk_alerts.count_documents({})
        risks_with_user = await db.risk_alerts.count_documents({"user_id": {"$ne": None}})
        
        logger.info(f"Migration verification:")
        logger.info(f"  - Total risks: {total_risks}")
        logger.info(f"  - Risks with user_id: {risks_with_user}")
        logger.info(f"  - Risks without user_id: {total_risks - risks_with_user}")
        
        if risks_with_user == total_risks:
            logger.info("✅ Migration completed successfully!")
        else:
            logger.warning("⚠️ Migration completed but some documents still missing user_id")
            
    except Exception as e:
        logger.error(f"Migration failed with error: {e}")
        raise
    finally:
        # Clean up database connection
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(migrate_existing_risks())