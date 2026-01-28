from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.jira import JiraTask

class TaskFilter(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    project: Optional[str] = None
    assignee: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    tasks: List[JiraTask]
    total: int
    page: int
    size: int

class TaskCreate(BaseModel):
    summary: str
    project_key: str
    issue_type: str
    priority: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    duedate: Optional[datetime] = None

class TaskUpdate(BaseModel):
    summary: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    duedate: Optional[datetime] = None