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


async def run_risk_analysis():
    """
    Advanced risk analysis based on:
    - Leave overlap
    - Due date proximity
    - Story points
    - Priority
    - Status
    - Start date delay
    """

    db = get_database()
    tasks = db.jira_tasks
    leaves = db.leaves
    risks = db.risk_alerts

    # Reset risks
    await risks.delete_many({})
    logger.info("🗑️ Cleared existing risk alerts")

    today = datetime.utcnow().date()
    created = []

    async for task in tasks.find():
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
        # 1️⃣ LEAVE OVERLAP
        # -----------------------------
        if assignee_id and due_date:
            leave = await leaves.find_one({
                "employee_account_id": assignee_id,
                "leave_start": {"$lte": due_date},
                "leave_end": {"$gte": due_date}
            })

            if leave:
                risk_score += 40
                reasons.append("Assignee on leave during due date")

        # -----------------------------
        # 2️⃣ DUE DATE PROXIMITY
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

        # -----------------------------
        # 3️⃣ STORY POINT COMPLEXITY
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
        # 4️⃣ PRIORITY
        # -----------------------------
        if priority == "Highest":
            risk_score += 20
            reasons.append("Highest priority")
        elif priority == "High":
            risk_score += 15
            reasons.append("High priority")

        # -----------------------------
        # 5️⃣ STATUS RISK
        # -----------------------------
        if status == "Blocked":
            risk_score += 25
            reasons.append("Task is blocked")
        elif status in ["In Progress", "In Review"]:
            risk_score += 10
            reasons.append("Task in active state")

        # -----------------------------
        # 6️⃣ START DATE DELAY
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

        if risk_level in ["CRITICAL", "HIGH"]:
            risk_doc = {
                "task_key": task["key"],
                "task_title": task.get("summary"),

                # UI fields
                "assignee": assignee_name,
                "start_date": start_date,
                "due_date": due_date,
                "leave_start": leave.get("leave_start") if leave else None,
                "leave_end": leave.get("leave_end") if leave else None,

                # Risk logic
                "assignee_account_id": assignee_id,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "reasons": reasons,

                "status": "OPEN",
                "created_at": datetime.utcnow()
            }

            await risks.insert_one(risk_doc)
            created.append(risk_doc)

            logger.info(
                f"⚠️ {risk_level} | {task['key']} | score={risk_score}"
            )

    logger.info(f"🚨 Created {len(created)} risk alerts")

    return {
        "count": len(created),
        "message": "Advanced risk analysis completed"
    }
