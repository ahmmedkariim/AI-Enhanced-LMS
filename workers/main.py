"""
AI-Enhanced LMS — Worker Orchestrator
Starts all 6 external task workers in parallel threads.
Each worker subscribes to its topic group and polls Camunda.

Run with:
    cd ai-enhanced-lms
    python -m workers.main

Or directly:
    python workers/main.py
"""
import sys
import time
import signal
import logging
import threading
from datetime import datetime

# ─── Logging Setup (must come before imports that log) ────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("worker.log", mode="a"),
    ]
)
logger = logging.getLogger("lms.main")

# ─── Worker Imports ───────────────────────────────────────────────────────────
from workers.database import init_db
from workers.config import CAMUNDA_URL, AI_MODE, LLM_MODE

# ─── Graceful Shutdown ────────────────────────────────────────────────────────
shutdown_event = threading.Event()

def signal_handler(sig, frame):
    logger.info("⛔ Shutdown signal received — stopping all workers...")
    shutdown_event.set()

signal.signal(signal.SIGINT,  signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# ─── Worker Registry ──────────────────────────────────────────────────────────

WORKERS = [
    {
        "name":   "Authentication Worker",
        "emoji":  "🔐",
        "module": "workers.auth_worker",
        "topics": ["validate-credentials", "init-*-session"],
    },
    {
        "name":   "AI Engine Worker",
        "emoji":  "🤖",
        "module": "workers.ai_engine_worker",
        "topics": ["analyze-*", "assess-*", "get-student-*", "generate-lecture-summary"],
    },
    {
        "name":   "LLM Tutor Worker",
        "emoji":  "🧠",
        "module": "workers.llm_tutor_worker",
        "topics": ["generate-*-quiz", "generate-personalized-*", "generate-*-feedback",
                   "generate-remedial-*", "assign-llm-tutor"],
    },
    {
        "name":   "Gamification Worker",
        "emoji":  "🏆",
        "module": "workers.gamification_worker",
        "topics": ["award-*", "update-points-*", "update-leaderboard",
                   "update-gamification-*", "unlock-*"],
    },
    {
        "name":   "Email Worker",
        "emoji":  "📧",
        "module": "workers.email_worker",
        "topics": ["send-*-email", "send-realtime-*", "notify-*"],
    },
    {
        "name":   "Learning Management Worker",
        "emoji":  "📚",
        "module": "workers.learning_worker",
        "topics": ["create-student-*", "assign-*", "track-*", "update-student-*",
                   "create-quiz-*", "grade-*", "prepare-*"],
    },
]


def run_worker(worker_def: dict):
    """Import and start a single worker module. Runs in its own thread."""
    name   = worker_def["name"]
    module = worker_def["module"]
    try:
        import importlib
        mod = importlib.import_module(module)
        logger.info("%s %s started", worker_def["emoji"], name)
        mod.start()  # Blocking call — runs until process ends
    except Exception as e:
        logger.error("❌ %s crashed: %s", name, str(e), exc_info=True)


def print_banner():
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║         AI-Enhanced LMS — External Task Workers             ║
║         Software Process Engineering (SE396)                ║
╠══════════════════════════════════════════════════════════════╣
║  Camunda Engine : {CAMUNDA_URL:<43}║
║  AI Mode        : {AI_MODE:<43}║
║  LLM Mode       : {LLM_MODE:<43}║
║  Started at     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<43}║
╠══════════════════════════════════════════════════════════════╣
║  Workers: 6 | Topics: 46 total                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_camunda_connection() -> bool:
    """Verify Camunda is reachable before starting workers."""
    try:
        import requests
        resp = requests.get(f"{CAMUNDA_URL}/engine", timeout=5)
        if resp.status_code == 200:
            engines = resp.json()
            engine_name = engines[0].get("name", "default") if engines else "default"
            logger.info("✅ Camunda connected — engine: %s", engine_name)
            return True
        else:
            logger.error("❌ Camunda returned status %d", resp.status_code)
            return False
    except Exception as e:
        logger.error("❌ Cannot connect to Camunda at %s: %s", CAMUNDA_URL, str(e))
        return False


def main():
    print_banner()

    # 1. Initialize database
    logger.info("📦 Initializing database...")
    try:
        init_db()
        logger.info("✅ Database ready")
    except Exception as e:
        logger.error("❌ Database init failed: %s", str(e))
        sys.exit(1)

    # 2. Check Camunda connection
    logger.info("🔌 Connecting to Camunda...")
    if not check_camunda_connection():
        logger.error("Camunda is not reachable. Make sure it is running at %s", CAMUNDA_URL)
        logger.error("Start Camunda: cd camunda && ./start.bat --rest  (Windows)")
        logger.error("              cd camunda && ./start.sh --rest   (Linux/Mac)")
        sys.exit(1)

    # 3. Start all workers in daemon threads
    threads = []
    logger.info("🚀 Starting %d workers...", len(WORKERS))

    for worker_def in WORKERS:
        thread = threading.Thread(
            target=run_worker,
            args=(worker_def,),
            name=worker_def["name"],
            daemon=True,  # dies when main thread exits
        )
        thread.start()
        threads.append(thread)
        time.sleep(0.3)  # stagger startup to avoid race conditions

    logger.info("✅ All workers started and polling Camunda")
    logger.info("📋 Subscribed topics breakdown:")
    for w in WORKERS:
        logger.info("  %s %s → %s", w["emoji"], w["name"], w["topics"])

    logger.info("")
    logger.info("🔍 Monitor processes:   http://localhost:8080/camunda/app/cockpit/")
    logger.info("✅ Complete tasks:      http://localhost:8080/camunda/app/tasklist/")
    logger.info("")
    logger.info("Press Ctrl+C to stop all workers.")

    # 4. Keep main thread alive until shutdown
    try:
        while not shutdown_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    logger.info("👋 Shutting down workers — goodbye!")
    sys.exit(0)


if __name__ == "__main__":
    main()
