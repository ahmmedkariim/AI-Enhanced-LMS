"""
Email service using Gmail SMTP.
In mock mode (EMAIL_MODE=mock), logs emails instead of sending them.
To use Gmail: generate an App Password at https://myaccount.google.com/apppasswords
"""
import smtplib
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from workers.config import SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM

logger = logging.getLogger("lms.email")

EMAIL_MODE = os.getenv("EMAIL_MODE", "mock")


def send_email(to_address: str, subject: str, html_body: str, text_body: str = None) -> bool:
    """
    Send an email. Returns True on success.
    In mock mode, just logs the email content.
    """
    if EMAIL_MODE == "mock":
        logger.info("📧 [MOCK EMAIL] To: %s | Subject: %s", to_address, subject)
        logger.info("📧 [MOCK EMAIL BODY PREVIEW]\n%s", text_body or html_body[:200])
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{SMTP_FROM} <{SMTP_USERNAME}>"
        msg["To"]      = to_address

        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_address, msg.as_string())

        logger.info("✅ Email sent to %s: %s", to_address, subject)
        return True

    except Exception as e:
        logger.error("❌ Failed to send email to %s: %s", to_address, str(e))
        return False


# ─── Pre-built Email Templates ────────────────────────────────────────────────

def send_welcome_email(to_address: str, username: str, role: str, dashboard_url: str = "#") -> bool:
    subject = f"Welcome to AI-Enhanced LMS, {username}!"
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;padding:24px">
      <h2 style="color:#534AB7">Welcome to AI-Enhanced LMS! 🎓</h2>
      <p>Hi <strong>{username}</strong>,</p>
      <p>Your account has been successfully created with the role: <strong>{role}</strong>.</p>
      <p>You now have access to:</p>
      <ul>
        <li>🤖 AI-powered adaptive learning paths</li>
        <li>📝 LLM-generated personalized quizzes</li>
        <li>🏆 Gamification & rewards system</li>
        <li>🏫 Hybrid classroom features</li>
      </ul>
      <a href="{dashboard_url}" style="background:#534AB7;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;margin-top:16px">
        Go to Dashboard →
      </a>
      <p style="color:#888;margin-top:24px;font-size:12px">AI-Enhanced LMS | Software Process Engineering Project</p>
    </div>
    """
    text = f"Welcome {username}! Your {role} account is ready. Login to get started."
    return send_email(to_address, subject, html, text)


def send_onboarding_email(to_address: str, username: str, learning_path: str, resources: list) -> bool:
    subject = "Your Personalized Learning Plan is Ready! 📚"
    resource_items = "".join(f"<li>{r}</li>" for r in resources)
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;padding:24px">
      <h2 style="color:#1D9E75">Your Learning Plan is Ready! 📚</h2>
      <p>Hi <strong>{username}</strong>,</p>
      <p>Our AI has analyzed your profile and created a personalized learning experience for you.</p>
      <h3>Your Learning Path: <em>{learning_path}</em></h3>
      <p>Assigned resources:</p>
      <ul>{resource_items}</ul>
      <p>Start learning now and earn your first badge!</p>
      <p style="color:#888;margin-top:24px;font-size:12px">AI-Enhanced LMS</p>
    </div>
    """
    text = f"Hi {username}, your learning plan '{learning_path}' is ready with {len(resources)} resources."
    return send_email(to_address, subject, html, text)


def send_quiz_results_email(to_address: str, username: str, score: int,
                             passed: bool, badge_name: str = None) -> bool:
    status = "Passed ✅" if passed else "Keep going! 💪"
    subject = f"Quiz Results: {score}% — {status}"
    badge_section = f"<p>🏅 You earned: <strong>{badge_name}</strong></p>" if badge_name else ""
    color = "#639922" if passed else "#BA7517"
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;padding:24px">
      <h2 style="color:{color}">Quiz Results</h2>
      <p>Hi <strong>{username}</strong>,</p>
      <p style="font-size:48px;text-align:center;margin:16px 0"><strong>{score}%</strong></p>
      <p style="text-align:center">{status}</p>
      {badge_section}
      {"<p>Your adaptive learning path has been updated based on this result.</p>" if not passed else ""}
      <p style="color:#888;margin-top:24px;font-size:12px">AI-Enhanced LMS</p>
    </div>
    """
    text = f"Hi {username}, your quiz score: {score}%. {status}"
    return send_email(to_address, subject, html, text)


def send_achievement_email(to_address: str, username: str, badge_name: str,
                            points_awarded: int, total_points: int) -> bool:
    subject = f"🏆 Achievement Unlocked: {badge_name}!"
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;padding:24px">
      <h2 style="color:#BA7517">Achievement Unlocked! 🏆</h2>
      <p>Congratulations <strong>{username}</strong>!</p>
      <div style="background:#FAEEDA;border-radius:12px;padding:24px;text-align:center;margin:16px 0">
        <p style="font-size:24px;margin:0">🏅 <strong>{badge_name}</strong></p>
        <p style="color:#BA7517">+{points_awarded} points</p>
      </div>
      <p>Total points: <strong>{total_points}</strong></p>
      <p>Keep learning to unlock more achievements!</p>
      <p style="color:#888;margin-top:24px;font-size:12px">AI-Enhanced LMS</p>
    </div>
    """
    text = f"Congratulations {username}! You earned '{badge_name}' (+{points_awarded} points). Total: {total_points}"
    return send_email(to_address, subject, html, text)


def send_lecture_feedback_email(to_address: str, username: str, topic: str, feedback: str) -> bool:
    subject = f"Feedback from today's lecture: {topic}"
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;padding:24px">
      <h2 style="color:#185FA5">Lecture Feedback 📝</h2>
      <p>Hi <strong>{username}</strong>, here's your personalized feedback from today's lecture on <em>{topic}</em>:</p>
      <div style="background:#E6F1FB;border-left:4px solid #185FA5;padding:16px;border-radius:4px">
        <p>{feedback}</p>
      </div>
      <p style="color:#888;margin-top:24px;font-size:12px">AI-Enhanced LMS</p>
    </div>
    """
    text = f"Hi {username}, feedback from lecture '{topic}': {feedback}"
    return send_email(to_address, subject, html, text)
