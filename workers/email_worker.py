"""
Email Notification Worker
Handles all email topics: welcome, onboarding confirmation, quiz results,
achievement notifications, real-time lecture feedback, quiz-ready alerts.
"""
import logging
from camunda.external_task.external_task_worker import ExternalTaskWorker
from workers.config import CAMUNDA_URL, WORKER_CONFIG, WORKER_IDS, EMAIL_TOPICS
from workers.email_service import (send_welcome_email, send_onboarding_email,
                                    send_quiz_results_email, send_achievement_email,
                                    send_lecture_feedback_email, send_email)

logger = logging.getLogger("lms.email_worker")


def handle_email_task(task):
    """Route all email tasks by topic name."""
    topic = task.get_topic_name()
    logger.info("📧 Email task: topic=%s | pid=%s", topic, task.get_process_instance_id())

    try:
        # Common variables available in most processes
        user_email   = task.get_variable("userEmail") or task.get_variable("studentEmail") or ""
        username     = task.get_variable("username") or task.get_variable("studentName") or "Student"
        student_id   = task.get_variable("userId") or task.get_variable("studentId") or ""

        if not user_email:
            logger.warning("No email address found for topic %s — skipping", topic)
            return task.complete({"emailSent": False, "reason": "no_email_address"})
            return

        if topic == "send-welcome-email":
            role = task.get_variable("userType") or "student"
            dashboard = task.get_variable("redirectUrl") or "#"
            success = send_welcome_email(user_email, username, role.upper(), dashboard)

        elif topic == "send-confirmation-email":
            # Onboarding complete confirmation
            learning_path  = task.get_variable("nextLearningPath") or "Personalized Learning Path"
            resources_raw  = task.get_variable("assignedResources") or ""
            resources_list = [r.strip() for r in resources_raw.split(",") if r.strip()] or [
                "Video content library",
                "Interactive exercises",
                "Practice quizzes",
            ]
            success = send_onboarding_email(user_email, username, learning_path, resources_list)

        elif topic == "send-quiz-results-email":
            score     = int(task.get_variable("quizScore") or 0)
            passed    = bool(task.get_variable("quizPassed") or score >= 60)
            badge     = task.get_variable("badgeName") or None
            success   = send_quiz_results_email(user_email, username, score, passed, badge)

        elif topic == "send-achievement-email":
            badge_name     = task.get_variable("badgeName") or "Achievement"
            points_awarded = int(task.get_variable("pointsAwarded") or 0)
            total_points   = int(task.get_variable("totalPoints") or 0)
            success = send_achievement_email(user_email, username, badge_name, points_awarded, total_points)

        elif topic == "send-realtime-feedback":
            topic_name = task.get_variable("lectureTopic") or "Today's Lecture"
            feedback   = task.get_variable("feedbackText") or "Great participation in today's session!"
            success = send_lecture_feedback_email(user_email, username, topic_name, feedback)

        elif topic == "notify-student-quiz-ready":
            quiz_id     = task.get_variable("quizId") or "quiz-001"
            difficulty  = task.get_variable("nextDifficulty") or "Medium"
            quiz_url    = f"/student/quiz/{quiz_id}"
            subject = f"Your {difficulty} Quiz is Ready! 📝"
            html = f"""
            <div style="font-family:sans-serif;max-width:600px;margin:auto;padding:24px">
              <h2 style="color:#534AB7">Your Quiz is Ready! 📝</h2>
              <p>Hi <strong>{username}</strong>,</p>
              <p>Your personalized <strong>{difficulty}</strong> difficulty quiz has been generated and is ready to take.</p>
              <p>The AI has tailored the questions specifically to your learning level and style.</p>
              <a href="{quiz_url}" style="background:#534AB7;color:white;padding:12px 24px;
                 border-radius:8px;text-decoration:none;display:inline-block;margin-top:16px">
                Start Quiz →
              </a>
              <p style="color:#888;margin-top:24px;font-size:12px">AI-Enhanced LMS</p>
            </div>
            """
            text = f"Hi {username}, your {difficulty} quiz is ready! Go to {quiz_url} to start."
            success = send_email(user_email, subject, html, text)

        else:
            logger.warning("Unknown email topic: %s", topic)
            success = True  # Don't fail the process for unknown email topics

        return task.complete({
            "emailSent":     success,
            "emailTopic":    topic,
            "emailRecipient": user_email,
        })
        logger.info("✅ Email task done: %s → %s (%s)", topic, user_email, "sent" if success else "failed")

    except Exception as e:
        logger.error("Email task failed [%s]: %s", topic, str(e), exc_info=True)
        # Email failures should NOT fail the whole process — mark complete with error flag
        return task.complete({"emailSent": False, "emailError": str(e)})


def start():
    """Start the email worker — called by main.py."""
    logger.info("🚀 Email worker starting | Topics: %s", EMAIL_TOPICS)
    worker = ExternalTaskWorker(
        worker_id=WORKER_IDS["email"],
        base_url=CAMUNDA_URL,
        config=WORKER_CONFIG
    )
    worker.subscribe(EMAIL_TOPICS, handle_email_task)
