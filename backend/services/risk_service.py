from datetime import datetime
from db import get_database
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# Risk calculation helpers
# -----------------------------

def calculate_risk_level(score: int) -> str:
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    return "LOW"


async def run_risk_analysis(user_id: str = None):
    """
    Advanced risk analysis based on:
    - Leave overlap (when leave data exists)
    - Due date proximity
    - Story points
    - Priority
    - Status
    - Start date delay
    - Unassigned tasks
    """

    db = get_database()
    tasks = db.jira_tasks
    leaves = db.leaves
    risks = db.risk_alerts

    today = datetime.utcnow().date()
    created = []

    # Track newly created risks in this run to avoid duplicates within the same execution
    created_risk_keys = set()
    
    # If user_id is provided, only process that user's data
    user_filter = {"user_id": user_id} if user_id else {}

    # Get all employee IDs from current leave records for this user
    leave_filter = user_filter.copy() if user_filter else {}
    leave_employees_cursor = leaves.find(leave_filter, {"employee_account_id": 1})
    leave_employee_ids = set()
    async for leave_record in leave_employees_cursor:
        if leave_record.get('employee_account_id'):
            leave_employee_ids.add(leave_record['employee_account_id'])
    
    logger.info(f"📋 Found {len(leave_employee_ids)} unique employees with leave data: {list(leave_employee_ids)[:10]}...")

    # Process ALL tasks for the user (not just those assigned to employees with leave data)
    # This allows us to calculate risks based on due dates, priority, status, etc. without leave data
    task_filter = user_filter.copy()  # Process all tasks for this user
    task_count = await tasks.count_documents(task_filter)
    leave_count = len(leave_employee_ids)
    logger.info(f"📊 Processing {task_count} tasks for risk analysis (including tasks without leave data)")

    async for task in tasks.find(task_filter):
        risk_score = 0
        reasons = []

        assignee_id = task.get("assignee_account_id")
        assignee_name = task.get("assignee", "Unassigned")

        due_date = task.get("duedate")
        start_date = task.get("start_date")
        story_points = task.get("story_points")
        priority = task.get("priority")
        status = task.get("status")

        leave = None

        # -----------------------------
        # 0️⃣ UNASSIGNED TASK (REAL RISK)
        # -----------------------------
        if not assignee_id:
            risk_score += 15
            reasons.append("Task unassigned")

        # -----------------------------
        # 1️⃣ LEAVE OVERLAP (only if leave data exists for this assignee)
        # -----------------------------
        if assignee_id and due_date and assignee_id in leave_employee_ids:
            logger.debug(f"🔍 Checking leave overlap for task {task['key']} (assignee: {assignee_id}, due: {due_date})")
            
            leave = await leaves.find_one({
                "employee_account_id": assignee_id,
                "leave_start": {"$lte": due_date},
                "leave_end": {"$gte": due_date}
            })

            if leave:
                risk_score += 40
                reasons.append("Assignee on leave during due date")
                logger.info(f"⚠️ Leave overlap found: {assignee_id} on leave {leave['leave_start'].date()} to {leave['leave_end'].date()} during task due date {due_date.date()}")
            else:
                # Debug: Check if there are any leaves for this assignee at all
                assignee_leaves = await leaves.find({"employee_account_id": assignee_id}).to_list(None)
                if assignee_leaves:
                    logger.debug(f"📋 Found {len(assignee_leaves)} leaves for assignee {assignee_id}, but none overlap with due date {due_date.date()}")
                else:
                    logger.debug(f"❌ No leaves found for assignee {assignee_id}")

        # -----------------------------
        # 2️⃣ DUE DATE PROXIMITY (ALWAYS CALCULATED)
        # -----------------------------
        if due_date:
            days_left = (due_date.date() - today).days

            if days_left <= 2:
                risk_score += 25
                reasons.append("Due in ≤ 2 days")
            elif days_left <= 5:
                risk_score += 18
                reasons.append("Due in ≤ 5 days")
            elif days_left <= 10:
                risk_score += 10
                reasons.append("Due in ≤ 10 days")
            elif days_left < 0:  # Overdue
                risk_score += 30
                reasons.append("Task is overdue")

        # -----------------------------
        # 3️⃣ STORY POINT COMPLEXITY (ALWAYS CALCULATED)
        # -----------------------------
        if story_points:
            if story_points >= 13:
                risk_score += 20
                reasons.append("Very high effort task")
            elif story_points >= 8:
                risk_score += 15
                reasons.append("High effort task")
            elif story_points >= 5:
                risk_score += 10
                reasons.append("Medium effort task")

        # -----------------------------
        # 4️⃣ PRIORITY (ALWAYS CALCULATED)
        # -----------------------------
        if priority == "Highest":
            risk_score += 20
            reasons.append("Highest priority")
        elif priority == "High":
            risk_score += 15
            reasons.append("High priority")

        # -----------------------------
        # 5️⃣ STATUS RISK (ALWAYS CALCULATED)
        # -----------------------------
        if status == "Blocked":
            risk_score += 25
            reasons.append("Task is blocked")
        elif status in ["In Progress", "In Review"]:
            risk_score += 10
            reasons.append("Task in active state")
        elif status == "To Do" and due_date and (due_date.date() - today).days <= 3:
            # High risk if "To Do" task is due soon
            risk_score += 20
            reasons.append("To Do task due very soon")

        # -----------------------------
        # 6️⃣ START DATE DELAY (ALWAYS CALCULATED)
        # -----------------------------
        if start_date and due_date:
            total_days = (due_date.date() - start_date.date()).days
            days_used = (today - start_date.date()).days

            if total_days > 0 and days_used / total_days > 0.75:
                risk_score += 15
                reasons.append("Late start, most time already consumed")

        # -----------------------------
        # FINAL RISK
        # -----------------------------
        risk_level = calculate_risk_level(risk_score)

        if risk_level in ["CRITICAL", "HIGH", "MEDIUM"]:
            risk_key = f"{task['key']}_{assignee_id or 'unassigned'}"
            
            # Skip if we already created a risk for this task-assignee combination in this run
            if risk_key in created_risk_keys:
                logger.debug(f"⏭️ Skipping duplicate risk for {task['key']} (already created in this run)")
                continue
            
            # Check if a similar risk already exists in database for this user
            risk_filter = {
                "task_key": task["key"],
                "assignee_account_id": assignee_id
            }
            if user_id:
                risk_filter["user_id"] = user_id
            
            existing_risk = await risks.find_one(risk_filter)
            
            risk_doc = {
                "task_key": task["key"],
                "task_title": task.get("summary"),
                "project_key": task.get("project_key"),  # Add project key
                "project_name": task.get("project_name"),  # Add project name

                # UI fields
                "assignee": assignee_name,
                "start_date": start_date,
                "due_date": due_date,
                "leave_start": leave.get("leave_start").date().isoformat() if leave and leave.get("leave_start") else None,
                "leave_end": leave.get("leave_end").date().isoformat() if leave and leave.get("leave_end") else None,

                # Risk logic
                "assignee_account_id": assignee_id,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "reasons": reasons,
                "user_id": user_id,  # Add user ownership

                "status": "OPEN",
                "created_at": datetime.utcnow()
            }
            
            # Update existing risk if found, otherwise create new one
            if existing_risk:
                # Preserve the original creation time and any user modifications
                risk_doc["created_at"] = existing_risk.get("created_at")
                risk_doc["updated_at"] = datetime.utcnow()
                # Update the existing risk document
                await risks.update_one(
                    {"_id": existing_risk["_id"]},
                    {"$set": risk_doc}
                )
                logger.info(
                    f"⚠️ Updated {risk_level} risk for {task['key']} | score={risk_score}"
                )
            else:
                # Insert new risk document
                await risks.insert_one(risk_doc)
                created.append(risk_doc)
                created_risk_keys.add(risk_key)  # Track that we created this risk

                logger.info(
                    f"⚠️ {risk_level} | {task['key']} | score={risk_score}"
                )

    logger.info(f"🚨 Created {len(created)} risk alerts")

    return {
        "count": len(created),
        "message": "Advanced risk analysis completed"
    }
