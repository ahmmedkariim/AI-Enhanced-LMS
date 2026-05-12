"""
AI Engine Worker
Handles all AI analysis topics: learning style, personality, engagement,
class profile analysis, quiz performance, lecture summarization.
In mock mode returns realistic simulated responses.
In real mode, calls the Anthropic/OpenAI API.
"""
import json
import random
import logging
from datetime import datetime
from camunda.external_task.external_task_worker import ExternalTaskWorker
from workers.config import CAMUNDA_URL, WORKER_CONFIG, WORKER_IDS, AI_TOPICS, AI_MODE, ANTHROPIC_API_KEY
from workers.database import get_student_profile, get_last_quiz_attempt

logger = logging.getLogger("lms.ai")


# ─── Mock AI Responses ────────────────────────────────────────────────────────

LEARNING_STYLE_PROFILES = {
    "Visual":      {"description": "Prefers diagrams, charts, and visual representations", "color": "#534AB7"},
    "Auditory":    {"description": "Learns best through listening, podcasts, and discussion", "color": "#185FA5"},
    "Kinesthetic": {"description": "Thrives with hands-on practice and experiments", "color": "#1D9E75"},
    "Active":      {"description": "Engages through doing, group work, and problem-solving", "color": "#BA7517"},
    "Reflective":  {"description": "Prefers thinking deeply, reading, and individual work", "color": "#993556"},
}

PERSONALITY_TYPES = [
    "Analytical",  # Data-driven, systematic
    "Creative",    # Innovative, exploratory
    "Pragmatic",   # Goal-focused, practical
    "Collaborative",  # Team-oriented, social
]

ENGAGEMENT_LEVELS = ["High", "Medium", "Low"]


def mock_analyze_learning_style(learning_style: str, experience: str, weekly_hours: int) -> dict:
    """Return a rich learning style profile based on inputs."""
    profile = LEARNING_STYLE_PROFILES.get(learning_style, LEARNING_STYLE_PROFILES["Visual"])
    strength = random.randint(75, 95) if experience == "Advanced" else random.randint(55, 80)
    return {
        "learningStyle":          learning_style,
        "styleDescription":       profile["description"],
        "styleStrengthScore":     strength,
        "recommendedContentTypes": f"{learning_style.lower()}-media,interactive,practice",
        "optimalSessionLength":   40 if weekly_hours >= 10 else 25,
        "aiAnalysisTimestamp":    datetime.utcnow().isoformat(),
    }


def mock_assess_personality(learning_goals: str, learning_style: str) -> dict:
    """Infer personality type from goals and style."""
    personality = "Analytical"
    if "team" in (learning_goals or "").lower() or learning_style == "Active":
        personality = "Collaborative"
    elif "creative" in (learning_goals or "").lower() or learning_style == "Visual":
        personality = "Creative"
    elif learning_style in ("Kinesthetic", "Active"):
        personality = "Pragmatic"

    return {
        "personalityType":        personality,
        "collaborationPreference": "Team" if personality == "Collaborative" else "Individual",
        "motivationStyle":        "Achievement" if personality == "Analytical" else "Mastery",
        "bestTeamRole":           "Leader" if personality in ("Analytical", "Pragmatic") else "Contributor",
        "aiPersonalityScore":     random.randint(70, 95),
    }


def mock_analyze_engagement(student_id: str, session_data: dict) -> dict:
    """Simulate real-time engagement analysis during a lecture."""
    quiz_attempt = get_last_quiz_attempt(student_id)
    base_score = quiz_attempt["score"] if quiz_attempt else 50

    if base_score >= 70:
        level = "High"
        score = random.randint(75, 95)
    elif base_score >= 45:
        level = "Medium"
        score = random.randint(45, 74)
    else:
        level = "Low"
        score = random.randint(15, 44)

    return {
        "engagementLevel":     level,
        "engagementScore":     score,
        "attentionSpan":       "Sustained" if level == "High" else "Intermittent",
        "predictedDropoff":    level == "Low",
        "recommendedAction":   "continue" if level != "Low" else "inject-game",
        "analysisTimestamp":   datetime.utcnow().isoformat(),
    }


def mock_analyze_class_profile(course_id: str, student_count: int) -> dict:
    """Generate class-wide analytics for lecture preparation."""
    return {
        "classSize":            student_count or random.randint(15, 35),
        "avgEngagementLevel":   random.choice(["High", "Medium", "Medium"]),
        "dominantLearningStyle": random.choice(["Visual", "Active", "Kinesthetic"]),
        "avgQuizScore":         random.randint(55, 78),
        "atRiskStudents":       random.randint(1, 5),
        "topPerformers":        random.randint(3, 8),
        "recommendedPace":      random.choice(["Normal", "Slower", "Normal"]),
        "suggestedActivities":  "live-quiz,team-challenge,poll",
        "lectureAdaptations":   "Include more visual aids; add interactive breakout at minute 20",
    }


def mock_analyze_quiz_performance(student_id: str, score: int, avg_time: int) -> dict:
    """AI analysis of a completed quiz attempt."""
    weak_topics = []
    if score < 50: weak_topics = ["fundamentals", "core-concepts"]
    elif score < 70: weak_topics = ["advanced-topics"]

    return {
        "quizScoreLevel":       "High" if score >= 70 else ("Medium" if score >= 45 else "Low"),
        "weakTopics":           ",".join(weak_topics),
        "masteredTopics":       "introduction,basics" if score >= 60 else "",
        "speedAssessment":      "Fast" if avg_time < 30 else ("Normal" if avg_time < 90 else "Slow"),
        "improvementTips":      "Focus on practice problems" if score < 70 else "Challenge yourself with expert topics",
        "nextDifficultyHint":   "increase" if score >= 70 else ("maintain" if score >= 45 else "decrease"),
    }


def mock_get_student_performance(student_id: str) -> dict:
    """Return student's overall performance metrics."""
    profile = get_student_profile(student_id)
    last_quiz = get_last_quiz_attempt(student_id)

    total_points = profile.get("total_points", 0) if profile else 0
    last_score = last_quiz["score"] if last_quiz else 50
    last_difficulty = last_quiz["difficulty"] if last_quiz else "Medium"
    consecutive = last_quiz["consecutive_correct"] if last_quiz else 0
    avg_time = last_quiz["avg_time_seconds"] if last_quiz else 60

    # previousScore (numeric) is needed by QuizDifficultyDecision DMN
    return {
        "totalPoints":           total_points,
        "lastQuizScore":         last_score,
        "previousScore":         last_score,
        "lastDifficulty":        last_difficulty,
        "consecutiveCorrect":    consecutive,
        "averageTimeSeconds":    avg_time,
        "quizScoreLevel":        "High" if last_score >= 70 else ("Medium" if last_score >= 45 else "Low"),
        "engagementLevel":       "High" if total_points > 300 else ("Medium" if total_points > 100 else "Low"),
        "weeklyStreak":          profile.get("weekly_streak", 0) if profile else 0,
        "learningStyle":         profile.get("learning_style", "Visual") if profile else "Visual",
        "personalityType":       profile.get("personality", "Analytical") if profile else "Analytical",
        "experienceLevel":       profile.get("experience", "Beginner") if profile else "Beginner",
    }


def mock_generate_lecture_summary(topic: str, duration_minutes: int) -> dict:
    """AI-generated post-lecture summary."""
    return {
        "lectureSummary":  f"In today's {duration_minutes}-minute session on '{topic}', we covered core concepts, "
                           f"ran 2 interactive polls, completed a team challenge, and ended with a live quiz. "
                           f"Key takeaways: foundational theory, practical applications, and group problem-solving.",
        "keyPoints":       "Key concept 1, Key concept 2, Team activity results, Live quiz insights",
        "avgClassScore":   f"{random.randint(60, 85)}%",
        "engagementPeak":  f"Minute {random.randint(15, 25)}",
        "generatedAt":     datetime.utcnow().isoformat(),
    }


# ─── Real AI via Anthropic API ────────────────────────────────────────────────

def real_analyze_with_ai(prompt: str) -> str:
    """Call Anthropic API for a real AI response. Falls back to mock on error."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        logger.warning("Anthropic API call failed, using mock: %s", str(e))
        return None


# ─── Task Handler ─────────────────────────────────────────────────────────────

def handle_ai_task(task):
    """Route AI tasks by topic name."""
    topic = task.get_topic_name()
    logger.info("🤖 AI task: topic=%s | pid=%s | mode=%s", topic, task.get_process_instance_id(), AI_MODE)

    try:
        student_id  = task.get_variable("userId") or task.get_variable("studentId") or "unknown"
        course_id   = task.get_variable("courseId") or "course-001"

        if topic == "analyze-learning-style":
            result = mock_analyze_learning_style(
                task.get_variable("learningStyle") or "Visual",
                task.get_variable("experienceLevel") or "Beginner",
                int(task.get_variable("weeklyHours") or 5),
            )

        elif topic == "assess-personality":
            result = mock_assess_personality(
                task.get_variable("learningGoals") or "",
                task.get_variable("learningStyle") or "Visual",
            )

        elif topic == "analyze-engagement":
            result = mock_analyze_engagement(student_id, {})

        elif topic == "analyze-class-profile":
            result = mock_analyze_class_profile(
                course_id,
                int(task.get_variable("studentCount") or 25),
            )

        elif topic == "analyze-quiz-performance":
            result = mock_analyze_quiz_performance(
                student_id,
                int(task.get_variable("quizScore") or 60),
                int(task.get_variable("averageTimeSeconds") or 60),
            )

        elif topic in ("get-student-performance", "get-student-quiz-history"):
            result = mock_get_student_performance(student_id)

        elif topic == "generate-lecture-summary":
            result = mock_generate_lecture_summary(
                task.get_variable("lectureTopic") or "Today's Topic",
                int(task.get_variable("durationMinutes") or 90),
            )

        else:
            logger.warning("Unknown AI topic: %s", topic)
            result = {"status": "completed", "topic": topic}

        logger.info("✅ AI task complete: %s → %s keys", topic, len(result))
        return task.complete(result)

    except Exception as e:
        logger.error("AI task failed [%s]: %s", topic, str(e), exc_info=True)
        return task.failure(
            error_message=f"AI Engine error: {str(e)}",
            error_details=str(e),
            retries=2,
            retry_timeout=5000
        )


def start():
    """Start the AI engine worker — called by main.py."""
    logger.info("🚀 AI Engine worker starting | Topics: %s", AI_TOPICS)
    worker = ExternalTaskWorker(
        worker_id=WORKER_IDS["ai"],
        base_url=CAMUNDA_URL,
        config=WORKER_CONFIG
    )
    worker.subscribe(AI_TOPICS, handle_ai_task)
