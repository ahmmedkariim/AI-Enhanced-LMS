"""
LLM Tutor Worker
Handles all LLM content generation: adaptive quizzes, in-class quizzes,
post-lecture quizzes, personalized content, feedback, and remedial explanations.
Mock mode: returns realistic pre-built quiz templates.
Real mode: calls OpenAI / Anthropic API.
"""
import json
import random
import logging
from datetime import datetime
from camunda.external_task.external_task_worker import ExternalTaskWorker
from workers.config import (CAMUNDA_URL, WORKER_CONFIG, WORKER_IDS,
                              LLM_TOPICS, LLM_MODE, OPENAI_API_KEY, ANTHROPIC_API_KEY)

logger = logging.getLogger("lms.llm")


# ─── Mock Quiz Templates ──────────────────────────────────────────────────────

QUIZ_TEMPLATES = {
    "Easy": [
        {"q": "What is a variable in programming?",
         "options": ["A stored value", "A loop", "A function", "A database"],
         "answer": 0, "explanation": "A variable is a named container that stores a value in memory."},
        {"q": "Which symbol is used for comments in Python?",
         "options": ["//", "/*", "#", "--"],
         "answer": 2, "explanation": "Python uses the # symbol for single-line comments."},
        {"q": "What does HTML stand for?",
         "options": ["HyperText Markup Language", "High Tech Modern Language", "Hyper Transfer Meta Language", "None"],
         "answer": 0, "explanation": "HTML = HyperText Markup Language, the standard for web pages."},
        {"q": "What is the output of print(2 + 3)?",
         "options": ["23", "5", "2+3", "Error"],
         "answer": 1, "explanation": "Python adds the integers: 2 + 3 = 5."},
        {"q": "What is a boolean value?",
         "options": ["A number", "True or False", "A word", "A list"],
         "answer": 1, "explanation": "Boolean values are True or False — the basis of logic in programming."},
    ],
    "Medium": [
        {"q": "What is the time complexity of binary search?",
         "options": ["O(n)", "O(n²)", "O(log n)", "O(1)"],
         "answer": 2, "explanation": "Binary search halves the search space each step: O(log n)."},
        {"q": "What is a REST API?",
         "options": ["A database type", "An architectural style for web services", "A programming language", "A framework"],
         "answer": 1, "explanation": "REST (Representational State Transfer) is an architectural style using HTTP."},
        {"q": "Which HTTP method is used to update a resource?",
         "options": ["GET", "POST", "PUT", "DELETE"],
         "answer": 2, "explanation": "PUT replaces a resource entirely; PATCH for partial updates."},
        {"q": "What does SQL stand for?",
         "options": ["Structured Query Language", "System Query Logic", "Sequential Query Line", "Secure Query Layer"],
         "answer": 0, "explanation": "SQL = Structured Query Language — used to manage relational databases."},
        {"q": "What is polymorphism in OOP?",
         "options": ["Multiple inheritance", "One interface, many implementations", "Hiding data", "Encapsulation"],
         "answer": 1, "explanation": "Polymorphism allows objects of different classes to be treated as the same type."},
    ],
    "Hard": [
        {"q": "Which algorithm is used in Dijkstra's shortest path?",
         "options": ["Depth-first search", "Greedy with priority queue", "Dynamic programming only", "Backtracking"],
         "answer": 1, "explanation": "Dijkstra's uses a greedy approach with a min-heap priority queue."},
        {"q": "What is the CAP theorem?",
         "options": ["A caching algorithm", "Consistency-Availability-Partition tolerance tradeoff",
                    "A compression method", "A cryptographic protocol"],
         "answer": 1, "explanation": "CAP: distributed systems can guarantee only 2 of 3: Consistency, Availability, Partition tolerance."},
        {"q": "In BPMN, what does an Event-Based Gateway wait for?",
         "options": ["A timer only", "The first event to occur", "All events to occur", "A user decision"],
         "answer": 1, "explanation": "An Event-Based Gateway routes to whichever connected event fires first."},
        {"q": "What is a DMN decision table's FIRST hit policy?",
         "options": ["All matching rules fire", "Only the first matching rule fires", "Rules are ranked", "Random rule fires"],
         "answer": 1, "explanation": "FIRST hit policy evaluates rules top-to-bottom and stops at the first match."},
        {"q": "What is eventual consistency in distributed systems?",
         "options": ["Data is always consistent", "All nodes will eventually agree if no new updates arrive",
                    "Updates are synchronous", "A RDBMS concept"],
         "answer": 1, "explanation": "Eventual consistency guarantees nodes will converge given no new writes — a BASE property."},
    ],
    "Expert": [
        {"q": "What is the difference between SAGA and 2PC in distributed transactions?",
         "options": ["No difference", "SAGA uses compensating transactions; 2PC uses a coordinator lock",
                    "2PC is faster", "SAGA requires all services to be available"],
         "answer": 1, "explanation": "SAGA breaks transactions into local steps with compensations; 2PC locks all participants."},
        {"q": "In Camunda, what is the External Task pattern?",
         "options": ["Tasks executed inside the engine", "Workers poll the engine via REST and execute tasks externally",
                    "Tasks with external variables", "An event subprocess"],
         "answer": 1, "explanation": "External Tasks let Camunda delegate work to external workers that poll via REST API."},
    ],
}

FEEDBACK_TEMPLATES = {
    "excellent": [
        "Outstanding performance! You've clearly mastered this material. Try the expert challenge next!",
        "Excellent work! Your understanding is well above average. Keep pushing your limits!",
    ],
    "good": [
        "Good job! You've got a solid grasp of the fundamentals. Focus on the highlighted weak areas to advance.",
        "Well done! You're making great progress. A little more practice on {weak_topics} will get you to the next level.",
    ],
    "needs_work": [
        "Keep going! Learning takes time. Let's revisit the core concepts with a different approach.",
        "Don't give up! Everyone struggles at first. Your personalized remedial content is ready to help.",
    ],
}


def build_mock_quiz(difficulty: str, question_count: int, topic: str = "General Programming") -> dict:
    """Build a realistic mock quiz for the given difficulty."""
    pool = QUIZ_TEMPLATES.get(difficulty, QUIZ_TEMPLATES["Medium"])
    selected = random.sample(pool, min(question_count, len(pool)))

    quiz_id = f"quiz-{difficulty.lower()}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    return {
        "quizId":         quiz_id,
        "topic":          topic,
        "difficulty":     difficulty,
        "questionCount":  len(selected),
        "timeLimitSecs":  question_count * 60,
        "questions":      json.dumps(selected),
        "generatedBy":    "LLM Tutor (Mock)",
        "generatedAt":    datetime.utcnow().isoformat(),
        "hintsEnabled":   difficulty in ("Easy", "Medium"),
    }


def generate_with_llm(prompt: str, max_tokens: int = 1000) -> str | None:
    """Call real LLM API. Returns text or None on failure."""
    if LLM_MODE == "anthropic" and ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return msg.content[0].text
        except Exception as e:
            logger.warning("Anthropic call failed: %s", e)

    elif LLM_MODE == "openai" and OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.warning("OpenAI call failed: %s", e)

    return None


def handle_llm_task(task):
    """Route LLM tasks by topic name."""
    topic = task.get_topic_name()
    logger.info("🧠 LLM task: topic=%s | pid=%s | mode=%s", topic, task.get_process_instance_id(), LLM_MODE)

    try:
        student_id   = task.get_variable("userId") or task.get_variable("studentId") or "unknown"
        difficulty   = task.get_variable("nextDifficulty") or task.get_variable("difficulty") or "Medium"
        q_count      = int(task.get_variable("questionCount") or 8)
        learning_style = task.get_variable("learningStyle") or "Visual"
        course_topic = task.get_variable("courseTopic") or "Software Engineering"

        if topic == "generate-adaptive-quiz":
            result = build_mock_quiz(difficulty, q_count, course_topic)
            logger.info("📝 Generated %s quiz (%s Qs) for student %s", difficulty, q_count, student_id)

        elif topic == "generate-inclass-quiz":
            # Shorter, faster in-class quiz
            result = build_mock_quiz("Medium", min(q_count, 5), course_topic)
            result["quizId"] = f"inclass-{result['quizId']}"
            result["timeLimitSecs"] = 120  # 2 minutes for in-class

        elif topic == "generate-post-lecture-quiz":
            result = build_mock_quiz(difficulty, q_count, course_topic)
            result["quizId"] = f"post-lecture-{result['quizId']}"

        elif topic == "generate-personalized-content":
            result = {
                "contentType":    learning_style.lower() + "-module",
                "contentTitle":   f"Personalized {course_topic} Module — {learning_style} Learner",
                "contentUrl":     f"/content/{learning_style.lower()}/{course_topic.lower().replace(' ', '-')}",
                "estimatedMins":  random.randint(20, 45),
                "contentFormat":  "video" if learning_style == "Visual" else
                                  "podcast" if learning_style == "Auditory" else "interactive",
                "generatedAt":    datetime.utcnow().isoformat(),
            }

        elif topic == "generate-positive-feedback":
            score = int(task.get_variable("quizScore") or 80)
            if score >= 80:
                feedback = random.choice(FEEDBACK_TEMPLATES["excellent"])
            elif score >= 60:
                feedback = random.choice(FEEDBACK_TEMPLATES["good"])
            else:
                feedback = random.choice(FEEDBACK_TEMPLATES["needs_work"])
            result = {
                "feedbackText":   feedback,
                "motivationLevel": "High" if score >= 75 else "Medium",
                "nextChallenge":  "Try the expert-level quiz!" if score >= 80 else "Practice 10 more exercises",
            }

        elif topic == "generate-remedial-explanation":
            weak_topics = task.get_variable("weakTopics") or "core concepts"
            real_explanation = generate_with_llm(
                f"Explain '{weak_topics}' in simple terms for a {learning_style} learner in 2-3 sentences."
            )
            result = {
                "remedialContent":    real_explanation or f"Let's revisit '{weak_topics}'. Focus on building a strong foundation before advancing.",
                "remedialExercises":  f"Complete 5 practice problems on {weak_topics}",
                "studyTips":          f"As a {learning_style} learner, try {'drawing diagrams' if learning_style == 'Visual' else 'explaining aloud' if learning_style == 'Auditory' else 'hands-on practice'}",
                "estimatedReviewMins": random.randint(15, 30),
            }

        elif topic == "assign-llm-tutor":
            result = {
                "tutorAssigned":  True,
                "tutorMode":      "async",
                "sessionUrl":     f"/llm-tutor/session/{student_id}",
                "initialPrompt":  f"Hello! I'm your AI tutor. I see you're working on {course_topic}. What would you like help with?",
            }

        else:
            logger.warning("Unknown LLM topic: %s", topic)
            result = {"status": "completed", "topic": topic}

        logger.info("✅ LLM task complete: %s", topic)
        return task.complete(result)

    except Exception as e:
        logger.error("LLM task failed [%s]: %s", topic, str(e), exc_info=True)
        return task.failure(
            error_message=f"LLM Tutor error: {str(e)}",
            error_details=str(e),
            retries=2,
            retry_timeout=8000
        )


def start():
    """Start the LLM tutor worker — called by main.py."""
    logger.info("🚀 LLM Tutor worker starting | Topics: %s", LLM_TOPICS)
    worker = ExternalTaskWorker(
        worker_id=WORKER_IDS["llm"],
        base_url=CAMUNDA_URL,
        config=WORKER_CONFIG
    )
    worker.subscribe(LLM_TOPICS, handle_llm_task)
