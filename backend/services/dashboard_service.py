import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from db import get_database
from models.jira import JiraTask, DashboardStats, EisenhowerQuadrant, TaskByStatus, TaskVelocityData, IssueTypeData, AnalyticsData

logger = logging.getLogger(__name__)

def calculate_importance(task: dict) -> int:
    score = 0

    priority = task.get("priority")
    story_points = task.get("story_points")
    issue_type = task.get("issue_type")

    # Priority weight
    if priority == "Highest":
        score += 40
    elif priority == "High":
        score += 30
    elif priority == "Medium":
        score += 15

    # Story points weight
    if story_points:
        if story_points >= 8:
            score += 20
        elif story_points >= 5:
            score += 12

    # Issue type impact
    if issue_type == "Bug":
        score += 10
    elif issue_type == "Story":
        score += 8

    return score


def calculate_urgency(task: dict) -> int:
    score = 0
    now = datetime.utcnow()

    due_date = task.get("duedate")
    status = task.get("status")

    if due_date:
        days_left = (due_date - now).days

        if days_left <= 2:
            score += 40
        elif days_left <= 5:
            score += 25
        elif days_left <= 10:
            score += 15

    # Status pressure
    if status in ["In Progress", "In Review"]:
        score += 10
    if status == "Blocked":
        score += 20

    return score


class DashboardService:
    async def get_dashboard_stats(self, user_id: str) -> DashboardStats:
        """Get dashboard statistics for a user"""
        try:
            db = get_database()
            tasks_collection = db.jira_tasks
            
            # Get total tasks
            total_tasks = await tasks_collection.count_documents({"user_id": user_id})
            
            # Get tasks in progress
            in_progress_tasks = await tasks_collection.count_documents({
                "user_id": user_id,
                "status": {"$in": ["In Progress", "In Review", "In Development"]}
            })
            
            # Get completed tasks
            completed_tasks = await tasks_collection.count_documents({
                "user_id": user_id,
                "status": {"$in": ["Done", "Closed", "Resolved"]}
            })
            
            # Get overdue tasks (tasks with due date in the past and not completed)
            overdue_tasks = await tasks_collection.count_documents({
                "user_id": user_id,
                "duedate": {"$lt": datetime.utcnow()},
                "status": {"$nin": ["Done", "Closed", "Resolved"]}
            })
            
            # Calculate trends (simplified - in a real app, you'd compare with previous period)
            total_tasks_trend = 4.5  # Simulated trend
            in_progress_tasks_trend = 8.2
            completed_tasks_trend = 12.3
            overdue_tasks_trend = 16.3
            
            return DashboardStats(
                total_tasks=total_tasks,
                in_progress_tasks=in_progress_tasks,
                completed_tasks=completed_tasks,
                overdue_tasks=overdue_tasks,
                total_tasks_trend=total_tasks_trend,
                in_progress_tasks_trend=in_progress_tasks_trend,
                completed_tasks_trend=completed_tasks_trend,
                overdue_tasks_trend=overdue_tasks_trend
            )
            
        except Exception as e:
            logger.error(f"Failed to get dashboard stats for user {user_id}: {e}")
            # Return default values
            return DashboardStats(
                total_tasks=0,
                in_progress_tasks=0,
                completed_tasks=0,
                overdue_tasks=0,
                total_tasks_trend=0.0,
                in_progress_tasks_trend=0.0,
                completed_tasks_trend=0.0,
                overdue_tasks_trend=0.0
            )

    def _classify_eisenhower(self, task: dict) -> str:
        """
        Returns one of:
        - urgent_important
        - urgent_not_important
        - not_urgent_important
        - not_urgent_not_important
        """

        today = datetime.utcnow().date()
        duedate = task.get("duedate")
        story_points = task.get("story_points") or 0
        priority = task.get("priority", "")
        status = task.get("status", "")

        # Completed tasks → Not urgent & not important
        if status in ["Done", "Closed", "Resolved"]:
            return "not_urgent_not_important"

        # Urgency
        urgent = False
        if duedate:
            days_left = (duedate.date() - today).days
            if days_left <= 3:
                urgent = True

        # Importance
        important = False
        if story_points >= 8 or priority in ["High", "Highest"]:
            important = True

        if urgent and important:
            return "urgent_important"
        if urgent and not important:
            return "urgent_not_important"
        if not urgent and important:
            return "not_urgent_important"

        return "not_urgent_not_important"



    async def get_eisenhower_matrix(self, user_id: str) -> EisenhowerQuadrant:
        try:
            db = get_database()
            tasks_collection = db.jira_tasks

            quadrants = {
                "urgent_important": [],
                "urgent_not_important": [],
                "not_urgent_important": [],
                "not_urgent_not_important": []
            }

            async for task in tasks_collection.find({
                "user_id": user_id,
                "status": {"$nin": ["Done", "Closed", "Resolved"]}
            }):
                urgency = calculate_urgency(task)
                importance = calculate_importance(task)

                enriched_task = {
                    **task,
                    "urgency": urgency,
                    "importance": importance
                }

                # Quadrant decision
                if urgency >= 40 and importance >= 40:
                    quadrants["urgent_important"].append(enriched_task)
                elif urgency >= 40 and importance < 40:
                    quadrants["urgent_not_important"].append(enriched_task)
                elif urgency < 40 and importance >= 40:
                    quadrants["not_urgent_important"].append(enriched_task)
                else:
                    quadrants["not_urgent_not_important"].append(enriched_task)

            # Sorting logic (VERY IMPORTANT)
            def sort_key(t):
                return (
                    -t["urgency"],
                    -t["importance"],
                    t.get("duedate") or datetime.max,
                    -(t.get("story_points") or 0)
                )

            for key in quadrants:
                quadrants[key].sort(key=sort_key)

            # Take top 5 only
            def build_tasks(task_list):
                return [
                    JiraTask(
                        id=str(t["_id"]),
                        user_id=t["user_id"],
                        jira_id=t["jira_id"],
                        key=t["key"],
                        summary=t["summary"],
                        status=t["status"],
                        priority=t["priority"],
                        assignee=t.get("assignee"),
                        assignee_email=t.get("assignee_email"),
                        assignee_account_id=t.get("assignee_account_id"),
                        story_points=t.get("story_points"),
                        created=t["created"],
                        updated=t["updated"],
                        duedate=t.get("duedate"),
                        project_key=t["project_key"],
                        project_name=t["project_name"],
                        issue_type=t["issue_type"],
                        start_date=t.get("start_date"),
                        sprint=t.get("sprint")
                    )
                    for t in task_list[:5]
                ]

            return EisenhowerQuadrant(
                urgent_important=len(quadrants["urgent_important"]),
                urgent_not_important=len(quadrants["urgent_not_important"]),
                not_urgent_important=len(quadrants["not_urgent_important"]),
                not_urgent_not_important=len(quadrants["not_urgent_not_important"]),

                urgent_important_tasks=build_tasks(quadrants["urgent_important"]),
                urgent_not_important_tasks=build_tasks(quadrants["urgent_not_important"]),
                not_urgent_important_tasks=build_tasks(quadrants["not_urgent_important"]),
                not_urgent_not_important_tasks=build_tasks(quadrants["not_urgent_not_important"]),
            )

        except Exception as e:
            logger.error(f"Eisenhower failed: {e}")
            return EisenhowerQuadrant(
                urgent_important=0,
                urgent_not_important=0,
                not_urgent_important=0,
                not_urgent_not_important=0,
                urgent_important_tasks=[],
                urgent_not_important_tasks=[],
                not_urgent_important_tasks=[],
                not_urgent_not_important_tasks=[]
                )

    async def get_eisenhower_tasks_by_quadrant(self, user_id: str, quadrant: str):
        db = get_database()
        tasks = db.jira_tasks

        base_query = {
            "user_id": user_id,
            "status": {"$nin": ["Done", "Closed", "Resolved"]}
        }

        if quadrant == "urgent_important":
            base_query["priority"] = {"$in": ["High", "Highest"]}

        elif quadrant == "urgent_not_important":
            base_query["priority"] = "Medium"

        elif quadrant == "not_urgent_important":
            base_query["priority"] = {"$in": ["Low"]}

        elif quadrant == "not_urgent_not_important":
            base_query["$or"] = [
                {"status": {"$in": ["Done", "Closed", "Resolved"]}},
                {"priority": "Lowest"}
            ]

        cursor = tasks.find(base_query).sort("duedate", 1)

        result = []
        async for doc in cursor:
            result.append({
                "id": str(doc["_id"]),  # ✅ FIX
                "jira_id": doc.get("jira_id"),
                "key": doc.get("key"),
                "summary": doc.get("summary"),
                "status": doc.get("status"),
                "priority": doc.get("priority"),
                "assignee": doc.get("assignee"),
                "assignee_email": doc.get("assignee_email"),
                "duedate": doc.get("duedate"),
                "story_points": doc.get("story_points"),
                "start_date": doc.get("start_date"),
                "sprint": doc.get("sprint"),
                "issue_type": doc.get("issue_type"),
                "project_key": doc.get("project_key"),
                "project_name": doc.get("project_name"),
                "created": doc.get("created"),
                "updated": doc.get("updated")
            })

        return result

    async def get_analytics_data(self, user_id: str) -> AnalyticsData:
        """Get analytics data for a user"""
        try:
            db = get_database()
            tasks_collection = db.jira_tasks
            
            # Get tasks by status
            status_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            status_cursor = tasks_collection.aggregate(status_pipeline)
            tasks_by_status = []
            async for doc in status_cursor:
                tasks_by_status.append(TaskByStatus(name=doc["_id"], value=doc["count"]))
            
            # If no data, provide default values
            if not tasks_by_status:
                tasks_by_status = [
                    TaskByStatus(name="To Do", value=25),
                    TaskByStatus(name="In Progress", value=45),
                    TaskByStatus(name="Done", value=85),
                    TaskByStatus(name="Verified", value=15)
                ]
            
            # Get task velocity data (simplified - in a real app, you'd group by month)
            task_velocity = [
                TaskVelocityData(month="Jan", tasks=40, completed=35),
                TaskVelocityData(month="Feb", tasks=45, completed=40),
                TaskVelocityData(month="Mar", tasks=38, completed=42),
                TaskVelocityData(month="Apr", tasks=55, completed=48),
                TaskVelocityData(month="May", tasks=52, completed=55),
                TaskVelocityData(month="Jun", tasks=48, completed=50)
            ]
            
            # Get issue type distribution
            type_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$issue_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            type_cursor = tasks_collection.aggregate(type_pipeline)
            issue_type_distribution = []
            async for doc in type_cursor:
                issue_type_distribution.append(IssueTypeData(name=doc["_id"], value=doc["count"]))
            
            # If no data, provide default values
            if not issue_type_distribution:
                issue_type_distribution = [
                    IssueTypeData(name="Story", value=45),
                    IssueTypeData(name="Bug", value=25),
                    IssueTypeData(name="Task", value=20),
                    IssueTypeData(name="Epic", value=10)
                ]
            
            return AnalyticsData(
                tasks_by_status=tasks_by_status,
                task_velocity=task_velocity,
                issue_type_distribution=issue_type_distribution
            )
            
        except Exception as e:
            logger.error(f"Failed to get analytics data for user {user_id}: {e}")
            # Return default values
            return AnalyticsData(
                tasks_by_status=[
                    TaskByStatus(name="Pending", value=25),
                    TaskByStatus(name="In Progress", value=45),
                    TaskByStatus(name="Done", value=85),
                    TaskByStatus(name="Verified", value=15)
                ],
                task_velocity=[
                    TaskVelocityData(month="Jan", tasks=40, completed=35),
                    TaskVelocityData(month="Feb", tasks=45, completed=40),
                    TaskVelocityData(month="Mar", tasks=38, completed=42),
                    TaskVelocityData(month="Apr", tasks=55, completed=48),
                    TaskVelocityData(month="May", tasks=52, completed=55),
                    TaskVelocityData(month="Jun", tasks=48, completed=50)
                ],
                issue_type_distribution=[
                    IssueTypeData(name="Story", value=45),
                    IssueTypeData(name="Bug", value=25),
                    IssueTypeData(name="Task", value=20),
                    IssueTypeData(name="Epic", value=10)
                ]
            )

# Create global dashboard service instance
dashboard_service = DashboardService()