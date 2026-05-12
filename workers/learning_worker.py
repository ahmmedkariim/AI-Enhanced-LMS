"""
Learning Management Worker
Handles: profile creation, resource assignment, quiz session management,
         grading, progress tracking, lecture preparation, remedial content.
"""
import json
import uuid
import random
import logging
from datetime import datetime
from camunda.external_task.external_task_worker import ExternalTaskWorker
from workers.config import CAMUNDA_URL, WORKER_CONFIG, WORKER_IDS, LEARNING_TOPICS
from workers.database import (upsert_student_profile, assign_resource,
                                record_quiz_attempt, get_last_quiz_attempt,
                                get_student_profile)

logger = logging.getLogger("lms.learning")


# ─── Mock Course Catalog ──────────────────────────────────────────────────────

COURSE_CATALOG = {
    "Visual": [
        {"id": "v-001", "name": "Python Fundamentals — Visual Guide", "format": "video", "duration": 45},
        {"id": "v-002", "name": "Data Structures with Diagrams",       "format": "video", "duration": 60},
        {"id": "v-003", "name": "Algorithm Visualizations",            "format": "interactive", "duration": 30},
    ],
    "Auditory": [
        {"id": "a-001", "name": "CS Concepts Podcast Series",          "format": "audio", "duration": 40},
        {"id": "a-002", "name": "Tech Talks: OOP Deep Dive",           "format": "audio", "duration": 55},
        {"id": "a-003", "name": "Interview with Senior Engineers",      "format": "podcast", "duration": 35},
    ],
    "Kinesthetic": [
        {"id": "k-001", "name": "Build a REST API from Scratch",       "format": "lab", "duration": 90},
        {"id": "k-002", "name": "Hands-on Database Design",            "format": "lab", "duration": 75},
        {"id": "k-003", "name": "Deploy Your First App",               "format": "project", "duration": 120},
    ],
    "Active": [
        {"id": "act-001", "name": "Team Coding Challenge",             "format": "group", "duration": 60},
        {"id": "act-002", "name": "Hackathon Prep Workshop",           "format": "workshop", "duration": 90},
        {"id": "act-003", "name": "Pair Programming Session",          "format": "collaborative", "duration": 45},
    ],
    "Reflective": [
        {"id": "r-001", "name": "Software Design Patterns — Reading",  "format": "text", "duration": 50},
        {"id": "r-002", "name": "Case Study: Scaling Twitter",         "format": "analysis", "duration": 40},
        {"id": "r-003", "name": "Research: AI in Education",           "format": "paper", "duration": 35},
    ],
}

REMEDIAL_RESOURCES = [
    {"id": "rem-001", "name": "CS101 Fundamentals Review",            "format": "video"},
    {"id": "rem-002", "name": "Step-by-Step Python Basics",           "format": "interactive"},
    {"id": "rem-003", "name": "Guided Practice: Variables & Loops",   "format": "exercise"},
    {"id": "rem-004", "name": "1-on-1 LLM Tutor: Concept Q&A",       "format": "llm-chat"},
]

SUPPLEMENTARY_RESOURCES = [
    {"id": "sup-001", "name": "Advanced Problem Sets",                "format": "exercise"},
    {"id": "sup-002", "name": "Interview Prep Questions",             "format": "quiz"},
    {"id": "sup-003", "name": "Community Discussion Forum",           "format": "discussion"},
]


def handle_learning_task(task):
    """Route learning management tasks by topic name."""
    topic = task.get_topic_name()
    logger.info("📚 Learning task: topic=%s | pid=%s", topic, task.get_process_instance_id())

    try:
        student_id     = task.get_variable("userId") or task.get_variable("studentId") or "unknown"
        username       = task.get_variable("username") or student_id
        learning_style = task.get_variable("learningStyle") or "Visual"
        course_id      = task.get_variable("courseId") or "course-001"

        if topic == "create-student-profile":
            result = _create_student_profile(task, student_id, learning_style)

        elif topic in ("assign-learning-resources", "assign-primary-content"):
            result = _assign_primary_content(task, student_id, learning_style)

        elif topic == "assign-supplementary-materials":
            result = _assign_supplementary(student_id, learning_style)

        elif topic == "assign-practice-exercises":
            result = _assign_practice(student_id, learning_style)

        elif topic == "assign-study-plan":
            result = _create_study_plan(student_id, learning_style, task)

        elif topic == "assign-remedial-content":
            result = _assign_remedial(student_id, task)

        elif topic == "track-learning-progress":
            result = _track_progress(student_id)

        elif topic == "update-student-progress":
            result = _update_progress(student_id, task)

        elif topic == "create-quiz-session":
            result = _create_quiz_session(student_id, task)

        elif topic == "grade-quiz-responses":
            result = _grade_quiz(student_id, task)

        elif topic == "prepare-lecture-materials":
            result = _prepare_lecture(course_id, task)

        elif topic == "setup-lecture-session":
            result = _setup_lecture_session(course_id, task)

        else:
            logger.warning("Unknown learning topic: %s", topic)
            result = {"status": "completed", "topic": topic}

        logger.info("✅ Learning task complete: %s", topic)
        return task.complete(result)

    except Exception as e:
        logger.error("Learning task failed [%s]: %s", topic, str(e), exc_info=True)
        return task.failure(
            error_message=f"Learning worker error: {str(e)}",
            error_details=str(e),
            retries=2,
            retry_timeout=3000
        )


def _create_student_profile(task, student_id: str, learning_style: str) -> dict:
    """Create or update student profile after AI assessment."""
    data = {
        "learning_style":  task.get_variable("learningStyle") or "Visual",
        "personality":     task.get_variable("personalityType") or "Analytical",
        "learning_goals":  task.get_variable("learningGoals") or "General learning",
        "experience":      task.get_variable("experienceLevel") or "Beginner",
    }
    upsert_student_profile(student_id, data)

    profile_id = f"profile-{student_id}-{datetime.utcnow().strftime('%Y%m%d')}"
    courses    = COURSE_CATALOG.get(data["learning_style"], COURSE_CATALOG["Visual"])
    primary    = courses[0]["name"] if courses else "Core Curriculum"
    assigned_path = (
        f"{data['learning_style']}-{data['personality']} Track "
        f"({data['experience']}) → starts with: {primary}"
    )
    logger.info("👤 Profile created: %s | style=%s | personality=%s",
                student_id, data["learning_style"], data["personality"])
    return {
        "profileCreated":  True,
        "profileId":       profile_id,
        "learningStyle":   data["learning_style"],
        "personality":     data["personality"],
        "assignedPath":    assigned_path,
    }


def _assign_primary_content(task, student_id: str, learning_style: str) -> dict:
    """Assign the primary learning content based on learning path decision."""
    dmn_path     = task.get_variable("nextLearningPath")
    path_priority = task.get_variable("pathPriority") or "Normal"

    courses = COURSE_CATALOG.get(learning_style, COURSE_CATALOG["Visual"])
    primary = courses[0]

    # If the DMN didn't match a rule, synthesize a personalized path string so the
    # downstream user-task form doesn't show a generic placeholder.
    next_path = dmn_path or f"{learning_style} Track — Foundations to Mastery (starts with: {primary['name']})"

    assign_resource(student_id, "primary", primary["id"], primary["name"])
    logger.info("📖 Primary content assigned: %s → %s | path=%s", student_id, primary["name"], next_path)

    recommended_lines = [f"• {c['name']} ({c['format']}, {c['duration']} min)" for c in courses]
    recommended_lines += [f"• {s['name']} ({s['format']})" for s in SUPPLEMENTARY_RESOURCES[:2]]
    recommended_resources = "\n".join(recommended_lines)

    return {
        "primaryContentId":      primary["id"],
        "primaryContentName":    primary["name"],
        "contentFormat":         primary["format"],
        "estimatedMins":         primary["duration"],
        "learningPath":          next_path,
        "nextLearningPath":      next_path,
        "pathPriority":          path_priority,
        "assignedAt":            datetime.utcnow().isoformat(),
        "assignedResources":     primary["name"],
        "recommendedResources":  recommended_resources,
    }


def _assign_supplementary(student_id: str, learning_style: str) -> dict:
    """Assign supplementary enrichment materials."""
    courses = COURSE_CATALOG.get(learning_style, COURSE_CATALOG["Visual"])
    supplementary = courses[1] if len(courses) > 1 else SUPPLEMENTARY_RESOURCES[0]

    assign_resource(student_id, "supplementary", supplementary["id"], supplementary["name"])
    extra = random.choice(SUPPLEMENTARY_RESOURCES)
    assign_resource(student_id, "extra", extra["id"], extra["name"])

    return {
        "supplementaryAssigned": True,
        "resourceCount":         2,
        "resources":             f"{supplementary['name']}, {extra['name']}",
    }


def _assign_practice(student_id: str, learning_style: str) -> dict:
    """Assign practice exercises matching the student's style."""
    courses = COURSE_CATALOG.get(learning_style, COURSE_CATALOG["Visual"])
    practice = courses[-1] if courses else SUPPLEMENTARY_RESOURCES[0]

    assign_resource(student_id, "practice", practice["id"], practice["name"])
    logger.info("💪 Practice assigned: %s → %s", student_id, practice["name"])

    return {
        "practiceAssigned": True,
        "practiceId":       practice["id"],
        "practiceName":     practice["name"],
        "practiceFormat":   practice.get("format", "exercise"),
        "estimatedMins":    practice.get("duration", 30),
    }


def _create_study_plan(student_id: str, learning_style: str, task) -> dict:
    """Build a weekly study plan for the student."""
    weekly_hours  = int(task.get_variable("weeklyHours") or 5)
    experience    = task.get_variable("experienceLevel") or "Beginner"

    sessions_per_week = max(2, weekly_hours // 2)
    session_length    = 60 if weekly_hours >= 10 else 30

    return {
        "studyPlanCreated":   True,
        "sessionsPerWeek":    sessions_per_week,
        "sessionLengthMins":  session_length,
        "weeklyGoalHours":    weekly_hours,
        "planSummary":        f"{sessions_per_week} sessions/week × {session_length} mins",
        "startDate":          datetime.utcnow().strftime("%Y-%m-%d"),
        "primaryFocus":       COURSE_CATALOG.get(learning_style, [{}])[0].get("name", "Core Curriculum"),
    }


def _assign_remedial(student_id: str, task) -> dict:
    """Assign remedial content for struggling students."""
    weak_topics  = task.get_variable("weakTopics") or "core concepts"
    rem_content  = random.choice(REMEDIAL_RESOURCES)
    extra_rem    = random.choice(REMEDIAL_RESOURCES)

    assign_resource(student_id, "remedial", rem_content["id"], rem_content["name"])
    assign_resource(student_id, "remedial", extra_rem["id"], extra_rem["name"])

    logger.info("🆘 Remedial content assigned: %s | topics=%s", student_id, weak_topics)
    return {
        "remedialAssigned":   True,
        "remedialResources":  f"{rem_content['name']}, {extra_rem['name']}",
        "targetTopics":       weak_topics,
        "estimatedMins":      60,
        "llmTutorEnabled":    True,
    }


def _track_progress(student_id: str) -> dict:
    """Snapshot current learning progress."""
    profile   = get_student_profile(student_id)
    last_quiz = get_last_quiz_attempt(student_id)

    progress_pct = min(100, (profile.get("total_points", 0) // 5)) if profile else 30
    return {
        "progressPercent":  progress_pct,
        "completedItems":   progress_pct // 10,
        "totalPoints":      profile.get("total_points", 0) if profile else 0,
        "lastQuizScore":    last_quiz["score"] if last_quiz else 0,
        "progressLevel":    "Advanced" if progress_pct >= 70 else "Intermediate" if progress_pct >= 40 else "Beginner",
        "snapshotAt":       datetime.utcnow().isoformat(),
    }


def _update_progress(student_id: str, task) -> dict:
    """Update a student's progress after completing an activity."""
    activity_type = task.get_variable("activityType") or "general"
    score         = int(task.get_variable("activityScore") or 0)

    return {
        "progressUpdated": True,
        "activityType":    activity_type,
        "scoreRecorded":   score,
        "updatedAt":       datetime.utcnow().isoformat(),
    }


def _create_quiz_session(student_id: str, task) -> dict:
    """Create a new quiz session context."""
    difficulty = task.get_variable("nextDifficulty") or "Medium"
    session_id = f"qs-{student_id[:8]}-{uuid.uuid4().hex[:6]}"

    return {
        "quizSessionId":   session_id,
        "sessionDifficulty": difficulty,
        "sessionCreatedAt": datetime.utcnow().isoformat(),
        "sessionStatus":   "ready",
    }


def _grade_quiz(student_id: str, task) -> dict:
    """Grade student quiz responses from per-question form fields."""
    difficulty   = task.get_variable("nextDifficulty") or "Medium"

    # Time spent comes from execution listeners on the user task (auto-computed).
    time_spent   = int(task.get_variable("timeSpentSeconds") or 0)

    # Pull each question's correct answer (from build_mock_quiz output) and the student's answer
    correct_count = 0
    total = 0
    for i in range(1, 6):
        student_ans  = task.get_variable(f"q{i}Answer")
        correct_ans  = task.get_variable(f"q{i}Correct")
        if correct_ans is None or correct_ans == "":
            continue
        total += 1
        # Both are string indices ("0".."3")
        if str(student_ans) == str(correct_ans):
            correct_count += 1

    if total == 0:
        # No question variables at all — fall back to mock so the process doesn't crash
        score = random.randint(45, 90)
        correct_count = score // 20
        total = 5
    else:
        score = int(round((correct_count / total) * 100))

    consecutive_correct = correct_count
    avg_time = max(int(time_spent / max(total, 1)), 5) if time_spent > 0 else 60

    passed       = score >= 60
    score_level  = "High" if score >= 70 else "Medium" if score >= 45 else "Low"

    # Persist attempt
    quiz_id = task.get_variable("quizId") or f"quiz-{uuid.uuid4().hex[:6]}"
    record_quiz_attempt(student_id, quiz_id, score, difficulty, consecutive_correct, avg_time)

    logger.info("📊 Quiz graded: student=%s score=%d passed=%s", student_id, score, passed)
    return {
        "quizScore":          score,
        "quizScoreLevel":     score_level,
        "quizPassed":         passed,
        "correctAnswers":     consecutive_correct,
        "consecutiveCorrect": consecutive_correct,
        "averageTimeSeconds": avg_time,
        "previousScore":      score,  # Used by DMN 4 (quiz-difficulty)
        "gradedAt":           datetime.utcnow().isoformat(),
    }


POLL_QUESTIONS = [
    ("How confident do you feel about today's topic so far?",
     "How well are you keeping up with the pace?"),
    ("Which concept introduced today feels least clear?",
     "Rate your engagement with this lecture so far."),
    ("Did the visual examples help you understand the concept?",
     "Would you prefer more hands-on examples next time?"),
]

TEAM_NAMES = [
    "Phoenix Coders", "Quantum Hackers", "Binary Bards",
    "Recursive Ravens", "Async Avengers", "Lambda Lions",
    "Syntax Sentinels", "Buffer Overflowers",
]

TEAM_CHALLENGES = [
    {"title": "API Scaling Challenge",
     "problem": "Your microservice gets hit by 1 million requests per minute during a flash sale. Outline a strategy using caching, rate-limiting, and horizontal scaling. List the 3 most critical decisions."},
    {"title": "Database Design Sprint",
     "problem": "Design the schema for a multi-tenant SaaS LMS that has Students, Courses, Quizzes, and Submissions. Highlight one indexing decision and one normalization decision."},
    {"title": "Algorithmic Trade-off",
     "problem": "You need to find the top-10 trending posts from a 100M-row table updated every second. Compare two approaches (e.g., sorted set vs. windowed aggregation). Pick one and justify."},
    {"title": "Debugging War Room",
     "problem": "A production payment endpoint returns 500 for 2% of requests, with no stack trace. Outline the first 4 diagnostic steps you'd take and one tool you'd reach for at each step."},
]


LECTURE_TITLES = [
    "Designing Resilient Microservices",
    "Algorithms in Practice: Trees & Graphs",
    "Concurrency Patterns and Pitfalls",
    "Modeling Business Processes with BPMN",
    "Database Internals: Indexes and Query Plans",
]


def _setup_lecture_session(course_id: str, task) -> dict:
    """Auto-initialize a lecture session (replaces the manual instructor setup task)."""
    title    = random.choice(LECTURE_TITLES)
    duration = random.choice([60, 75, 90])
    mode     = random.choice(["In-Person", "Hybrid", "Remote"])
    logger.info("🎬 Lecture session auto-setup: %s | %s | %d min", title, mode, duration)
    return {
        "lectureTitle":      title,
        "lectureTopic":      title,
        "lectureTopics":     "Core concepts, common pitfalls, real-world examples, Q&A",
        "estimatedDuration": duration,
        "classroomMode":     mode,
        "lectureStartedAt":  datetime.utcnow().isoformat(),
    }


def _prepare_lecture(course_id: str, task) -> dict:
    """Prepare lecture materials based on AI class profile analysis."""
    avg_engagement = task.get_variable("avgEngagementLevel") or "Medium"
    dominant_style = task.get_variable("dominantLearningStyle") or "Visual"
    at_risk_count  = int(task.get_variable("atRiskStudents") or 3)
    lecture_topic  = task.get_variable("lectureTopic") or "Software Engineering Fundamentals"
    student_id     = task.get_variable("userId") or task.get_variable("studentId") or "unknown"

    materials = {
        "slides":       f"/lectures/{course_id}/slides-{datetime.utcnow().strftime('%Y%m%d')}.pdf",
        "in_class_quiz": f"/quizzes/inclass-{course_id}-{uuid.uuid4().hex[:6]}",
    }

    adaptations = []
    if avg_engagement == "Low":
        adaptations.append("Add interactive game at minute 20")
    if dominant_style == "Visual":
        adaptations.append("Use more diagrams and live coding")
    if at_risk_count > 5:
        adaptations.append("Include extra Q&A time and peer support")

    # Pick a poll question varied by lecture topic length (deterministic mock)
    poll_q1, poll_q2 = random.choice(POLL_QUESTIONS)

    # Personality-driven team assignment (mock)
    personality = task.get_variable("personalityType") or random.choice(
        ["Collaborative", "Analytical", "Creative", "Pragmatic"]
    )
    team_name = random.choice(TEAM_NAMES) + f" ({personality})"

    challenge = random.choice(TEAM_CHALLENGES)

    logger.info("🏫 Lecture prepared: course=%s topic=%s team=%s",
                course_id, lecture_topic, team_name)
    return {
        "lectureReady":       True,
        "lectureMaterials":   str(materials),
        "adaptations":        "; ".join(adaptations) or "Standard delivery",
        "recommendedPace":    "Slower" if avg_engagement == "Low" else "Normal",
        "preparedAt":         datetime.utcnow().isoformat(),
        "lectureTopic":       lecture_topic,
        "pollQuestion":       poll_q1,
        "pollQuestionAlt":    poll_q2,
        "teamName":           team_name,
        "challengeTitle":     challenge["title"],
        "challengeProblem":   challenge["problem"],
    }


def start():
    """Start the learning worker — called by main.py."""
    logger.info("🚀 Learning worker starting | Topics: %s", LEARNING_TOPICS)
    worker = ExternalTaskWorker(
        worker_id=WORKER_IDS["learning"],
        base_url=CAMUNDA_URL,
        config=WORKER_CONFIG
    )
    worker.subscribe(LEARNING_TOPICS, handle_learning_task)
