from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any

class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    issue_id: str        # "JIR-29"
    project_key: str     # "JIR"
    raw: Optional[Dict[str, Any]] = None