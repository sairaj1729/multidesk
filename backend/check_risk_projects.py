import asyncio
from db import get_database, connect_to_mongo, close_mongo_connection

async def check_risk_project_keys():
    """Check what project_key values exist in risk data"""
    try:
        await connect_to_mongo()
        db = get_database()
        risks_collection = db.risk_alerts
        
        user_id = "6990a3c637ed27735ff66301"
        
        print("🔍 Checking Risk Project Keys...")
        print("=" * 50)
        
        # Get all unique project_key values for this user
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$project_key", "count": {"$sum": 1}}}
        ]
        
        project_stats = await risks_collection.aggregate(pipeline).to_list(None)
        
        print("Project key distribution in risks:")
        for stat in project_stats:
            print(f"  '{stat['_id']}': {stat['count']} risks")
        
        # Check if any risks have project_key as None or missing
        no_project_risks = await risks_collection.count_documents({
            "user_id": user_id,
            "project_key": {"$exists": False}
        })
        print(f"\nRisks with missing project_key: {no_project_risks}")
        
        null_project_risks = await risks_collection.count_documents({
            "user_id": user_id,
            "project_key": None
        })
        print(f"Risks with null project_key: {null_project_risks}")
        
        # Show some sample risks with missing project_key
        if no_project_risks > 0:
            print("\nSample risks with missing project_key:")
            sample = await risks_collection.find({
                "user_id": user_id,
                "project_key": {"$exists": False}
            }).limit(3).to_list(None)
            
            for risk in sample:
                print(f"  - {risk['task_key']}: {risk['risk_level']} | assignee: {risk.get('assignee', 'Unknown')}")
        
        # Check what project keys exist in the tasks
        tasks_collection = db.jira_tasks
        task_projects = await tasks_collection.distinct("project_key", {"user_id": user_id})
        print(f"\nProject keys in tasks: {task_projects}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_risk_project_keys())