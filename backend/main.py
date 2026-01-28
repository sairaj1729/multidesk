from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import os
from datetime import datetime

# Routers
from routers.auth import router as auth_router
from routers.jira import router as jira_router
from routers.dashboard import router as dashboard_router
from routers.tasks import router as tasks_router
from routers.users import router as users_router
from routers.files import router as files_router
from routers.projects import router as projects_router
from routers.reports import router as reports_router
from routers import risks

# Database
from db import connect_to_mongo, close_mongo_connection
from db.init_db import init_database
from db.mongodb import get_database

# Services
from services.jira_service import jira_service, JiraTask
from services import scheduler_service

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("multi-desk")

# =========================
# Lifespan (Startup / Shutdown)
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Multi Desk Backend...")

    # Mongo should not block health checks
    try:
        await connect_to_mongo()
        await init_database()
        logger.info("MongoDB connected")
    except Exception as e:
        logger.error(f"Mongo startup error: {e}")

    # Start scheduler in background (non-blocking)
    scheduler_task = asyncio.create_task(
        scheduler_service.start_scheduler()
    )

    yield

    logger.info("Shutting down Multi Desk Backend...")
    scheduler_service.stop_scheduler()
    await close_mongo_connection()
    scheduler_task.cancel()
    logger.info("Shutdown complete")

# =========================
# App Init
# =========================
app = FastAPI(
    title="Multi Desk API",
    version="1.0.0",
    lifespan=lifespan
)

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
        "https://multidesk-eight.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Routers
# =========================
app.include_router(auth_router)
app.include_router(jira_router)
app.include_router(dashboard_router)
app.include_router(tasks_router)
app.include_router(users_router)
app.include_router(files_router)
app.include_router(projects_router)
app.include_router(reports_router)
app.include_router(risks.router)

# =========================
# Root
# =========================
@app.get("/")
async def root():
    return {
        "message": "Multi Desk API",
        "version": "1.0.0",
        "status": "running"
    }

# =========================
# HEALTH CHECK (GET + HEAD)
# =========================
@app.api_route("/health", methods=["GET", "HEAD"], include_in_schema=False)
async def health_check():
    return Response(status_code=200)

# =========================
# Mongo Test
# =========================
@app.get("/api/mongo/connection-test")
async def test_mongo_connection():
    try:
        db = get_database()
        collections = await db.list_collection_names()
        return {
            "status": "connected",
            "collections_count": len(collections),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }

# =========================
# Jira Storage Test
# =========================
@app.get("/api/mongo/test-task-storage")
async def test_task_storage():
    try:
        test_task = JiraTask(
            id="",
            user_id="test_user_123",
            jira_id="test_1001",
            key="TEST-1",
            summary="Test task",
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

        await jira_service.store_jira_tasks("test_user_123", [test_task])

        db = get_database()
        count = await db.jira_tasks.count_documents({"user_id": "test_user_123"})
        await db.jira_tasks.delete_many({"user_id": "test_user_123"})

        return {"status": "success", "tasks_stored": count}

    except Exception as e:
        return {"status": "error", "error": str(e)}

# =========================
# Jira Fetch Test
# =========================
@app.get("/api/mongo/test-jira-fetch")
async def test_jira_fetch():
    try:
        user_id = "693e942a4a63b57055d9a211"
        credentials = await jira_service.get_jira_credentials(user_id)

        if not credentials:
            return {"status": "error", "message": "No credentials"}

        valid = await jira_service.validate_jira_connection(credentials)
        if not valid:
            return {"status": "error", "message": "Invalid JIRA connection"}

        tasks = await jira_service.fetch_jira_tasks(credentials, user_id)
        if tasks:
            await jira_service.store_jira_tasks(user_id, tasks)

        return {
            "status": "success",
            "tasks_fetched": len(tasks)
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}

# =========================
# Local Run (Render ignores this)
# =========================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
