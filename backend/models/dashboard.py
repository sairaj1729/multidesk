from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.jira import DashboardStats, EisenhowerQuadrant, AnalyticsData

class DashboardResponse(BaseModel):
    stats: DashboardStats
    eisenhower: EisenhowerQuadrant
    analytics: AnalyticsData