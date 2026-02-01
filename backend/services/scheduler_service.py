import asyncio
import logging
from datetime import datetime, timedelta
from db import get_database
from services.jira_service import jira_service
from services.risk_service import run_risk_analysis

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.is_running = False
        self.sync_interval = 300  # 5 minutes in seconds
        self.risk_analysis_interval = 600  # 10 minutes in seconds for risk analysis

    async def start_scheduler(self):
        """Start the scheduler service"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("Starting scheduler service")
        
        while self.is_running:
            try:
                await self.sync_all_users_data()
                
                # Run risk analysis periodically
                await self.run_periodic_risk_analysis()
                
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
                        
                        # Run risk analysis for this user after successful sync
                        try:
                            risk_result = await run_risk_analysis(user_id)
                            logger.info(f"Risk analysis completed for user {user_id}: {risk_result['count']} risks found")
                        except Exception as risk_error:
                            logger.error(f"Risk analysis failed for user {user_id}: {risk_error}")
                    else:
                        logger.warning(f"Failed to sync data for user {user_id}")
                        
                except Exception as e:
                    logger.error(f"Failed to sync data for user {credentials_doc['user_id']}: {e}")
                    continue
                    
            logger.info("Completed periodic sync for all users")
            
        except Exception as e:
            logger.error(f"Failed to sync all users data: {e}")

    async def run_periodic_risk_analysis(self):
        """Run risk analysis for all users periodically"""
        try:
            logger.info("Starting periodic risk analysis for all users")
            db = get_database()
            users_collection = db.users  # Get all users to run risk analysis for
            
            # Find all users
            cursor = users_collection.find({})
            async for user_doc in cursor:
                try:
                    user_id = user_doc["_id"]
                    logger.info(f"Running risk analysis for user {user_id}")
                    
                    # Run risk analysis for this user
                    risk_result = await run_risk_analysis(str(user_id))
                    logger.info(f"Risk analysis completed for user {user_id}: {risk_result['count']} risks found")
                    
                except Exception as e:
                    logger.error(f"Failed to run risk analysis for user {user_doc['_id']}: {e}")
                    continue
                    
            logger.info("Completed periodic risk analysis for all users")
            
        except Exception as e:
            logger.error(f"Failed to run periodic risk analysis: {e}")

# Create global scheduler service instance
scheduler_service = SchedulerService()