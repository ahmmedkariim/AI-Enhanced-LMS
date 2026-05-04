"""
Shared configuration for all Camunda External Task Workers.
Loads settings from .env file — never hardcode credentials here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Camunda Engine ──────────────────────────────────────────────────────────
CAMUNDA_URL = os.getenv("CAMUNDA_REST_URL", "http://127.0.0.1:8080/engine-rest")
CAMUNDA_USER = os.getenv("CAMUNDA_USERNAME", "demo")
CAMUNDA_PASS = os.getenv("CAMUNDA_PASSWORD", "demo")

# ─── Worker Polling Settings ──────────────────────────────────────────────────
WORKER_CONFIG = {
    "maxTasks": 5,
    "lockDuration": 10000,          # 10 seconds
    "asyncResponseTimeout": 5000,   # 5 seconds long-polling
    "retries": 3,
    "retryTimeout": 5000,
    "sleepSeconds": 0,
}

# ─── Email (Gmail SMTP) ──────────────────────────────────────────────────────
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")
SMTP_FROM     = os.getenv("SMTP_FROM_NAME", "AI-Enhanced LMS")

# ─── AI / LLM Mode ───────────────────────────────────────────────────────────
# Set to "mock" for demo — no API keys needed
# Set to "openai" or "anthropic" for real AI responses
AI_MODE  = os.getenv("AI_MODE", "mock")
LLM_MODE = os.getenv("LLM_MODE", "mock")

OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/lms.db")
DB_PATH = DATABASE_URL.replace("sqlite:///", "")

# ─── Worker IDs (must be unique per running instance) ─────────────────────────
WORKER_IDS = {
    "auth":          "lms-auth-worker-1",
    "ai":            "lms-ai-worker-1",
    "llm":           "lms-llm-worker-1",
    "gamification":  "lms-gamification-worker-1",
    "email":         "lms-email-worker-1",
    "learning":      "lms-learning-worker-1",
}

# ─── Topic Routing ────────────────────────────────────────────────────────────
AUTH_TOPICS = [
    "validate-credentials",
    "init-student-session",
    "init-instructor-session",
    "init-admin-session",
]

AI_TOPICS = [
    "analyze-learning-style",
    "assess-personality",
    "analyze-engagement",
    "analyze-class-profile",
    "analyze-quiz-performance",
    "get-student-performance",
    "get-student-quiz-history",
    "generate-lecture-summary",
]

LLM_TOPICS = [
    "generate-adaptive-quiz",
    "generate-inclass-quiz",
    "generate-post-lecture-quiz",
    "generate-personalized-content",
    "generate-positive-feedback",
    "generate-remedial-explanation",
    "assign-llm-tutor",
]

GAMIFICATION_TOPICS = [
    "award-premium-badge",
    "award-standard-badge",
    "award-participation-points",
    "award-completion-badge",
    "award-points",
    "update-points-balance",
    "update-leaderboard",
    "update-gamification-analytics",
    "unlock-special-achievement",
]

EMAIL_TOPICS = [
    "send-welcome-email",
    "send-confirmation-email",
    "send-quiz-results-email",
    "send-achievement-email",
    "send-realtime-feedback",
    "notify-student-quiz-ready",
]

LEARNING_TOPICS = [
    "create-student-profile",
    "assign-learning-resources",
    "assign-primary-content",
    "assign-supplementary-materials",
    "assign-practice-exercises",
    "assign-study-plan",
    "assign-remedial-content",
    "track-learning-progress",
    "update-student-progress",
    "create-quiz-session",
    "grade-quiz-responses",
    "prepare-lecture-materials",
]
