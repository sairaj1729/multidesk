from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectFilter(BaseModel):
    search: Optional[str] = None
    lead: Optional[str] = None

class JiraProjectResponse(BaseModel):
    id: str
    jira_id: str
    key: str
    name: str
    description: Optional[str] = None
    lead: str
    created: datetime
    updated: datetime

class ProjectListResponse(BaseModel):
    projects: List[JiraProjectResponse]
    total: int
    page: int
    size: int