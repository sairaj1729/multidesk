import logging
import os
from typing import List, Optional
from datetime import datetime
from db import get_database
from models.jira import FileUpload
from models.files import FileFilter
from bson import ObjectId


logger = logging.getLogger(__name__)
logger.info("upload_file() called")


# Define upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FilesService:
    async def upload_file(self, user_id: str, filename: str, content: bytes, content_type: str, uploader: str) -> Optional[FileUpload]:
        """Upload a file and store its metadata"""
        try:
            db = get_database()
            files_collection = db.files
            
            # Save file to disk
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Create file document
            file_doc = {
                "user_id": user_id,
                "filename": filename,
                "size": len(content),
                "content_type": content_type,
                "status": "processing",
                "records": 0,
                "uploader": uploader,
                "uploaded_at": datetime.utcnow(),
                "processed_at": None,
                "error_message": None
            }
            
            # Insert file document
            result = await files_collection.insert_one(file_doc)
            
            if result.inserted_id:
                file_doc["_id"] = result.inserted_id
                return FileUpload(
                    id=str(result.inserted_id),
                    user_id=file_doc["user_id"],
                    filename=file_doc["filename"],
                    size=file_doc["size"],
                    content_type=file_doc["content_type"],
                    status=file_doc["status"],
                    records=file_doc["records"],
                    uploader=file_doc["uploader"],
                    uploaded_at=file_doc["uploaded_at"],
                    processed_at=file_doc["processed_at"],
                    error_message=file_doc["error_message"]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to upload file {filename} for user {user_id}: {e}")
            return None

    async def get_files(self, user_id: str, filter_params: FileFilter, page: int = 1, size: int = 50) -> dict:
        """Get files for a user with filtering and pagination"""
        try:
            db = get_database()
            files_collection = db.files
            
            # Build query based on filters
            query = {"user_id": user_id}
            
            if filter_params.search:
                query["filename"] = {"$regex": filter_params.search, "$options": "i"}
            
            if filter_params.status:
                query["status"] = filter_params.status
            
            if filter_params.file_type:
                query["content_type"] = filter_params.file_type
            
            # Calculate pagination
            skip = (page - 1) * size
            
            # Get total count
            total = await files_collection.count_documents(query)
            
            # Get files with pagination
            cursor = files_collection.find(query).skip(skip).limit(size).sort("uploaded_at", -1)
            files = []
            async for doc in cursor:
                file = FileUpload(
                    id=str(doc["_id"]),
                    user_id=doc["user_id"],
                    filename=doc["filename"],
                    size=doc["size"],
                    content_type=doc["content_type"],
                    status=doc["status"],
                    records=doc["records"],
                    uploader=doc["uploader"],
                    uploaded_at=doc["uploaded_at"],
                    processed_at=doc["processed_at"],
                    error_message=doc["error_message"]
                )
                files.append(file)
            
            return {
                "files": files,
                "total": total,
                "page": page,
                "size": size
            }
            
        except Exception as e:
            logger.error(f"Failed to get files for user {user_id}: {e}")
            return {
                "files": [],
                "total": 0,
                "page": page,
                "size": size
            }

    async def get_file_by_id(self, user_id: str, file_id: str) -> Optional[FileUpload]:
        """Get a specific file by ID"""
        try:
            db = get_database()
            files_collection = db.files
            
            # Find file that belongs to the user
            # _id in MongoDB is an ObjectId; convert incoming string to ObjectId
            try:
                oid = ObjectId(file_id)
            except Exception:
                return None

            doc = await files_collection.find_one({"_id": oid, "user_id": user_id})
            if doc:
                return FileUpload(
                    id=str(doc["_id"]),
                    user_id=doc["user_id"],
                    filename=doc["filename"],
                    size=doc["size"],
                    content_type=doc["content_type"],
                    status=doc["status"],
                    records=doc["records"],
                    uploader=doc["uploader"],
                    uploaded_at=doc["uploaded_at"],
                    processed_at=doc["processed_at"],
                    error_message=doc["error_message"]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get file {file_id} for user {user_id}: {e}")
            return None

    async def delete_file(self, user_id: str, file_id: str) -> bool:
        """Delete a file"""
        try:
            db = get_database()
            files_collection = db.files
            leaves_collection = db.leaves
            
            # Import risk service here to avoid circular import
            from services.risk_service import run_risk_analysis
            
            # Find file that belongs to the user
            try:
                oid = ObjectId(file_id)
            except Exception:
                return False

            doc = await files_collection.find_one({"_id": oid, "user_id": user_id})
            if not doc:
                return False
            
            # Delete associated leave records
            delete_result = await leaves_collection.delete_many({"file_id": file_id})
            logger.info(f"🗑️ Deleted {delete_result.deleted_count} leave records associated with file {file_id}")
            
            # Delete file from disk
            file_path = os.path.join(UPLOAD_DIR, doc["filename"])
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete file document
            result = await files_collection.delete_one({"_id": oid, "user_id": user_id})
            
            # Trigger risk analysis after deleting leaves
            logger.info("Triggering risk analysis after deleting leave records...")
            try:
                risks_created = await run_risk_analysis()
                logger.info(f"Risk analysis completed after deletion: {len(risks_created)} risks created")
            except Exception as risk_error:
                logger.error(f"Risk analysis failed after deletion: {risk_error}")
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_id} for user {user_id}: {e}")
            return False

    async def download_file(self, user_id: str, file_id: str) -> Optional[bytes]:
        """Download a file"""
        try:
            # Get file metadata
            file = await self.get_file_by_id(user_id, file_id)
            if not file:
                return None
            
            # Read file from disk
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    return f.read()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to download file {file_id} for user {user_id}: {e}")
            return None

# Create global files service instance
files_service = FilesService()