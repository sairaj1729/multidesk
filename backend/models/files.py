from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.jira import FileUpload

class FileFilter(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None
    file_type: Optional[str] = None

class FileListResponse(BaseModel):
    files: List[FileUpload]
    total: int
    page: int
    size: int

class FileUploadResponse(BaseModel):
    id: str
    filename: str
    size: int
    content_type: str
    status: str
    records: int
    uploader: str
    uploaded_at: datetime

class FileDetailResponse(FileUpload):
    pass