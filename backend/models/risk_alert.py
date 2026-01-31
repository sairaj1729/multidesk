from pydantic import BaseModel, EmailStr
from datetime import date, datetime

class RiskAlert(BaseModel):
    task_key: str
    task_title: str
    assignee: EmailStr
    due_date: date
    leave_start: date
    leave_end: date
    risk_level: str
    status: str
    user_id: str  # Add user ownership
    created_at: datetime
