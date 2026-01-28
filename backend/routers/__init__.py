from .auth import router as auth_router
from .jira import router as jira_router
from .dashboard import router as dashboard_router
from .tasks import router as tasks_router
from .users import router as users_router
from .files import router as files_router
from .projects import router as projects_router
from .reports import router as reports_router

__all__ = ["auth_router", "jira_router", "dashboard_router", "tasks_router", "users_router", "files_router", "projects_router", "reports_router"]