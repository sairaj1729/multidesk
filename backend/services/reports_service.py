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
            elif request.report_type == "risk_analysis":
                data_points, summary = await self._generate_risk_analysis_report(user_id, request)
            
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
            
            if request.user_id:
                # Match on either assignee_account_id or assignee name/email
                query["$or"] = [
                    {"assignee_account_id": request.user_id},
                    {"assignee": request.user_id}  # For backward compatibility
                ]
            
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
                    assignee_account_id=doc.get("assignee_account_id"),
                    assignee_email=doc.get("assignee_email"),
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
                # Match on either assignee_account_id or assignee name/email
                query["$or"] = [
                    {"assignee_account_id": request.user_id},
                    {"assignee": request.user_id}  # For backward compatibility
                ]
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
                    assignee_account_id=doc.get("assignee_account_id"),
                    assignee_email=doc.get("assignee_email"),
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
                
                # Count tasks per user - prioritize using account_id if available
                assignee_id = task.assignee_account_id or task.assignee or "Unassigned"
                assignee_display = task.assignee or "Unassigned"
                
                # Use display name for the count dictionary
                user_task_counts[assignee_display] = user_task_counts.get(assignee_display, 0) + 1
            
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
            
            # Build query - filter by user_id first
            query = {"user_id": user_id}
            
            # Add project filter if specified
            if request.project_key:
                query["project_key"] = request.project_key
            
            # Add user assignment filter if specified
            if request.user_id:
                # Match on either assignee_account_id or assignee name/email
                query["$or"] = [
                    {"assignee_account_id": request.user_id},
                    {"assignee": request.user_id}  # For backward compatibility
                ]
            
            # Debug logging
            logger.info(f"Project progress report query for user {user_id}: {query}")
            
            # Get all tasks matching the criteria
            tasks_cursor = tasks_collection.find(query)
            tasks = []
            async for task in tasks_cursor:
                tasks.append(task)
            
            logger.info(f"Found {len(tasks)} tasks for project progress report")
            
            if not tasks:
                logger.warning(f"No tasks found for user {user_id} with query: {query}")
                return [], {"total_projects": 0, "average_completion_rate": 0, "projects": [], "message": "No tasks found matching the criteria"}
            
            # Group tasks by project
            projects = {}
            for task in tasks:
                project_key = task.get('project_key')
                project_name = task.get('project_name', 'Unknown Project')
                
                if project_key:
                    if project_key not in projects:
                        projects[project_key] = {
                            'project_name': project_name,
                            'total_tasks': 0,
                            'completed_tasks': 0,
                            'in_progress_tasks': 0,
                            'todo_tasks': 0,
                            'other_tasks': 0
                        }
                    
                    projects[project_key]['total_tasks'] += 1
                    
                    # Categorize by status
                    status = task.get('status', '').lower()
                    if status in ['done', 'closed', 'resolved']:
                        projects[project_key]['completed_tasks'] += 1
                    elif status in ['in progress', 'in review']:
                        projects[project_key]['in_progress_tasks'] += 1
                    elif status in ['to do', 'todo']:
                        projects[project_key]['todo_tasks'] += 1
                    else:
                        projects[project_key]['other_tasks'] += 1
            
            # Create data points and project data
            project_data = []
            data_points = []
            
            for project_key, project_info in projects.items():
                # Calculate completion rate
                completion_rate = round((project_info['completed_tasks'] / project_info['total_tasks'] * 100) if project_info['total_tasks'] > 0 else 0, 2)
                
                # Add completion rate to project info
                project_info['completion_rate'] = completion_rate
                project_info['project_key'] = project_key
                
                project_data.append(project_info)
                
                # Create data points for visualization
                data_points.append(ReportDataPoint(
                    label=f"Project: {project_info['project_name']} (Total Tasks)",
                    value=project_info['total_tasks'],
                    metadata={"category": "project_total", "project_key": project_key}
                ))
                
                data_points.append(ReportDataPoint(
                    label=f"Project: {project_info['project_name']} (Completed)",
                    value=project_info['completed_tasks'],
                    metadata={"category": "project_completed", "project_key": project_key}
                ))
                
                data_points.append(ReportDataPoint(
                    label=f"Project: {project_info['project_name']} (In Progress)",
                    value=project_info['in_progress_tasks'],
                    metadata={"category": "project_in_progress", "project_key": project_key}
                ))
                
                data_points.append(ReportDataPoint(
                    label=f"Project: {project_info['project_name']} (To Do)",
                    value=project_info['todo_tasks'],
                    metadata={"category": "project_todo", "project_key": project_key}
                ))
                
                data_points.append(ReportDataPoint(
                    label=f"Project: {project_info['project_name']} (Completion %)",
                    value=completion_rate,
                    metadata={"category": "project_completion", "project_key": project_key}
                ))
            
            # Calculate summary statistics
            total_projects = len(project_data)
            if total_projects > 0:
                avg_completion_rate = round(sum(p['completion_rate'] for p in project_data) / total_projects, 2)
                total_tasks_all_projects = sum(p['total_tasks'] for p in project_data)
                total_completed_all_projects = sum(p['completed_tasks'] for p in project_data)
                overall_completion_rate = round((total_completed_all_projects / total_tasks_all_projects * 100) if total_tasks_all_projects > 0 else 0, 2)
            else:
                avg_completion_rate = 0
                overall_completion_rate = 0
                total_tasks_all_projects = 0
                total_completed_all_projects = 0
            
            summary = {
                "total_projects": total_projects,
                "average_completion_rate": avg_completion_rate,
                "overall_completion_rate": overall_completion_rate,
                "total_tasks": total_tasks_all_projects,
                "completed_tasks": total_completed_all_projects,
                "projects": project_data,
                "filters_applied": {
                    "user_id": user_id,
                    "project_key": request.project_key,
                    "assignee_filter": request.user_id
                }
            }
            
            logger.info(f"Project progress report generated successfully for user {user_id}")
            logger.info(f"Summary: {total_projects} projects, {total_tasks_all_projects} total tasks, {overall_completion_rate}% overall completion")
            
            return data_points, summary
            
        except Exception as e:
            logger.error(f"Failed to generate project progress report for user {user_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return [], {"error": str(e), "total_projects": 0, "average_completion_rate": 0}

    async def _generate_time_tracking_report(self, user_id: str, request: ReportGenerationRequest) -> tuple:
        """Generate time tracking report"""
        try:
            db = get_database()
            tasks_collection = db.jira_tasks
            
            # Build query
            query = {"user_id": user_id}
            
            if request.project_key:
                query["project_key"] = request.project_key
            
            if request.user_id:
                # Match on either assignee_account_id or assignee name/email
                query["$or"] = [
                    {"assignee_account_id": request.user_id},
                    {"assignee": request.user_id}  # For backward compatibility
                ]
            
            # Get tasks
            cursor = tasks_collection.find(query)
            tasks = []
            total_estimated_hours = 0
            total_story_points = 0
            
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
                    assignee_account_id=doc.get("assignee_account_id"),
                    assignee_email=doc.get("assignee_email"),
                    story_points=doc.get("story_points"),
                    created=doc["created"],
                    updated=doc["updated"],
                    duedate=doc["duedate"],
                    project_key=doc["project_key"],
                    project_name=doc["project_name"],
                    issue_type=doc["issue_type"]
                )
                tasks.append(task)
                
                # Add to estimated hours if available
                if task.story_points:
                    total_story_points += float(task.story_points)
                    # Convert story points to hours (typically 1 story point = 1 hour)
                    total_estimated_hours += float(task.story_points)
            
            # Create data points
            data_points = [
                ReportDataPoint(
                    label="Total Estimated Hours",
                    value=round(total_estimated_hours, 2),
                    metadata={"category": "estimated"}
                ),
                ReportDataPoint(
                    label="Total Story Points",
                    value=round(total_story_points, 2),
                    metadata={"category": "story_points"}
                ),
                ReportDataPoint(
                    label="Total Tasks",
                    value=len(tasks),
                    metadata={"category": "total_tasks"}
                ),
                ReportDataPoint(
                    label="Completed Tasks",
                    value=len([t for t in tasks if t.status in ["Done", "Closed", "Resolved"]]),
                    metadata={"category": "completed_tasks"}
                )
            ]
            
            # Calculate summary
            completed_tasks = len([t for t in tasks if t.status in ["Done", "Closed", "Resolved"]])
            completion_rate = round((completed_tasks / len(tasks) * 100) if len(tasks) > 0 else 0, 2)
            
            summary = {
                "total_estimated_hours": round(total_estimated_hours, 2),
                "total_story_points": round(total_story_points, 2),
                "total_tasks": len(tasks),
                "completed_tasks": completed_tasks,
                "completion_rate": completion_rate
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
            
            if request.user_id:
                # Match on either assignee_account_id or assignee name/email
                query["$or"] = [
                    {"assignee_account_id": request.user_id},
                    {"assignee": request.user_id}  # For backward compatibility
                ]
            
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
                    assignee_account_id=doc.get("assignee_account_id"),
                    assignee_email=doc.get("assignee_email"),
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

    async def _generate_risk_analysis_report(self, user_id: str, request: ReportGenerationRequest) -> tuple:
        """Generate risk analysis report using risk service"""
        try:
            from services.risk_service import run_risk_analysis
            
            db = get_database()
            tasks_collection = db.jira_tasks
            risks_collection = db.risk_alerts
            
            # First, run risk analysis to ensure we have up-to-date risks
            await run_risk_analysis(user_id)
            
            # Build query for tasks
            query = {"user_id": user_id}
            
            if request.project_key:
                query["project_key"] = request.project_key
            
            if request.user_id:
                # Match on either assignee_account_id or assignee name/email
                query["$or"] = [
                    {"assignee_account_id": request.user_id},
                    {"assignee": request.user_id}  # For backward compatibility
                ]
            
            # Get tasks
            tasks = []
            cursor = tasks_collection.find(query)
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
                    assignee_account_id=doc.get("assignee_account_id"),
                    assignee_email=doc.get("assignee_email"),
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
            
            # Get risk alerts for the user with correct field mapping
            risk_query = {"user_id": user_id}
            if request.project_key:
                risk_query["project_key"] = request.project_key
            if request.user_id and request.user_id.strip():  # Only add if user_id is provided and not empty
                # Use assignee_account_id to match risk service storage
                risk_query["assignee_account_id"] = request.user_id
            
            risks = []
            risk_cursor = risks_collection.find(risk_query)
            async for doc in risk_cursor:
                risks.append(doc)
            
            # Create data points based on risk levels
            data_points = []
            risk_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            
            for risk in risks:
                risk_level = risk.get("risk_level", "UNKNOWN")
                risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            
            # Add risk counts to data points
            for level, count in risk_counts.items():
                if count > 0:  # Only add non-zero counts
                    data_points.append(ReportDataPoint(
                        label=f"Risk Level: {level}",
                        value=count,
                        metadata={"category": "risk_levels"}
                    ))
            
            # Add risk details breakdown
            high_risk_tasks = [r for r in risks if r.get("risk_level") in ["CRITICAL", "HIGH"]]
            for risk in high_risk_tasks[:10]:  # Limit to top 10 for readability
                data_points.append(ReportDataPoint(
                    label=f"High Risk: {risk.get('task_key', 'Unknown')} - {risk.get('assignee', 'Unassigned')}",
                    value=risk.get("risk_score", 0),
                    metadata={
                        "category": "high_risk_details",
                        "task_key": risk.get("task_key"),
                        "assignee": risk.get("assignee"),
                        "reasons": risk.get("reasons", [])
                    }
                ))
            
            # Also add task-based metrics
            overdue_tasks = len([t for t in tasks if t.duedate and t.duedate < datetime.utcnow() and t.status not in ["Done", "Closed", "Resolved"]])
            high_priority_tasks = len([t for t in tasks if t.priority in ["High", "Highest", "Critical"]])
            in_progress_tasks = len([t for t in tasks if t.status in ["In Progress", "In Review"]])
            unassigned_tasks = len([t for t in tasks if not t.assignee_account_id])
            
            data_points.extend([
                ReportDataPoint(
                    label="Overdue Tasks",
                    value=overdue_tasks,
                    metadata={"category": "task_metrics"}
                ),
                ReportDataPoint(
                    label="High Priority Tasks",
                    value=high_priority_tasks,
                    metadata={"category": "task_metrics"}
                ),
                ReportDataPoint(
                    label="In Progress Tasks",
                    value=in_progress_tasks,
                    metadata={"category": "task_metrics"}
                ),
                ReportDataPoint(
                    label="Unassigned Tasks",
                    value=unassigned_tasks,
                    metadata={"category": "task_metrics"}
                )
            ])
            
            # Calculate summary with more detailed metrics
            total_risks = sum(risk_counts.values())
            critical_risks = risk_counts.get("CRITICAL", 0)
            high_risks = risk_counts.get("HIGH", 0)
            completion_rate = round((len([t for t in tasks if t.status in ["Done", "Closed", "Resolved"]]) / len(tasks) * 100) if len(tasks) > 0 else 0, 2)
            
            # Calculate risk exposure percentage
            high_risk_percentage = round(((critical_risks + high_risks) / total_risks * 100) if total_risks > 0 else 0, 2)
            
            summary = {
                "total_risks": total_risks,
                "critical_risks": critical_risks,
                "high_risks": high_risks,
                "medium_risks": risk_counts.get("MEDIUM", 0),
                "low_risks": risk_counts.get("LOW", 0),
                "high_risk_percentage": high_risk_percentage,
                "total_tasks": len(tasks),
                "overdue_tasks": overdue_tasks,
                "high_priority_tasks": high_priority_tasks,
                "unassigned_tasks": unassigned_tasks,
                "completion_rate": completion_rate,
                "risk_analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return data_points, summary
            
        except Exception as e:
            logger.error(f"Failed to generate risk analysis report for user {user_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return [], {"error": str(e)}

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