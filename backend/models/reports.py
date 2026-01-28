from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ReportType(str):
    TASK_SUMMARY = "task_summary"
    USER_PERFORMANCE = "user_performance"
    PROJECT_PROGRESS = "project_progress"
    TIME_TRACKING = "time_tracking"
    RESOURCE_UTILIZATION = "resource_utilization"

class ReportFilter(BaseModel):
    report_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    project_key: Optional[str] = None
    user_id: Optional[str] = None
    status: Optional[str] = None

class ReportMetadata(BaseModel):
    id: str
    name: str
    description: str
    type: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_public: bool = False

class ReportDataPoint(BaseModel):
    label: str
    value: Any
    metadata: Optional[Dict[str, Any]] = None

class ReportResponse(BaseModel):
    metadata: ReportMetadata
    data: List[ReportDataPoint]
    summary: Optional[Dict[str, Any]] = None
    filters: Optional[ReportFilter] = None

class ReportListResponse(BaseModel):
    reports: List[ReportMetadata]
    total: int
    page: int
    size: int

class ReportGenerationRequest(BaseModel):
    report_type: str
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    project_key: Optional[str] = None
    user_id: Optional[str] = None
    is_public: bool = False

class ReportExportRequest(BaseModel):
    format: str  # pdf, csv, excel
    include_charts: bool = True