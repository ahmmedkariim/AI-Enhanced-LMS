"""
Lightweight SQLite database layer for the LMS.
Uses plain sqlite3 — no heavy ORM needed for this demo.
"""
import sqlite3
import json
import os
import logging
from datetime import datetime
from workers.config import DB_PATH

logger = logging.getLogger("lms.database")


def get_connection():
    """Return a thread-safe SQLite connection."""
    os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # access columns by name
    return conn


def init_db():
    """Create all tables if they don't exist. Called once at startup."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        -- Users table (students, instructors, admins)
        CREATE TABLE IF NOT EXISTS users (
            id          TEXT PRIMARY KEY,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            email       TEXT NOT NULL,
            user_type   TEXT NOT NULL,
            email_domain TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- Student profiles (extended info after onboarding)
        CREATE TABLE IF NOT EXISTS student_profiles (
            student_id      TEXT PRIMARY KEY,
            learning_style  TEXT DEFAULT 'Visual',
            personality     TEXT DEFAULT 'Analytical',
            learning_goals  TEXT,
            experience      TEXT DEFAULT 'Beginner',
            total_points    INTEGER DEFAULT 0,
            weekly_streak   INTEGER DEFAULT 0,
            last_active     TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id)
        );

        -- Courses and enrollments
        CREATE TABLE IF NOT EXISTS enrollments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT NOT NULL,
            course_id   TEXT NOT NULL,
            enrolled_at TEXT DEFAULT CURRENT_TIMESTAMP,
            progress    INTEGER DEFAULT 0
        );

        -- Quiz attempts
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id      TEXT NOT NULL,
            quiz_id         TEXT NOT NULL,
            score           INTEGER DEFAULT 0,
            difficulty      TEXT DEFAULT 'Medium',
            consecutive_correct INTEGER DEFAULT 0,
            avg_time_seconds    INTEGER DEFAULT 60,
            attempted_at    TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- Badges and rewards
        CREATE TABLE IF NOT EXISTS badges (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT NOT NULL,
            badge_name  TEXT NOT NULL,
            badge_icon  TEXT,
            points      INTEGER DEFAULT 0,
            earned_at   TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- Leaderboard
        CREATE TABLE IF NOT EXISTS leaderboard (
            student_id  TEXT PRIMARY KEY,
            username    TEXT NOT NULL,
            total_points INTEGER DEFAULT 0,
            badge_count  INTEGER DEFAULT 0,
            rank        INTEGER DEFAULT 0,
            updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- Learning resources assigned to students
        CREATE TABLE IF NOT EXISTS assigned_resources (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id TEXT NOT NULL,
            resource_name TEXT NOT NULL,
            assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed   INTEGER DEFAULT 0
        );

        -- Lecture sessions
        CREATE TABLE IF NOT EXISTS lecture_sessions (
            id          TEXT PRIMARY KEY,
            course_id   TEXT NOT NULL,
            instructor_id TEXT NOT NULL,
            status      TEXT DEFAULT 'scheduled',
            started_at  TEXT,
            ended_at    TEXT,
            summary     TEXT
        );
    """)

    conn.commit()
    _seed_mock_users(cur, conn)
    conn.close()
    logger.info("Database initialized at %s", DB_PATH)


def _seed_mock_users(cur, conn):
    """Insert demo users if the table is empty."""
    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        return

    mock_users = [
        ("student-001", "johndoe",      "Password123!", "john.doe@student.lms.edu",   "student",    "student.lms.edu"),
        ("student-002", "janesmith",    "Password123!", "jane.smith@student.lms.edu", "student",    "student.lms.edu"),
        ("student-003", "ahmedali",     "Password123!", "ahmed.ali@student.lms.edu",  "student",    "student.lms.edu"),
        ("student-004", "ahmed",        "Password123!", "ahmed@student.lms.edu",       "student",    "student.lms.edu"),
        ("inst-001",    "drsara",       "Password123!", "sara@faculty.lms.edu",        "instructor", "faculty.lms.edu"),
        ("inst-002",    "profhassan",   "Password123!", "hassan@faculty.lms.edu",      "instructor", "faculty.lms.edu"),
        ("admin-001",   "systemadmin",  "Admin456!",    "admin@admin.lms.edu",         "admin",      "admin.lms.edu"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO users (id, username, password, email, user_type, email_domain) VALUES (?,?,?,?,?,?)",
        mock_users
    )

    # Seed student profiles
    profiles = [
        ("student-001", "Visual",      "Analytical", "Learn Python and web development", "Intermediate", 250, 3),
        ("student-002", "Auditory",    "Creative",   "Master data science basics",       "Beginner",      80, 1),
        ("student-003", "Kinesthetic", "Active",     "Build mobile apps",                "Advanced",     520, 7),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO student_profiles (student_id, learning_style, personality, learning_goals, experience, total_points, weekly_streak) VALUES (?,?,?,?,?,?,?)",
        profiles
    )
    conn.commit()
    logger.info("Mock users seeded into database")


# ─── User Operations ──────────────────────────────────────────────────────────

def validate_user(username: str, password: str) -> dict | None:
    """Return user dict if credentials valid, else None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?", (username, password)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_profile(student_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT u.*, sp.* FROM users u LEFT JOIN student_profiles sp ON u.id=sp.student_id WHERE u.id=?",
        (student_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_student_profile(student_id: str, data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO student_profiles (student_id, learning_style, personality, learning_goals, experience)
        VALUES (:student_id, :learning_style, :personality, :learning_goals, :experience)
        ON CONFLICT(student_id) DO UPDATE SET
            learning_style = excluded.learning_style,
            personality    = excluded.personality,
            learning_goals = excluded.learning_goals,
            experience     = excluded.experience,
            last_active    = CURRENT_TIMESTAMP
    """, {"student_id": student_id, **data})
    conn.commit()
    conn.close()


# ─── Quiz Operations ──────────────────────────────────────────────────────────

def record_quiz_attempt(student_id: str, quiz_id: str, score: int, difficulty: str,
                         consecutive_correct: int = 0, avg_time: int = 60):
    conn = get_connection()
    conn.execute("""
        INSERT INTO quiz_attempts (student_id, quiz_id, score, difficulty, consecutive_correct, avg_time_seconds)
        VALUES (?,?,?,?,?,?)
    """, (student_id, quiz_id, score, difficulty, consecutive_correct, avg_time))
    conn.commit()
    conn.close()


def get_last_quiz_attempt(student_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM quiz_attempts WHERE student_id=? ORDER BY attempted_at DESC LIMIT 1",
        (student_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Gamification Operations ──────────────────────────────────────────────────

def add_badge(student_id: str, badge_name: str, badge_icon: str, points: int):
    conn = get_connection()
    conn.execute(
        "INSERT INTO badges (student_id, badge_name, badge_icon, points) VALUES (?,?,?,?)",
        (student_id, badge_name, badge_icon, points)
    )
    # Also update total points
    conn.execute(
        "UPDATE student_profiles SET total_points = total_points + ? WHERE student_id = ?",
        (points, student_id)
    )
    conn.commit()
    badge_count = conn.execute("SELECT COUNT(*) FROM badges WHERE student_id=?", (student_id,)).fetchone()[0]
    total_points = conn.execute("SELECT total_points FROM student_profiles WHERE student_id=?", (student_id,)).fetchone()
    conn.close()
    return {"badge_count": badge_count, "total_points": total_points[0] if total_points else points}


def get_total_points(student_id: str) -> int:
    conn = get_connection()
    row = conn.execute("SELECT total_points FROM student_profiles WHERE student_id=?", (student_id,)).fetchone()
    conn.close()
    return row[0] if row else 0


def update_leaderboard(student_id: str, username: str, total_points: int, badge_count: int):
    conn = get_connection()
    conn.execute("""
        INSERT INTO leaderboard (student_id, username, total_points, badge_count, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id) DO UPDATE SET
            total_points = excluded.total_points,
            badge_count  = excluded.badge_count,
            updated_at   = excluded.updated_at
    """, (student_id, username, total_points, badge_count))
    # Recalculate ranks
    conn.execute("""
        UPDATE leaderboard SET rank = (
            SELECT COUNT(*) + 1 FROM leaderboard l2
            WHERE l2.total_points > leaderboard.total_points
        )
    """)
    conn.commit()
    rank = conn.execute("SELECT rank FROM leaderboard WHERE student_id=?", (student_id,)).fetchone()
    conn.close()
    return rank[0] if rank else 1


def get_leaderboard_top(limit: int = 10) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM leaderboard ORDER BY total_points DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Resource Assignment ──────────────────────────────────────────────────────

def assign_resource(student_id: str, resource_type: str, resource_id: str, resource_name: str):
    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO assigned_resources (student_id, resource_type, resource_id, resource_name)
        VALUES (?,?,?,?)
    """, (student_id, resource_type, resource_id, resource_name))
    conn.commit()
    conn.close()
