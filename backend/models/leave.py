from pydantic import BaseModel, EmailStr
from datetime import date, datetime

class Leave(BaseModel):
    employee_email: EmailStr
    leave_start: date
    leave_end: date
    file_id: str
    uploaded_at: datetime
