"""
Authentication Worker
Handles: validate-credentials, init-student-session,
         init-instructor-session, init-admin-session
"""
import logging
import uuid
from datetime import datetime
from camunda.external_task.external_task_worker import ExternalTaskWorker
from workers.config import CAMUNDA_URL, WORKER_CONFIG, WORKER_IDS, AUTH_TOPICS
from workers.database import validate_user, get_student_profile
from workers.email_service import send_welcome_email

logger = logging.getLogger("lms.auth")


def handle_auth_task(task):
    """Route auth tasks by topic name."""
    topic = task.get_topic_name()
    logger.info("🔐 Auth task received: topic=%s | pid=%s", topic, task.get_process_instance_id())

    try:
        if topic == "validate-credentials":
            return _validate_credentials(task)
        elif topic == "init-student-session":
            return _init_student_session(task)
        elif topic == "init-instructor-session":
            return _init_instructor_session(task)
        elif topic == "init-admin-session":
            return _init_admin_session(task)
        else:
            logger.warning("Unknown auth topic: %s", topic)
            return task.complete({})
    except Exception as e:
        logger.error("Auth task failed [%s]: %s", topic, str(e), exc_info=True)
        return task.failure(
            error_message=f"Auth worker error: {str(e)}",
            error_details=str(e),
            retries=2,
            retry_timeout=3000
        )


def _validate_credentials(task):
    """
    Validate username + password against the database.
    Sets: credentialsValid (bool), userId (str), userEmail (str)
    """
    username = task.get_variable("username") or ""
    password = task.get_variable("password") or ""
    user_type = task.get_variable("userType") or "student"

    logger.info("🔍 Validating credentials for: %s (%s)", username, user_type)

    user = validate_user(username.strip(), password.strip())

    if user and user["user_type"] == user_type:
        logger.info("✅ Login valid: %s → %s", username, user["id"])
        return task.complete({
            "credentialsValid":  True,
            "userId":            user["id"],
            "userEmail":         user["email"],
            "userType":          user["user_type"],
            "emailDomain":       user.get("email_domain", ""),
            "loginTimestamp":    datetime.utcnow().isoformat(),
        })
    else:
        logger.warning("❌ Login failed for: %s", username)
        return task.complete({
            "credentialsValid": False,
            "userId":           "",
            "userEmail":        "",
            "errorMessage":     "Invalid username, password, or account type.",
        })


def _init_student_session(task):
    """
    Initialize student dashboard data after successful login.
    Sets: sessionId, dashboardData (JSON string)
    """
    user_id   = task.get_variable("userId") or ""
    username  = task.get_variable("username") or ""
    user_email = task.get_variable("userEmail") or ""

    logger.info("🎓 Initializing student session: %s", user_id)

    profile = get_student_profile(user_id)

    session_id = str(uuid.uuid4())
    dashboard_data = {
        "sessionId":       session_id,
        "role":            "STUDENT",
        "username":        username,
        "learningStyle":   profile.get("learning_style", "Visual") if profile else "Visual",
        "totalPoints":     profile.get("total_points", 0) if profile else 0,
        "weeklyStreak":    profile.get("weekly_streak", 0) if profile else 0,
        "redirectTo":      "/student/learning-hub",
        "initTime":        datetime.utcnow().isoformat(),
    }

    # Send welcome email (non-blocking — fire and forget)
    if user_email:
        send_welcome_email(user_email, username, "Student", "/student/learning-hub")

    return task.complete({
        "sessionId":     session_id,
        "dashboardData": str(dashboard_data),
        "redirectUrl":   "/student/learning-hub",
    })
    logger.info("✅ Student session created: %s → sessionId=%s", username, session_id)


def _init_instructor_session(task):
    """
    Initialize instructor dashboard data after successful login.
    """
    user_id    = task.get_variable("userId") or ""
    username   = task.get_variable("username") or ""
    user_email = task.get_variable("userEmail") or ""

    logger.info("👨‍🏫 Initializing instructor session: %s", user_id)

    session_id = str(uuid.uuid4())

    if user_email:
        send_welcome_email(user_email, username, "Instructor", "/instructor/teaching-dashboard")

    return task.complete({
        "sessionId":   session_id,
        "redirectUrl": "/instructor/teaching-dashboard",
        "permissions": "manage_content,monitor_students,grade_assignments,start_lectures",
    })
    logger.info("✅ Instructor session created: %s", username)


def _init_admin_session(task):
    """
    Initialize admin dashboard data after successful login.
    """
    user_id    = task.get_variable("userId") or ""
    username   = task.get_variable("username") or ""
    user_email = task.get_variable("userEmail") or ""

    logger.info("🛡️ Initializing admin session: %s", user_id)

    session_id = str(uuid.uuid4())

    if user_email:
        send_welcome_email(user_email, username, "Admin", "/admin/dashboard")

    return task.complete({
        "sessionId":   session_id,
        "redirectUrl": "/admin/dashboard",
        "permissions": "system_control,user_management,full_access",
    })
    logger.info("✅ Admin session created: %s", username)


def start():
    """Start the authentication worker — called by main.py."""
    logger.info("🚀 Auth worker starting | Topics: %s", AUTH_TOPICS)
    worker = ExternalTaskWorker(
        worker_id=WORKER_IDS["auth"],
        base_url=CAMUNDA_URL,
        config=WORKER_CONFIG
    )
    worker.subscribe(AUTH_TOPICS, handle_auth_task)
