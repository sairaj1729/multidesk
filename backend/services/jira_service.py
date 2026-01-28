import httpx
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from cryptography.fernet import Fernet
from db import get_database
from models.jira import JiraCredentialsCreate, JiraCredentialsInDB, JiraTask, JiraProject, JiraUser
from config import settings
import base64

logger = logging.getLogger(__name__)

# Define core fields that Jira must return
CORE_FIELDS = [
    "summary",
    "status",
    "issuetype",
    "priority",
    "duedate",
    "assignee",
    "created",
    "updated",
    "project",
    "customfield_10015",   # ✅ Start Date
    "customfield_10016",  # ✅ Story Points
    "customfield_10020" # sprint
]

class JiraService:
    def __init__(self):
        self.cipher_suite = Fernet(settings.FERNET_KEY.encode())


    def encrypt_token(self, token: str) -> str:
        """Encrypt API token before storing in database"""
        encrypted_token = self.cipher_suite.encrypt(token.encode())
        return base64.b64encode(encrypted_token).decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt API token for use with Jira API"""
        try:
            decoded_token = base64.b64decode(encrypted_token.encode())
            decrypted_token = self.cipher_suite.decrypt(decoded_token)
            return decrypted_token.decode()
        except Exception:
            logger.exception("Failed to decrypt Jira API token")
            raise
        


    async def store_jira_credentials(self, user_id: str, credentials: JiraCredentialsCreate) -> Optional[JiraCredentialsInDB]:
        """Store Jira credentials for a user"""
        try:
            db = get_database()
            credentials_collection = db.jira_credentials
            
            # Encrypt the API token
            encrypted_token = self.encrypt_token(credentials.api_token)
            
            # Create credentials document
            credentials_doc = {
                "user_id": user_id,
                "domain": credentials.domain,
                "email": credentials.email,
                "api_token": encrypted_token,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            }
            
            # Insert or update credentials
            result = await credentials_collection.update_one(
                {"user_id": user_id},
                {"$set": credentials_doc},
                upsert=True
            )
            
            # Retrieve the stored credentials
            stored_doc = await credentials_collection.find_one({"user_id": user_id})
            if stored_doc:
                return JiraCredentialsInDB(
                    id=str(stored_doc["_id"]),
                    user_id=stored_doc["user_id"],
                    domain=stored_doc["domain"],
                    email=stored_doc["email"],
                    api_token=stored_doc["api_token"],
                    created_at=stored_doc["created_at"],
                    updated_at=stored_doc["updated_at"],
                    is_active=stored_doc["is_active"]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to store Jira credentials for user {user_id}: {e}")
            return None


    def normalize_domain(self, domain: str) -> str:
        if not domain.startswith("http"):
            domain = f"https://{domain}"
        return domain.rstrip("/")


    async def get_jira_credentials(self, user_id: str) -> Optional[JiraCredentialsInDB]:
        """Get Jira credentials for a user"""
        try:
            db = get_database()
            credentials_collection = db.jira_credentials
            
            credentials_doc = await credentials_collection.find_one({"user_id": user_id})
            if credentials_doc:
                return JiraCredentialsInDB(
                    id=str(credentials_doc["_id"]),
                    user_id=credentials_doc["user_id"],
                    domain=credentials_doc["domain"],
                    email=credentials_doc["email"],
                    api_token=credentials_doc["api_token"],
                    created_at=credentials_doc["created_at"],
                    updated_at=credentials_doc["updated_at"],
                    is_active=credentials_doc["is_active"]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get Jira credentials for user {user_id}: {e}")
            return None

    async def validate_jira_connection(self, credentials: JiraCredentialsInDB) -> bool:
        """Validate Jira connection with provided credentials"""
        try:
            # Decrypt the API token
            decrypted_token = self.decrypt_token(credentials.api_token)
            
            # Construct Jira API URL for validation - use a basic endpoint
            jira_url = f"{self.normalize_domain(credentials.domain)}/rest/api/3/myself"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    jira_url,
                    auth=(credentials.email, decrypted_token),
                    headers={"Accept": "application/json"},
                    timeout=10
                )

            if response.status_code == 200:
                return True
            
        except Exception as e:
            logger.error(f"Jira connection validation failed: {e}")
            return False

    async def fetch_issues_by_jql_new_endpoint(self, credentials: JiraCredentialsInDB, jql: str, max_results: int = 100) -> List[Dict]:
        """Fetch issues from Jira API using the new JQL Search endpoint (/rest/api/3/search/jql)"""
        try:
            # Decrypt the API token
            decrypted_token = self.decrypt_token(credentials.api_token)
            
            # Construct Jira API URL for the new JQL search endpoint
            jira_url = f"{self.normalize_domain(credentials.domain)}/rest/api/3/search/jql"
            
            # Prepare request body
            body = {
                "jql": jql,
                "maxResults": max_results,
                "fields": CORE_FIELDS
            }
            
            # Headers for the request
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            # Make API call using POST method
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    jira_url,
                    json=body,
                    headers=headers,
                    auth=(credentials.email, decrypted_token),
                    timeout=30
                )
            
            # Log response for debugging
            logger.info(f"Jira API call to {jira_url} with JQL: {jql}")
            logger.info(f"Jira response status: {response.status_code}")
            
            if response.status_code == 401:
                logger.error("Jira API authentication failed - invalid credentials")
                return []
            elif response.status_code == 400:
                logger.error(f"Jira API bad request: {response.text}")
                # Try with a simpler JQL as fallback
                fallback_jqls = [
                    "assignee = currentUser() ORDER BY updated DESC",
                    "project in projectsWhereUserHasPermission() ORDER BY updated DESC",
                    "assignee = currentUser() OR reporter = currentUser() ORDER BY updated DESC"
                ]
                for fallback_jql in fallback_jqls:
                    if jql != fallback_jql:
                        logger.info(f"Trying fallback JQL: {fallback_jql}")
                        result = await self.fetch_issues_by_jql_new_endpoint(credentials, fallback_jql, max_results)
                        if result:  # If we got results, return them
                            return result
                return []
            elif response.status_code != 200:
                logger.error(f"Jira API call failed with status {response.status_code}: {response.text}")
                # Try with a simpler JQL as fallback
                fallback_jqls = [
                    "assignee = currentUser() ORDER BY updated DESC",
                    "project in projectsWhereUserHasPermission() ORDER BY updated DESC",
                    "assignee = currentUser() OR reporter = currentUser() ORDER BY updated DESC"
                ]
                for fallback_jql in fallback_jqls:
                    if jql != fallback_jql:
                        logger.info(f"Trying fallback JQL: {fallback_jql}")
                        result = await self.fetch_issues_by_jql_new_endpoint(credentials, fallback_jql, max_results)
                        if result:  # If we got results, return them
                            return result
                return []
            
            # Parse response
            try:
                data = response.json()
                issues = data.get("issues", [])
                logger.info(f"Successfully fetched {len(issues)} issues from Jira")
                return issues
            except Exception as parse_error:
                logger.error(f"Failed to parse Jira response: {parse_error}")
                return []
            
        except httpx.TimeoutException:
            logger.error("Jira API call timed out")
            return []
        except httpx.RequestError as request_error:
            logger.error(f"Jira API request failed: {request_error}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch Jira issues: {e}")
            return []

    async def fetch_issues_by_jql_old_endpoint(self, credentials: JiraCredentialsInDB, jql: str, max_results: int = 100) -> List[Dict]:
        """Fetch issues from Jira API using the old JQL Search endpoint (as fallback)"""
        try:
            # Decrypt the API token
            decrypted_token = self.decrypt_token(credentials.api_token)
            
            # Construct Jira API URL for the old JQL search endpoint
            jira_url = f"{self.normalize_domain(credentials.domain)}/rest/api/3/search"
            
            # Prepare request body
            body = {
                "jql": jql,
                "maxResults": max_results,
                "fields": CORE_FIELDS
            }
            
            # Headers for the request
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            # Make API call using POST method
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    jira_url,
                    json=body,
                    headers=headers,
                    auth=(credentials.email, decrypted_token),
                    timeout=30
                )
            
            # Log response for debugging
            logger.info(f"Jira API call to {jira_url} with JQL: {jql}")
            logger.info(f"Jira response status: {response.status_code}")
            
            if response.status_code == 401:
                logger.error("Jira API authentication failed - invalid credentials")
                return []
            elif response.status_code == 400:
                logger.error(f"Jira API bad request: {response.text}")
                # Try with a simpler JQL as fallback
                fallback_jqls = [
                    "assignee = currentUser() ORDER BY updated DESC",
                    "project in projectsWhereUserHasPermission() ORDER BY updated DESC",
                    "assignee = currentUser() OR reporter = currentUser() ORDER BY updated DESC"
                ]
                for fallback_jql in fallback_jqls:
                    if jql != fallback_jql:
                        logger.info(f"Trying fallback JQL: {fallback_jql}")
                        result = await self.fetch_issues_by_jql_old_endpoint(credentials, fallback_jql, max_results)
                        if result:  # If we got results, return them
                            return result
                return []
            elif response.status_code != 200:
                logger.error(f"Jira API call failed with status {response.status_code}: {response.text}")
                # Try with a simpler JQL as fallback
                fallback_jqls = [
                    "assignee = currentUser() ORDER BY updated DESC",
                    "project in projectsWhereUserHasPermission() ORDER BY updated DESC",
                    "assignee = currentUser() OR reporter = currentUser() ORDER BY updated DESC"
                ]
                for fallback_jql in fallback_jqls:
                    if jql != fallback_jql:
                        logger.info(f"Trying fallback JQL: {fallback_jql}")
                        result = await self.fetch_issues_by_jql_old_endpoint(credentials, fallback_jql, max_results)
                        if result:  # If we got results, return them
                            return result
                return []
            
            # Parse response
            try:
                data = response.json()
                issues = data.get("issues", [])
                logger.info(f"Successfully fetched {len(issues)} issues from Jira")
                return issues
            except Exception as parse_error:
                logger.error(f"Failed to parse Jira response: {parse_error}")
                return []
            
        except httpx.TimeoutException:
            logger.error("Jira API call timed out")
            return []
        except httpx.RequestError as request_error:
            logger.error(f"Jira API request failed: {request_error}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch Jira issues: {e}")
            return []

    async def fetch_issues_by_jql(self, credentials: JiraCredentialsInDB, jql: str, max_results: int = 100) -> List[Dict]:
        """Fetch issues from Jira API using the new JQL Search endpoint"""
        try:
            # Decrypt the API token
            decrypted_token = self.decrypt_token(credentials.api_token)
            
            # Construct Jira API URL for the new JQL search endpoint
            # Using the new endpoint as primary
            jira_url = f"{self.normalize_domain(credentials.domain)}/rest/api/3/search/jql"
            
            # Prepare request body
            body = {
                "jql": jql,
                "maxResults": max_results,
                "fields": CORE_FIELDS
            }
            
            # Headers for the request
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            # Make API call using POST method
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    jira_url,
                    json=body,
                    headers=headers,
                    auth=(credentials.email, decrypted_token),
                    timeout=30
                )
            
            # Log response for debugging
            logger.info(f"Jira API call to {jira_url} with JQL: {jql}")
            logger.info(f"Jira response status: {response.status_code}")
            
            if response.status_code == 401:
                logger.error("Jira API authentication failed - invalid credentials")
                return []
            elif response.status_code == 400:
                logger.error(f"Jira API bad request: {response.text}")
                # Try with a simpler JQL as fallback using the new endpoint
                fallback_jqls = [
                    "assignee = currentUser() ORDER BY updated DESC",
                    "project in projectsWhereUserHasPermission() ORDER BY updated DESC",
                    "assignee = currentUser() OR reporter = currentUser() ORDER BY updated DESC"
                ]
                for fallback_jql in fallback_jqls:
                    if jql != fallback_jql:
                        logger.info(f"Trying fallback JQL: {fallback_jql}")
                        result = await self.fetch_issues_by_jql(credentials, fallback_jql, max_results)
                        if result:  # If we got results, return them
                            return result
                return []
            elif response.status_code == 410:
                logger.error(f"Jira API endpoint deprecated: {response.text}")
                # The endpoint has been removed, try the old endpoint as fallback
                return await self.fetch_issues_by_jql_old_endpoint(credentials, jql, max_results)
            elif response.status_code != 200:
                logger.error(f"Jira API call failed with status {response.status_code}: {response.text}")
                # Try with a simpler JQL as fallback using the new endpoint
                fallback_jqls = [
                    "assignee = currentUser() ORDER BY updated DESC",
                    "project in projectsWhereUserHasPermission() ORDER BY updated DESC",
                    "assignee = currentUser() OR reporter = currentUser() ORDER BY updated DESC"
                ]
                for fallback_jql in fallback_jqls:
                    if jql != fallback_jql:
                        logger.info(f"Trying fallback JQL: {fallback_jql}")
                        result = await self.fetch_issues_by_jql(credentials, fallback_jql, max_results)
                        if result:  # If we got results, return them
                            return result
                return []
            
            # Parse response
            try:
                data = response.json()
                issues = data.get("issues", [])
                logger.info(f"Successfully fetched {len(issues)} issues from Jira")
                return issues
            except Exception as parse_error:
                logger.error(f"Failed to parse Jira response: {parse_error}")
                return []
            
        except httpx.TimeoutException:
            logger.error("Jira API call timed out")
            return []
        except httpx.RequestError as request_error:
            logger.error(f"Jira API request failed: {request_error}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch Jira issues: {e}")
            return []

    async def fetch_jira_tasks(self, credentials: JiraCredentialsInDB, user_id: str) -> List[JiraTask]:
        """Fetch tasks from Jira API using the new JQL Search endpoint"""
        try:
            # Try different JQL queries to get issues - prioritizing your project where you have admin access
            jql_queries = [
                "project = SCRUM ORDER BY updated DESC",  # Your specific project - you have admin access to all tasks
                "project in projectsWhereUserHasPermission() ORDER BY updated DESC",  # Issues in projects user has access to
                "assignee = currentUser() OR reporter = currentUser() ORDER BY updated DESC",  # Issues assigned to or reported by user
                "ORDER BY updated DESC"  # All issues user can access (with fallback for bounded queries)
            ]
            
            issues = []
            for jql in jql_queries:
                try:
                    logger.info(f"Trying JQL query: {jql}")
                    # Fetch issues using the new endpoint
                    issues = await self.fetch_issues_by_jql_new_endpoint(credentials, jql, max_results=100)
                    if issues:  # If we got issues, break and use this query
                        logger.info(f"Successfully fetched {len(issues)} issues with JQL: {jql}")
                        break
                    else:
                        logger.info(f"No issues returned with JQL: {jql}")
                except Exception as jql_error:
                    logger.warning(f"JQL query failed '{jql}': {jql_error}")
                    continue  # Try next query
            
            if not issues:
                logger.warning("No issues found with any JQL query")
                return []
            
            tasks = []
            
            # Process each issue
            for issue in issues:
                fields = issue.get("fields", {})
                project = fields.get("project", {})
                status = fields.get("status", {})
                priority = fields.get("priority", {})
                assignee = fields.get("assignee")
                issuetype = fields.get("issuetype", {})
                story_points = fields.get("customfield_10016")
                logger.info(f"Task {issue.get('key')} story_points raw = {story_points}"
)


                
                # Extract assignee email
                assignee_account_id = assignee.get("accountId") if assignee else None
                assignee_email = assignee.get("emailAddress", "") if assignee else ""
                assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"
                
                sprint_raw = fields.get("customfield_10020")
                start_date_raw = fields.get("customfield_10015")

                if start_date_raw:
                    start_date = parse_jira_date(start_date_raw)
                else:
                    # Fallback: infer start date from created date
                    start_date = parse_jira_datetime(fields.get("created"))

                
                # Parse sprint (array → last sprint)
                sprint_name = None
                if sprint_raw and isinstance(sprint_raw, list):
                    sprint_name = sprint_raw[-1].get("name")

                task = JiraTask(
                    id="",  # Will be set when storing in database
                    user_id=user_id,
                    jira_id=issue.get("id", ""),
                    key=issue.get("key", ""),
                    summary=fields.get("summary", ""),
                    status=status.get("name", ""),
                    priority=priority.get("name", "") if priority else "Unknown",
                    assignee=assignee_name,
                    assignee_email=assignee_email,
                    assignee_account_id=assignee_account_id,
                    story_points=story_points, 
                    start_date=start_date,
                    sprint=sprint_name,                   
                    created=parse_jira_datetime(fields.get("created")) if fields.get("created") else datetime.utcnow(),
                    updated=parse_jira_datetime(fields.get("updated")) if fields.get("updated") else datetime.utcnow(),
                    duedate=parse_jira_date(fields.get("duedate")) if fields.get("duedate") else None,
                    project_key=project.get("key", ""),
                    project_name=project.get("name", ""),
                    issue_type=issuetype.get("name", "") if issuetype else "Task"
                )
                tasks.append(task)
                # logger.info("FIRST TASK RAW:", response.data.tasks[0]);

            
            logger.info(f"Successfully processed {len(tasks)} tasks from {len(issues)} issues")
            return tasks
            
            
        except Exception as e:
            logger.error(f"Failed to fetch Jira tasks: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def fetch_jira_projects(self, credentials: JiraCredentialsInDB, user_id: str) -> List[JiraProject]:
        """Fetch projects from Jira API"""
        try:
            # Decrypt the API token
            decrypted_token = self.decrypt_token(credentials.api_token)
            
            # Construct Jira API URL
            jira_url = f"{self.normalize_domain(credentials.domain)}/rest/api/3/project"
            
            # Make API call
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    jira_url,
                    auth=(credentials.email, decrypted_token),
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                projects = []
                
                # Process each project
                for project_data in data:
                    project = JiraProject(
                        id="",  # Will be set when storing in database
                        user_id=user_id,
                        jira_id=project_data.get("id", ""),
                        key=project_data.get("key", ""),
                        name=project_data.get("name", ""),
                        description=project_data.get("description", ""),
                        lead=project_data.get("lead", {}).get("displayName", "Unknown"),
                        created=datetime.utcnow(),  # Jira API doesn't always return created date for projects
                        updated=datetime.utcnow()
                    )
                    projects.append(project)
                
                return projects
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to fetch Jira projects: {e}")
            return []

    async def store_jira_projects(self, user_id: str, projects: List[JiraProject]) -> bool:
        """Store Jira projects in database"""
        try:
            db = get_database()
            projects_collection = db.jira_projects
            
            # Clear existing projects for this user
            await projects_collection.delete_many({"user_id": user_id})
            
            # Insert new projects
            if projects:
                project_docs = []
                for project in projects:
                    project_doc = {
                        "user_id": project.user_id,
                        "jira_id": project.jira_id,
                        "key": project.key,
                        "name": project.name,
                        "description": project.description,
                        "lead": project.lead,
                        "created": project.created,
                        "updated": project.updated
                    }
                    project_docs.append(project_doc)
                
                await projects_collection.insert_many(project_docs)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store Jira projects for user {user_id}: {e}")
            return False

    async def get_user_projects(self, user_id: str) -> List[JiraProject]:
        """Get Jira projects for a user from database"""
        try:
            db = get_database()
            projects_collection = db.jira_projects
            
            # Find projects for this user
            cursor = projects_collection.find({"user_id": user_id})
            projects = []
            
            async for project_doc in cursor:
                project = JiraProject(
                    id=str(project_doc["_id"]),
                    user_id=project_doc["user_id"],
                    jira_id=project_doc["jira_id"],
                    key=project_doc["key"],
                    name=project_doc["name"],
                    description=project_doc["description"],
                    lead=project_doc["lead"],
                    created=project_doc["created"],
                    updated=project_doc["updated"]
                )
                projects.append(project)
            
            return projects
            
        except Exception as e:
            logger.error(f"Failed to get Jira projects for user {user_id}: {e}")
            return []

    async def store_jira_tasks(self, user_id: str, tasks: List[JiraTask]) -> bool:
        """Store Jira tasks in database"""
        try:
            db = get_database()
            tasks_collection = db.jira_tasks
            
            # Clear existing tasks for this user
            await tasks_collection.delete_many({"user_id": user_id})
            
            # Insert new tasks
            if tasks:
                task_docs = []
                for task in tasks:
                    task_doc = {
                        "user_id": task.user_id,
                        "jira_id": task.jira_id,
                        "key": task.key,
                        "summary": task.summary,
                        "status": task.status,
                        "priority": task.priority,
                        "assignee": task.assignee,
                        "assignee_email": task.assignee_email,
                        "assignee_account_id": task.assignee_account_id,
                        "story_points": task.story_points,
                        "start_date": task.start_date,
                        "sprint": task.sprint,
                        "created": task.created,
                        "updated": task.updated,
                        "duedate": task.duedate,
                        "project_key": task.project_key,
                        "project_name": task.project_name,
                        "issue_type": task.issue_type
                    }
                    task_docs.append(task_doc)
                
                await tasks_collection.insert_many(task_docs)
                logger.info(f"Storing task {task.key}")


            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store Jira tasks for user {user_id}: {e}")
            return False
    

    async def sync_jira_data(self, user_id: str) -> bool:
        """Sync Jira data (tasks and projects) for a user"""
        try:
            # Get user's Jira credentials
            credentials = await self.get_jira_credentials(user_id)
            if not credentials:
                logger.warning(f"No Jira credentials found for user {user_id}")
                return False
            
            # Validate connection
            is_valid = await self.validate_jira_connection(credentials)
            if not is_valid:
                logger.warning(f"Invalid Jira connection for user {user_id}")
                return False
            
            # Fetch and store projects
            projects = await self.fetch_jira_projects(credentials, user_id)
            if projects:
                await self.store_jira_projects(user_id, projects)
                logger.info(f"Synced {len(projects)} projects for user {user_id}")
            
            # Fetch and store tasks
            tasks = await self.fetch_jira_tasks(credentials, user_id)
            logger.info(f"Fetched {len(tasks)} tasks from Jira")

            if tasks:
                result = await self.store_jira_tasks(user_id, tasks)
                logger.info(f"store_jira_tasks result = {result}")
            else:
                logger.warning("No tasks returned from fetch_jira_tasks")

            
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync Jira data for user {user_id}")
            return False

    # New methods for specific issue types (matching the updated API)
    async def fetch_epics(self, credentials: JiraCredentialsInDB, project_key: str) -> List[Dict]:
        """Fetch epics for a specific project"""
        jql = f"project={project_key} AND issuetype=Epic"
        return await self.fetch_issues_by_jql_new_endpoint(credentials, jql)

    async def fetch_stories(self, credentials: JiraCredentialsInDB, project_key: str) -> List[Dict]:
        """Fetch stories for a specific project"""
        jql = f"project={project_key} AND issuetype=Story"
        return await self.fetch_issues_by_jql_new_endpoint(credentials, jql)

    async def fetch_tasks(self, credentials: JiraCredentialsInDB, project_key: str) -> List[Dict]:
        """Fetch tasks for a specific project"""
        jql = f"project={project_key} AND issuetype=Task"
        return await self.fetch_issues_by_jql_new_endpoint(credentials, jql)

    async def fetch_bugs(self, credentials: JiraCredentialsInDB, project_key: str) -> List[Dict]:
        """Fetch bugs for a specific project"""
        jql = f"project={project_key} AND issuetype=Bug"
        return await self.fetch_issues_by_jql_new_endpoint(credentials, jql)

# Helper functions for date parsing

def parse_jira_datetime(date_str):
    """Parse JIRA datetime string in various formats"""
    if not date_str:
        return None
    
    # Common JIRA datetime formats
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",  # 2023-01-01T10:00:00.000+0000
        "%Y-%m-%dT%H:%M:%S%z",      # 2023-01-01T10:00:00+0000
        "%Y-%m-%dT%H:%M:%S.%fZ",    # 2023-01-01T10:00:00.000Z
        "%Y-%m-%dT%H:%M:%SZ",       # 2023-01-01T10:00:00Z
        "%Y-%m-%dT%H:%M:%S",        # 2023-01-01T10:00:00
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # If all formats fail, log and return current time
    logger.warning(f"Unable to parse datetime: {date_str}")
    return datetime.utcnow()


def parse_jira_date(date_str):
    """Parse JIRA date string in various formats and return datetime object for MongoDB compatibility"""
    if not date_str:
        return None
    
    # Common JIRA date formats
    formats = [
        "%Y-%m-%d",  # 2023-01-01
    ]
    
    for fmt in formats:
        try:
            # Parse as date and convert to datetime at start of day
            parsed_date = datetime.strptime(date_str, fmt).date()
            # Convert date to datetime at start of day (00:00:00) for MongoDB
            return datetime.combine(parsed_date, datetime.min.time())
        except ValueError:
            continue
    
    # If all formats fail, log and return current date as datetime
    logger.warning(f"Unable to parse date: {date_str}")
    return datetime.combine(datetime.utcnow().date(), datetime.min.time())

# Create singleton instance
jira_service = JiraService()