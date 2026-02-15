import asyncio
from db import get_database, connect_to_mongo, close_mongo_connection

async def fix_risk_project_keys():
    """Fix existing risks by adding missing project_key fields"""
    try:
        await connect_to_mongo()
        db = get_database()
        risks_collection = db.risk_alerts
        tasks_collection = db.jira_tasks
        
        user_id = "6990a3c637ed27735ff66301"
        
        print("🔧 Fixing Risk Project Keys...")
        print("=" * 50)
        
        # Find risks missing project_key
        risks_without_project = await risks_collection.find({
            "user_id": user_id,
            "$or": [
                {"project_key": {"$exists": False}},
                {"project_key": None}
            ]
        }).to_list(None)
        
        print(f"Found {len(risks_without_project)} risks missing project_key")
        
        if not risks_without_project:
            print("✅ All risks already have project_key")
            return
            
        # Update each risk
        updated_count = 0
        for risk in risks_without_project:
            task_key = risk["task_key"]
            
            # Find the corresponding task to get project info
            task = await tasks_collection.find_one({
                "user_id": user_id,
                "key": task_key
            })
            
            if task:
                # Update the risk with project information
                result = await risks_collection.update_one(
                    {"_id": risk["_id"]},
                    {
                        "$set": {
                            "project_key": task.get("project_key"),
                            "project_name": task.get("project_name")
                        }
                    }
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"✅ Updated {task_key}: {task.get('project_key')}")
            else:
                print(f"❌ Could not find task {task_key} for risk update")
        
        print(f"\n✅ Updated {updated_count} risks with project_key information")
        
        # Verify the fix
        remaining_missing = await risks_collection.count_documents({
            "user_id": user_id,
            "$or": [
                {"project_key": {"$exists": False}},
                {"project_key": None}
            ]
        })
        
        print(f"Remaining risks with missing project_key: {remaining_missing}")
        
        # Test the query now works
        project_risks = await risks_collection.count_documents({
            "user_id": user_id,
            "project_key": "SCRUM"
        })
        print(f"Risks in SCRUM project: {project_risks}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(fix_risk_project_keys())