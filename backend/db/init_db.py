import logging
from .mongodb import get_database

logger = logging.getLogger(__name__)

async def init_database():
    """Initialize database with required collections and indexes"""
    try:
        db = get_database()
        
        # Create indexes for reports collection
        reports_collection = db.reports
        await reports_collection.create_index([("created_by", 1)])
        await reports_collection.create_index([("type", 1)])
        await reports_collection.create_index([("created_at", -1)])
        await reports_collection.create_index([("is_public", 1)])
        logger.info("Reports collection indexes created")
        
        # Create indexes for report_data collection
        report_data_collection = db.report_data
        await report_data_collection.create_index([("report_id", 1)])
        await report_data_collection.create_index([("label", 1)])
        logger.info("Report data collection indexes created")
        
        # Create indexes for report_summaries collection
        report_summaries_collection = db.report_summaries
        await report_summaries_collection.create_index([("report_id", 1)])
        logger.info("Report summaries collection indexes created")
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise