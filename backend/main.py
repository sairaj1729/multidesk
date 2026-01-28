from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio

# Import routers
from routers.auth import router as auth_router
from routers.jira import router as jira_router
from routers.dashboard import router as dashboard_router
from routers.tasks import router as tasks_router
from routers.users import router as users_router
from routers.files import router as files_router
from routers.projects import router as projects_router
from routers.reports import router as reports_router

# Import database connection
from db import connect_to_mongo, close_mongo_connection
from db.init_db import init_database
from db.mongodb import get_database
from services.jira_service import jira_service, JiraTask
from datetime import datetime

# Import services
from services import scheduler_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Multi Desk Backend...")
    await connect_to_mongo()
    await init_database()
    logger.info("Multi Desk Backend started successfully")
    
    # Start scheduler in background
    scheduler_task = asyncio.create_task(scheduler_service.start_scheduler())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi Desk Backend...")
    scheduler_service.stop_scheduler()
    await close_mongo_connection()
    logger.info("Multi Desk Backend shut down successfully")

# Create FastAPI application
app = FastAPI(
    title="Multi Desk API",
    description="Backend API for Multi Desk Dashboard Tool",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Alternative dev server
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
        "multidesk-eight.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(jira_router)
app.include_router(dashboard_router)
app.include_router(tasks_router)
app.include_router(users_router)
app.include_router(files_router)
app.include_router(projects_router)
app.include_router(reports_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multi Desk API",
        "version": "1.0.0",
        "status": "healthy"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "multi-desk-backend"
    }


@app.get("/api/mongo/connection-test")
async def test_mongo_connection():
    """Test MongoDB connection endpoint"""
    try:
        db = get_database()
        # Try to access a collection to verify connection
        collections = await db.list_collection_names()
        return {
            "status": "connected",
            "collections_count": len(collections),
            "collections": collections,
            "message": "MongoDB connection successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to connect to MongoDB"
        }


@app.get("/api/mongo/test-task-storage")
async def test_task_storage():
    """Test endpoint to verify JIRA task storage functionality"""
    try:
        # Create a test task
        test_task = JiraTask(
            id="",
            user_id="test_user_123",
            jira_id="test_1001",
            key="TEST-1",
            summary="Test task for verification",
            status="To Do",
            priority="High",
            assignee="Test User",
            assignee_email="test@example.com",
            created=datetime.utcnow(),
            updated=datetime.utcnow(),
            duedate=datetime.utcnow(),
            project_key="TEST",
            project_name="Test Project",
            issue_type="Task"
        )
        
        # Store the task using the service method
        result = await jira_service.store_jira_tasks("test_user_123", [test_task])
        
        # Verify the task was stored by counting
        db = get_database()
        tasks_collection = db.jira_tasks
        task_count = await tasks_collection.count_documents({"user_id": "test_user_123"})
        
        # Clean up test data
        await tasks_collection.delete_many({"user_id": "test_user_123"})
        
        return {
            "status": "success",
            "storage_result": result,
            "tasks_stored": task_count,
            "message": f"Task storage test completed. {task_count} tasks were stored and cleaned up."
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to test task storage"
        }


@app.get("/api/mongo/test-jira-fetch")
async def test_jira_fetch():
    """Test endpoint to verify JIRA fetch and storage functionality"""
    from services.jira_service import jira_service
    try:
        # Get JIRA credentials for the current user
        # For this test, we'll use a sample user ID that should have credentials
        user_id = "693e942a4a63b57055d9a211"  # From the logs
        
        # Get credentials
        credentials = await jira_service.get_jira_credentials(user_id)
        if not credentials:
            return {
                "status": "error",
                "message": f"No JIRA credentials found for user {user_id}. Please connect JIRA first."
            }
        
        # Validate connection
        is_valid = await jira_service.validate_jira_connection(credentials)
        if not is_valid:
            return {
                "status": "error",
                "message": f"Invalid JIRA connection for user {user_id}. Please check credentials."
            }
        
        # Fetch tasks using the same method as sync
        tasks = await jira_service.fetch_jira_tasks(credentials, user_id)
        
        # Store tasks if any found
        storage_result = True
        if tasks:
            storage_result = await jira_service.store_jira_tasks(user_id, tasks)
        
        return {
            "status": "success",
            "credentials_found": credentials is not None,
            "connection_valid": is_valid,
            "tasks_fetched": len(tasks),
            "storage_result": storage_result,
            "message": f"JIRA fetch test completed. Fetched {len(tasks)} tasks."
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to test JIRA fetch"
        }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


from routers import risks

app.include_router(risks.router)
