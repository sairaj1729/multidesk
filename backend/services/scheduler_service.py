import asyncio
import logging
from datetime import datetime, timedelta
from db import get_database
from services.jira_service import jira_service

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.is_running = False
        self.sync_interval = 300  # 5 minutes in seconds

    async def start_scheduler(self):
        """Start the scheduler service"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("Starting scheduler service")
        
        while self.is_running:
            try:
                await self.sync_all_users_data()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def stop_scheduler(self):
        """Stop the scheduler service"""
        self.is_running = False
        logger.info("Stopping scheduler service")

    async def sync_all_users_data(self):
        """Sync Jira data for all users with active connections"""
        try:
            logger.info("Starting periodic sync for all users")
            db = get_database()
            credentials_collection = db.jira_credentials
            
            # Find all active credentials
            cursor = credentials_collection.find({"is_active": True})
            async for credentials_doc in cursor:
                try:
                    user_id = credentials_doc["user_id"]
                    logger.info(f"Syncing data for user {user_id}")
                    
                    # Sync user data
                    success = await jira_service.sync_jira_data(user_id)
                    if success:
                        logger.info(f"Successfully synced data for user {user_id}")
                    else:
                        logger.warning(f"Failed to sync data for user {user_id}")
                        
                except Exception as e:
                    logger.error(f"Failed to sync data for user {credentials_doc['user_id']}: {e}")
                    continue
                    
            logger.info("Completed periodic sync for all users")
            
        except Exception as e:
            logger.error(f"Failed to sync all users data: {e}")

# Create global scheduler service instance
scheduler_service = SchedulerService()