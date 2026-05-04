"""
Gamification Worker
Handles: award-premium-badge, award-standard-badge, award-participation-points,
         award-completion-badge, award-points, update-points-balance,
         update-leaderboard, update-gamification-analytics, unlock-special-achievement
"""
import logging
import random
from datetime import datetime
from camunda.external_task.external_task_worker import ExternalTaskWorker
from workers.config import CAMUNDA_URL, WORKER_CONFIG, WORKER_IDS, GAMIFICATION_TOPICS
from workers.database import (add_badge, get_total_points, update_leaderboard,
                                get_leaderboard_top, get_student_profile)

logger = logging.getLogger("lms.gamification")


# ─── Badge Definitions ────────────────────────────────────────────────────────

PREMIUM_BADGES = {
    "Gold Badge - Quiz Master":     {"icon": "trophy_gold",    "points": 100, "tier": "gold"},
    "AI Game Champion Trophy":      {"icon": "robot_gold",     "points": 120, "tier": "gold"},
    "Team Champion Trophy":         {"icon": "crown_team",     "points": 200, "tier": "platinum"},
    "Hidden Discovery Badge":       {"icon": "compass_gold",   "points": 75,  "tier": "gold"},
    "Quick Thinker Badge":          {"icon": "lightning",      "points": 60,  "tier": "silver"},
}

STANDARD_BADGES = {
    "Silver Badge - Quiz Achiever": {"icon": "medal_silver",   "points": 50,  "tier": "silver"},
    "Team Player Badge":            {"icon": "shield_team",    "points": 150, "tier": "silver"},
    "Collaboration Reward":         {"icon": "handshake",      "points": 100, "tier": "silver"},
    "Active Contributor Badge":     {"icon": "chat_active",    "points": 80,  "tier": "silver"},
    "Curious Mind Badge":           {"icon": "compass_silver", "points": 40,  "tier": "bronze"},
    "Live Participation Badge":     {"icon": "target",         "points": 25,  "tier": "bronze"},
}

SPECIAL_ACHIEVEMENTS = {
    "100 Points Club":      {"icon": "star_100",    "points": 50,  "threshold": 100},
    "Weekly Champion":      {"icon": "calendar_7",  "points": 75,  "threshold_streak": 7},
    "Quiz Marathon":        {"icon": "fire_streak", "points": 100, "threshold_streak": 5},
    "Top of the Class":     {"icon": "podium_1st",  "points": 200, "rank_threshold": 3},
}


def handle_gamification_task(task):
    """Route gamification tasks by topic name."""
    topic = task.get_topic_name()
    logger.info("🏆 Gamification task: topic=%s | pid=%s", topic, task.get_process_instance_id())

    try:
        student_id   = task.get_variable("userId") or task.get_variable("studentId") or "unknown"
        username     = task.get_variable("username") or student_id
        reward_type  = ""

        # Extract rewardResult from DMN if present
        reward_result = task.get_variable("rewardResult")
        if reward_result and isinstance(reward_result, dict):
            reward_type    = reward_result.get("rewardType", "")
            points_awarded = int(reward_result.get("pointsAwarded", 10))
            badge_icon     = reward_result.get("badgeIcon", "star_basic")
        else:
            reward_type    = task.get_variable("rewardType") or ""
            points_awarded = int(task.get_variable("pointsAwarded") or 10)
            badge_icon     = task.get_variable("badgeIcon") or "star_basic"

        if topic == "award-premium-badge":
            result = _award_badge(student_id, username, reward_type or "Gold Badge - Quiz Master",
                                   badge_icon, points_awarded, "premium")

        elif topic == "award-standard-badge":
            result = _award_badge(student_id, username, reward_type or "Silver Badge - Quiz Achiever",
                                   badge_icon, points_awarded, "standard")

        elif topic in ("award-participation-points", "award-points"):
            result = _award_points(student_id, username, points_awarded or 10)

        elif topic == "award-completion-badge":
            result = _award_badge(student_id, username, "Course Completion Badge",
                                   "graduation_cap", 150, "premium")

        elif topic == "update-points-balance":
            result = _update_points_balance(student_id, points_awarded)

        elif topic == "update-leaderboard":
            result = _refresh_leaderboard(student_id, username)

        elif topic == "update-gamification-analytics":
            result = _update_analytics(student_id)

        elif topic == "unlock-special-achievement":
            total_pts = get_total_points(student_id)
            profile = get_student_profile(student_id)
            streak = profile.get("weekly_streak", 0) if profile else 0
            result = _unlock_achievement(student_id, username, total_pts, streak)

        else:
            logger.warning("Unknown gamification topic: %s", topic)
            result = {"status": "completed"}

        # Ensure totalPoints and weeklyStreak are always returned to the process instance
        if isinstance(result, dict):
            if "totalPoints" not in result:
                result["totalPoints"] = get_total_points(student_id)
            if "weeklyStreak" not in result:
                profile = get_student_profile(student_id)
                result["weeklyStreak"] = profile.get("weekly_streak", 0) if profile else 0

        logger.info("✅ Gamification complete: %s → %s", topic, result)
        return task.complete(result)

    except Exception as e:
        logger.error("Gamification task failed [%s]: %s", topic, str(e), exc_info=True)
        return task.failure(
            error_message=f"Gamification error: {str(e)}",
            error_details=str(e),
            retries=2,
            retry_timeout=3000
        )


def _award_badge(student_id: str, username: str, badge_name: str,
                  badge_icon: str, points: int, tier: str) -> dict:
    """Add a badge to student's record and update their points."""
    db_result = add_badge(student_id, badge_name, badge_icon, points)
    total_points = db_result["total_points"]
    badge_count = db_result["badge_count"]

    logger.info("🏅 Badge awarded: %s → %s (+%d pts)", username, badge_name, points)

    # Refresh leaderboard entry
    rank = update_leaderboard(student_id, username, total_points, badge_count)

    return {
        "badgeAwarded":     True,
        "badgeName":        badge_name,
        "badgeIcon":        badge_icon,
        "badgeTier":        tier,
        "pointsAwarded":    points,
        "totalPoints":      total_points,
        "badgeCount":       badge_count,
        "currentRank":      rank,
        "awardedAt":        datetime.utcnow().isoformat(),
    }


def _award_points(student_id: str, username: str, points: int) -> dict:
    """Award participation points without a badge."""
    db_result = add_badge(student_id, "Participation Points", "star_basic", points)
    total_points = db_result["total_points"]

    logger.info("⭐ Points awarded: %s → +%d pts (total: %d)", username, points, total_points)

    return {
        "badgeAwarded":  False,
        "pointsAwarded": points,
        "totalPoints":   total_points,
        "awardedAt":     datetime.utcnow().isoformat(),
    }


def _update_points_balance(student_id: str, points_to_add: int) -> dict:
    """Update points balance and return new total."""
    db_result = add_badge(student_id, "_points_update", "none", points_to_add)
    total = db_result["total_points"]
    logger.info("💰 Points balance updated: student=%s +%d → total=%d", student_id, points_to_add, total)
    return {"totalPoints": total, "pointsAdded": points_to_add}


def _refresh_leaderboard(student_id: str, username: str) -> dict:
    """Recalculate leaderboard ranking for this student."""
    total_points = get_total_points(student_id)
    profile = get_student_profile(student_id)
    badge_count = 0  # simplified

    rank = update_leaderboard(student_id, username, total_points, badge_count)
    top_10 = get_leaderboard_top(10)

    logger.info("📊 Leaderboard updated: %s is rank #%d with %d pts", username, rank, total_points)

    return {
        "currentRank":    rank,
        "totalPoints":    total_points,
        "leaderboardTop": str(top_10[:3]),  # Top 3 as string for process variable
        "updatedAt":      datetime.utcnow().isoformat(),
    }


def _update_analytics(student_id: str) -> dict:
    """Update gamification analytics for AI learning optimization."""
    total_points = get_total_points(student_id)
    engagement_score = min(100, total_points // 5 + random.randint(10, 30))

    return {
        "analyticsUpdated":    True,
        "engagementScore":     engagement_score,
        "gamificationHealth":  "Excellent" if engagement_score > 70 else "Good" if engagement_score > 40 else "Needs Attention",
        "updatedAt":           datetime.utcnow().isoformat(),
    }


def _unlock_achievement(student_id: str, username: str, total_points: int, streak: int) -> dict:
    """Check and unlock any special milestone achievements."""
    unlocked = []

    if total_points >= 500:
        unlocked.append({"name": "500 Points Legend", "icon": "star_500", "points": 100})
    elif total_points >= 100:
        unlocked.append({"name": "100 Points Club", "icon": "star_100", "points": 50})

    if streak >= 7:
        unlocked.append({"name": "Weekly Champion", "icon": "calendar_7", "points": 75})
    elif streak >= 5:
        unlocked.append({"name": "Quiz Marathon", "icon": "fire_streak", "points": 50})

    for achievement in unlocked:
        add_badge(student_id, achievement["name"], achievement["icon"], achievement["points"])
        logger.info("🌟 Special achievement unlocked: %s → %s", username, achievement["name"])

    return {
        "achievementsUnlocked": len(unlocked),
        "achievementNames":     ",".join(a["name"] for a in unlocked) if unlocked else "none",
        "bonusPoints":          sum(a["points"] for a in unlocked),
        "unlockedAt":           datetime.utcnow().isoformat(),
    }


def start():
    """Start the gamification worker — called by main.py."""
    logger.info("🚀 Gamification worker starting | Topics: %s", GAMIFICATION_TOPICS)
    worker = ExternalTaskWorker(
        worker_id=WORKER_IDS["gamification"],
        base_url=CAMUNDA_URL,
        config=WORKER_CONFIG
    )
    worker.subscribe(GAMIFICATION_TOPICS, handle_gamification_task)
