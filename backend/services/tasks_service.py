import logging
from typing import List, Optional
from datetime import datetime
from db import get_database
from models.jira import JiraTask
from models.tasks import TaskFilter

logger = logging.getLogger(__name__)

class TasksService:
    async def get_tasks(self, user_id: str, filter_params: TaskFilter, page: int = 1, size: int = 50) -> dict:
        """Get tasks for a user with filtering and pagination"""
        try:
            db = get_database()
            tasks_collection = db.jira_tasks
            
            # Build query based on filters
            query = {"user_id": user_id}
            
            if filter_params.search:
                query["$or"] = [
                    {"summary": {"$regex": filter_params.search, "$options": "i"}},
                    {"key": {"$regex": filter_params.search, "$options": "i"}}
                ]
            
            if filter_params.status:
                query["status"] = filter_params.status
            
            if filter_params.priority:
                query["priority"] = filter_params.priority
            
            if filter_params.project:
                query["project_key"] = filter_params.project
            
            if filter_params.assignee:
                query["assignee"] = filter_params.assignee
            
            # Calculate pagination
            skip = (page - 1) * size
            
            # Get total count
            total = await tasks_collection.count_documents(query)
            
            # Get tasks with pagination
            cursor = tasks_collection.find(query).skip(skip).limit(size).sort("updated", -1)
            tasks = []
            async for doc in cursor:
                task = JiraTask(
                    id=str(doc["_id"]),
                    user_id=doc["user_id"],
                    jira_id=doc["jira_id"],
                    key=doc["key"],
                    summary=doc["summary"],
                    status=doc["status"],
                    priority=doc["priority"],
                    assignee=doc["assignee"],
                    assignee_email=doc.get("assignee_email"),
                    assignee_account_id=doc.get("assignee_account_id"),
                    story_points=doc.get("story_points"),
                    start_date=doc.get("start_date"),
                    sprint=doc.get("sprint"),
                    created=doc["created"],
                    updated=doc["updated"],
                    duedate=doc["duedate"],
                    project_key=doc["project_key"],
                    project_name=doc["project_name"],
                    issue_type=doc["issue_type"]
                )
                tasks.append(task)
            
            return {
                "tasks": tasks,
                "total": total,
                "page": page,
                "size": size
            }
            
        except Exception as e:
            logger.error(f"Failed to get tasks for user {user_id}: {e}")
            return {
                "tasks": [],
                "total": 0,
                "page": page,
                "size": size
            }

    async def get_task_by_id(self, user_id: str, task_id: str) -> Optional[JiraTask]:
        """Get a specific task by ID"""
        try:
            db = get_database()
            tasks_collection = db.jira_tasks
            
            # Find task that belongs to the user
            doc = await tasks_collection.find_one({"_id": task_id, "user_id": user_id})
            if doc:
                return JiraTask(
                    id=str(doc["_id"]),
                    user_id=doc["user_id"],
                    jira_id=doc["jira_id"],
                    key=doc["key"],
                    summary=doc["summary"],
                    status=doc["status"],
                    priority=doc["priority"],
                    assignee=doc["assignee"],
                    assignee_email=doc.get("assignee_email"),
                    assignee_account_id=doc.get("assignee_account_id"),
                    created=doc["created"],
                    updated=doc["updated"],
                    duedate=doc["duedate"],
                    project_key=doc["project_key"],
                    project_name=doc["project_name"],
                    issue_type=doc["issue_type"]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get task {task_id} for user {user_id}: {e}")
            return None

# Create global tasks service instance
tasks_service = TasksService()