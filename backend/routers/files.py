from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File, Response
from typing import Optional
from models.files import FileListResponse, FileFilter, FileDetailResponse
from services.files_service import files_service
from utils.dependencies import get_current_user
import logging
from services.leave_processor import process_leave_file
from fastapi import BackgroundTasks
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/files", tags=["Files"])



@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload file - NO AUTH for testing"""
    content = await file.read()
    
    # Use a default test user ID
    test_user_id = "test_user_123"
    test_user_email = "test@example.com"

    uploaded = await files_service.upload_file(
        user_id=test_user_id,
        filename=file.filename,
        content=content,
        content_type=file.content_type,
        uploader=test_user_email
    )

    if uploaded and file.filename.endswith((".xlsx", ".xls", ".csv")):
        # Get absolute path to uploads directory
        uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
        file_path = os.path.join(uploads_dir, file.filename)
        
        logger.info(f"📂 Triggering background task for file: {file_path}")

        # Run leave processing in background
        background_tasks.add_task(
            process_leave_file,
            uploaded.id,
            file_path
        )

    return uploaded

@router.get("/", response_model=FileListResponse)
async def get_files(
    search: Optional[str] = Query(None, description="Search in filename"),
    status: Optional[str] = Query(None, description="Filter by status"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size")
):
    """Get files - NO AUTH for testing"""
    test_user_id = "test_user_123"
    
    try:
        filter_params = FileFilter(
            search=search,
            status=status,
            file_type=file_type
        )
        
        result = await files_service.get_files(test_user_id, filter_params, page, size)
        return FileListResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to get files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get files"
        )

@router.get("/{file_id}", response_model=FileDetailResponse)
async def get_file(file_id: str):
    """Get a specific file by ID - NO AUTH for testing"""
    test_user_id = "test_user_123"
    
    try:
        file = await files_service.get_file_by_id(test_user_id, file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        return file
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file {file_id} for user {test_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get file"
        )

@router.delete("/{file_id}", response_model=dict)
async def delete_file(file_id: str):
    """Delete a file - NO AUTH for testing"""
    test_user_id = "test_user_123"
    
    try:
        success = await files_service.delete_file(test_user_id, file_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or deletion failed"
            )
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file {file_id} for user {test_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

@router.get("/{file_id}/download")
async def download_file(file_id: str):
    """Download a file - NO AUTH for testing"""
    test_user_id = "test_user_123"
    
    try:
        # Get file content
        content = await files_service.download_file(test_user_id, file_id)
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Get file metadata for filename
        file = await files_service.get_file_by_id(test_user_id, file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Return file content
        return Response(
            content=content,
            media_type=file.content_type,
            headers={"Content-Disposition": f"attachment; filename={file.filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download file {file_id} for user {test_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download file"
        )