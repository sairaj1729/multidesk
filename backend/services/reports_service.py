import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from db import get_database
from models.reports import (
    ReportMetadata, 
    ReportDataPoint, 
    ReportResponse, 
    ReportListResponse, 
    ReportFilter,
    ReportGenerationRequest
)
from models.jira import JiraTask, JiraProject
from models.auth import UserResponse
import uuid

logger = logging.getLogger(__name__)

class ReportsService:
    async def get_available_reports(self, user_id: str, page: int = 1, size: int = 50) -> ReportListResponse:
        """Get list of available reports for the user"""
        try:
            db = get_database()
            reports_collection = db.reports
            
            # Build query for user's reports or public reports
            query = {
                "$or": [
                    {"created_by": user_id},
                    {"is_public": True}
                ]
            }
            
            # Calculate pagination
            skip = (page - 1) * size
            
            # Get total count
            total = await reports_collection.count_documents(query)
            
            # Get reports with pagination
            cursor = reports_collection.find(query).skip(skip).limit(size).sort("created_at", -1)
            reports = []
            async for doc in cursor:
                report = ReportMetadata(
                    id=str(doc["_id"]),
                    name=doc["name"],
                    description=doc["description"],
                    type=doc["type"],
                    created_by=doc["created_by"],
                    created_at=doc["created_at"],
                    updated_at=doc["updated_at"],
                    is_public=doc.get("is_public", False)
                )
                reports.append(report)
            
            return ReportListResponse(
                reports=reports,
                total=total,
                page=page,
                size=size
            )
            
        except Exception as e:
            logger.error(f"Failed to get available reports for user {user_id}: {e}")
            return ReportListResponse(
                reports=[],
                total=0,
                page=page,
                size=size
            )

    async def get_report_by_id(self, user_id: str, report_id: str) -> Optional[ReportResponse]:
        """Get a specific report by ID"""
        try:
            db = get_database()
            reports_collection = db.reports
            
            # Find report that belongs to the user or is public
            doc = await reports_collection.find_one({
                "_id": report_id,
                "$or": [
                    {"created_by": user_id},
                    {"is_public": True}
                ]
            })
            
            if not doc:
                return None
            
            # Get report data
            data_collection = db.report_data
            data_cursor = data_collection.find({"report_id": report_id})
            data_points = []
            async for data_doc in data_cursor:
                data_point = ReportDataPoint(
                    label=data_doc["label"],
                    value=data_doc["value"],
                    metadata=data_doc.get("metadata")
                )
                data_points.append(data_point)
            
            # Get summary data
            summary_collection = db.report_summaries
            summary_doc = await summary_collection.find_one({"report_id": report_id})
            summary = summary_doc.get("data") if summary_doc else None
            
            report_metadata = ReportMetadata(
                id=str(doc["_id"]),
                name=doc["name"],
                description=doc["description"],
                type=doc["type"],
                created_by=doc["created_by"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                is_public=doc.get("is_public", False)
            )
            
            return ReportResponse(
                metadata=report_metadata,
                data=data_points,
                summary=summary,
                filters=doc.get("filters")
            )
            
        except Exception as e:
            logger.error(f"Failed to get report {report_id} for user {user_id}: {e}")
            return None

    async def generate_report(self, user_id: str, request: ReportGenerationRequest) -> Optional[ReportResponse]:
        """Generate a new report based on the request"""
        try:
            db = get_database()
            reports_collection = db.reports
            
            # Create report metadata
            report_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            report_metadata_doc = {
                "_id": report_id,
                "name": request.name,
                "description": request.description,
                "type": request.report_type,
                "created_by": user_id,
                "created_at": now,
                "updated_at": now,
                "is_public": request.is_public,
                "filters": {
                    "report_type": request.report_type,
                    "start_date": request.start_date,
                    "end_date": request.end_date,
                    "project_key": request.project_key,
                    "user_id": request.user_id
                }
            }
            
            # Insert report metadata
            await reports_collection.insert_one(report_metadata_doc)
            
            # Generate report data based on type
            data_points = []
            summary = {}
            
            if request.report_type == "task_summary":
                data_points, summary = await self._generate_task_summary_report(user_id, request)
            elif request.report_type == "user_performance":
                data_points, summary = await self._generate_user_performance_report(user_id, request)
            elif request.report_type == "project_progress":
                data_points, summary = await self._generate_project_progress_report(user_id, request)
            elif request.report_type == "time_tracking":
                data_points, summary = await self._generate_time_tracking_report(user_id, request)
            elif request.report_type == "resource_utilization":
                data_points, summary = await self._generate_resource_utilization_report(user_id, request)
            
            # Store report data
            if data_points:
                data_collection = db.report_data
                data_docs = [
                    {
                        "report_id": report_id,
                        "label": point.label,
                        "value": point.value,
                        "metadata": point.metadata
                    }
                    for point in data_points
                ]
                await data_collection.insert_many(data_docs)
            
            # Store summary data
            if summary:
                summary_collection = db.report_summaries
                await summary_collection.insert_one({
                    "report_id": report_id,
                    "data": summary
                })
            
            # Return the generated report
            report_metadata = ReportMetadata(
                id=report_id,
                name=request.name,
                description=request.description,
                type=request.report_type,
                created_by=user_id,
                created_at=now,
                updated_at=now,
                is_public=request.is_public
            )
            
            return ReportResponse(
                metadata=report_metadata,
                data=data_points,
                summary=summary,
                filters=request.dict()
            )
            
        except Exception as e:
            logger.error(f"Failed to generate report for user {user_id}: {e}")
            return None

    async def _generate_task_summary_report(self, user_id: str, request: ReportGenerationRequest) -> tuple:
        """Generate task summary report"""
        try:
            db = get_database()
            tasks_collection = db.jira_tasks
            
            # Build query based on filters
            query = {"user_id": user_id}
            
            if request.project_key:
                query["project_key"] = request.project_key
            
            if request.start_date or request.end_date:
                date_query = {}
                if request.start_date:
                    date_query["$gte"] = request.start_date
                if request.end_date:
                    date_query["$lte"] = request.end_date
                query["created"] = date_query
            
            # Get tasks
            cursor = tasks_collection.find(query)
            tasks = []
            status_counts = {}
            priority_counts = {}
            assignee_counts = {}
            
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
                    created=doc["created"],
                    updated=doc["updated"],
                    duedate=doc["duedate"],
                    project_key=doc["project_key"],
                    project_name=doc["project_name"],
                    issue_type=doc["issue_type"]
                )
                tasks.append(task)
                
                # Count by status
                status_counts[task.status] = status_counts.get(task.status, 0) + 1
                
                # Count by priority
                priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1
                
                # Count by assignee
                assignee = task.assignee or "Unassigned"
                assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
            
            # Create data points
            data_points = []
            
            # Status distribution
            for status, count in status_counts.items():
                data_points.append(ReportDataPoint(
                    label=f"Status: {status}",
                    value=count,
                    metadata={"category": "status"}
                ))
            
            # Priority distribution
            for priority, count in priority_counts.items():
                data_points.append(ReportDataPoint(
                    label=f"Priority: {priority}",
                    value=count,
                    metadata={"category": "priority"}
                ))
            
            # Assignee distribution
            for assignee, count in assignee_counts.items():
                data_points.append(ReportDataPoint(
                    label=f"Assignee: {assignee}",
                    value=count,
                    metadata={"category": "assignee"}
                ))
            
            # Summary statistics
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.status in ["Done", "Closed", "Resolved"]])
            in_progress_tasks = len([t for t in tasks if t.status in ["In Progress", "In Review"]])
            overdue_tasks = len([t for t in tasks if t.duedate and t.duedate < datetime.utcnow() and t.status not in ["Done", "Closed", "Resolved"]])
            
            summary = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "overdue_tasks": overdue_tasks,
                "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
            }
            
            return data_points, summary
            
        except Exception as e:
            logger.error(f"Failed to generate task summary report for user {user_id}: {e}")
            return [], {}

    async def _generate_user_performance_report(self, user_id: str, request: ReportGenerationRequest) -> tuple:
        """Generate user performance report"""
        try:
            db = get_database()
            tasks_collection = db.jira_tasks
            
            # For user performance, we might want to look at tasks assigned to users
            query = {"user_id": user_id}
            
            if request.user_id:
                query["assignee_id"] = request.user_id
            elif request.project_key:
                query["project_key"] = request.project_key
            
            # Get tasks
            cursor = tasks_collection.find(query)
            tasks = []
            user_task_counts = {}
            
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
                    created=doc["created"],
                    updated=doc["updated"],
                    duedate=doc["duedate"],
                    project_key=doc["project_key"],
                    project_name=doc["project_name"],
                    issue_type=doc["issue_type"]
                )
                tasks.append(task)
                
                # Count tasks per user
                assignee = task.assignee or "Unassigned"
                user_task_counts[assignee] = user_task_counts.get(assignee, 0) + 1
            
            # Create data points
            data_points = []
            
            # Tasks per user
            for user, count in user_task_counts.items():
                data_points.append(ReportDataPoint(
                    label=f"User: {user}",
                    value=count,
                    metadata={"category": "user_tasks"}
                ))
            
            # Summary statistics
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.status in ["Done", "Closed", "Resolved"]])
            
            summary = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
                "active_users": len(user_task_counts)
            }
            
            return data_points, summary
            
        except Exception as e:
            logger.error(f"Failed to generate user performance report for user {user_id}: {e}")
            return [], {}

    async def _generate_project_progress_report(self, user_id: str, request: ReportGenerationRequest) -> tuple:
        """Generate project progress report"""
        try:
            db = get_database()
            tasks_collection = db.jira_tasks
            
            # Build query
            query = {"user_id": user_id}
            
            if request.project_key:
                query["project_key"] = request.project_key
            
            # Get tasks grouped by project
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$project_key",
                    "project_name": {"$first": "$project_name"},
                    "total_tasks": {"$sum": 1},
                    "completed_tasks": {"$sum": {"$cond": [
                        {"$in": ["$status", ["Done", "Closed", "Resolved"]]},
                        1,
                        0
                    ]}},
                    "in_progress_tasks": {"$sum": {"$cond": [
                        {"$in": ["$status", ["In Progress", "In Review"]]},
                        1,
                        0
                    ]}}
                }}
            ]
            
            cursor = tasks_collection.aggregate(pipeline)
            project_data = []
            data_points = []
            
            async for doc in cursor:
                project_info = {
                    "project_key": doc["_id"],
                    "project_name": doc["project_name"],
                    "total_tasks": doc["total_tasks"],
                    "completed_tasks": doc["completed_tasks"],
                    "in_progress_tasks": doc["in_progress_tasks"],
                    "completion_rate": round((doc["completed_tasks"] / doc["total_tasks"] * 100) if doc["total_tasks"] > 0 else 0, 2)
                }
                project_data.append(project_info)
                
                # Add data points
                data_points.append(ReportDataPoint(
                    label=f"Project: {doc['project_name']} (Total)",
                    value=doc["total_tasks"],
                    metadata={"category": "project_total", "project_key": doc["_id"]}
                ))
                
                data_points.append(ReportDataPoint(
                    label=f"Project: {doc['project_name']} (Completed)",
                    value=doc["completed_tasks"],
                    metadata={"category": "project_completed", "project_key": doc["_id"]}
                ))
                
                data_points.append(ReportDataPoint(
                    label=f"Project: {doc['project_name']} (Completion %)",
                    value=project_info["completion_rate"],
                    metadata={"category": "project_completion", "project_key": doc["_id"]}
                ))
            
            # Summary
            total_projects = len(project_data)
            avg_completion_rate = round(sum(p["completion_rate"] for p in project_data) / total_projects if total_projects > 0 else 0, 2)
            
            summary = {
                "total_projects": total_projects,
                "average_completion_rate": avg_completion_rate,
                "projects": project_data
            }
            
            return data_points, summary
            
        except Exception as e:
            logger.error(f"Failed to generate project progress report for user {user_id}: {e}")
            return [], {}

    async def _generate_time_tracking_report(self, user_id: str, request: ReportGenerationRequest) -> tuple:
        """Generate time tracking report"""
        try:
            # For now, we'll simulate time tracking data
            # In a real implementation, this would connect to Jira's time tracking API
            
            # Simulated data
            data_points = [
                ReportDataPoint(
                    label="Total Estimated Hours",
                    value=120,
                    metadata={"category": "estimated"}
                ),
                ReportDataPoint(
                    label="Total Logged Hours",
                    value=95,
                    metadata={"category": "logged"}
                ),
                ReportDataPoint(
                    label="Remaining Hours",
                    value=25,
                    metadata={"category": "remaining"}
                ),
                ReportDataPoint(
                    label="Time Variance (%)",
                    value=20.8,
                    metadata={"category": "variance"}
                )
            ]
            
            summary = {
                "total_estimated": 120,
                "total_logged": 95,
                "remaining": 25,
                "variance_percentage": 20.8
            }
            
            return data_points, summary
            
        except Exception as e:
            logger.error(f"Failed to generate time tracking report for user {user_id}: {e}")
            return [], {}

    async def _generate_resource_utilization_report(self, user_id: str, request: ReportGenerationRequest) -> tuple:
        """Generate resource utilization report"""
        try:
            db = get_database()
            tasks_collection = db.jira_tasks
            
            # Build query
            query = {"user_id": user_id}
            
            if request.project_key:
                query["project_key"] = request.project_key
            
            # Get tasks and analyze resource distribution
            cursor = tasks_collection.find(query)
            tasks = []
            assignee_workload = {}
            
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
                    created=doc["created"],
                    updated=doc["updated"],
                    duedate=doc["duedate"],
                    project_key=doc["project_key"],
                    project_name=doc["project_name"],
                    issue_type=doc["issue_type"]
                )
                tasks.append(task)
                
                # Track workload by assignee
                assignee = task.assignee or "Unassigned"
                assignee_workload[assignee] = assignee_workload.get(assignee, 0) + 1
            
            # Create data points
            data_points = []
            
            # Workload distribution
            for assignee, count in assignee_workload.items():
                data_points.append(ReportDataPoint(
                    label=f"Assignee: {assignee}",
                    value=count,
                    metadata={"category": "workload"}
                ))
            
            # Identify overloaded resources (simplified)
            avg_workload = sum(assignee_workload.values()) / len(assignee_workload) if assignee_workload else 0
            overloaded_resources = [user for user, count in assignee_workload.items() if count > avg_workload * 1.5]
            
            # Summary
            total_assignees = len(assignee_workload)
            max_workload = max(assignee_workload.values()) if assignee_workload else 0
            min_workload = min(assignee_workload.values()) if assignee_workload else 0
            
            summary = {
                "total_assignees": total_assignees,
                "max_workload": max_workload,
                "min_workload": min_workload,
                "avg_workload": round(avg_workload, 2),
                "overloaded_resources": overloaded_resources
            }
            
            return data_points, summary
            
        except Exception as e:
            logger.error(f"Failed to generate resource utilization report for user {user_id}: {e}")
            return [], {}

    async def delete_report(self, user_id: str, report_id: str) -> bool:
        """Delete a report"""
        try:
            db = get_database()
            reports_collection = db.reports
            
            # Check if user owns the report
            doc = await reports_collection.find_one({
                "_id": report_id,
                "created_by": user_id
            })
            
            if not doc:
                return False
            
            # Delete report metadata
            await reports_collection.delete_one({"_id": report_id})
            
            # Delete associated data
            data_collection = db.report_data
            await data_collection.delete_many({"report_id": report_id})
            
            summary_collection = db.report_summaries
            await summary_collection.delete_many({"report_id": report_id})
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete report {report_id} for user {user_id}: {e}")
            return False

# Create global reports service instance
reports_service = ReportsService()