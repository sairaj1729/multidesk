from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JiraCredentialsCreate(BaseModel):
    domain: str
    email: str
    api_token: str

class JiraCredentialsInDB(BaseModel):
    id: str
    user_id: str
    domain: str
    email: str
    api_token: str  # This will be encrypted in the database
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class JiraTask(BaseModel):
    id: str
    user_id: str
    jira_id: str
    key: str
    summary: str
    status: str
    priority: str
    assignee: str
    assignee_email: Optional[str]
    assignee_account_id: Optional[str] = None
    story_points: Optional[int] = None
    start_date: Optional[datetime] = None
    sprint: Optional[str] = None
    created: datetime
    updated: datetime
    duedate: Optional[datetime] = None
    project_key: str
    project_name: str
    issue_type: str
    




class JiraProject(BaseModel):
    id: str
    user_id: str
    jira_id: str
    key: str
    name: str
    description: Optional[str] = None
    lead: str
    created: datetime
    updated: datetime

class JiraUser(BaseModel):
    id: str
    user_id: str  # MultiDesk user ID
    jira_account_id: str
    display_name: str
    email_address: str
    active: bool
    timezone: Optional[str] = None

class DashboardStats(BaseModel):
    total_tasks: int
    todo_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
    total_tasks_trend: float
    todo_tasks_trend: float
    in_progress_tasks_trend: float
    completed_tasks_trend: float
    overdue_tasks_trend: float

class EisenhowerQuadrant(BaseModel):
    urgent_important: int
    urgent_not_important: int
    not_urgent_important: int
    not_urgent_not_important: int
    urgent_important_tasks: Optional[List[JiraTask]] = []
    urgent_not_important_tasks: Optional[List[JiraTask]] = []
    not_urgent_important_tasks: Optional[List[JiraTask]] = []
    not_urgent_not_important_tasks: Optional[List[JiraTask]] = []

class TaskByStatus(BaseModel):
    name: str
    value: int

class TaskVelocityData(BaseModel):
    month: str
    tasks: int
    completed: int

class IssueTypeData(BaseModel):
    name: str
    value: int

class AnalyticsData(BaseModel):
    tasks_by_status: List[TaskByStatus]
    task_velocity: List[TaskVelocityData]
    issue_type_distribution: List[IssueTypeData]

class FileUpload(BaseModel):
    id: str
    user_id: str
    filename: str
    size: int
    content_type: str
    status: str  # success, processing, error
    records: int
    uploader: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None