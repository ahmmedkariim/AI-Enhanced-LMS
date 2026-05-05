# 🎓 AI-Enhanced LMS with Hybrid Learning, DMN & Executable BPMN

![Camunda](https://img.shields.io/badge/Camunda-7%20Community-orange)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![BPMN](https://img.shields.io/badge/BPMN%20Diagrams-6-purple)
![DMN](https://img.shields.io/badge/DMN%20Tables-4-teal)
![Forms](https://img.shields.io/badge/Camunda%20Forms-11-green)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

> **Course:** Software Process Engineering (SE396 / CSE4401)  
> **Supervisor:** Eng. Sara Elshorbagy  
> **Platform:** Camunda 7 Community Edition + Python 3.12

An **executable BPMN-based Learning Management System** featuring adaptive learning paths, LLM-generated quizzes, gamification, DMN-driven decisions, hybrid classroom engagement, and a complete Python worker backend — all running live on Camunda Platform 7.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                CAMUNDA PLATFORM 7 (localhost:8080)             │
│                                                                │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│   │  Engine  │   │ Cockpit  │   │ Tasklist │   │   DMN    │  │
│   │  (core)  │   │(monitor) │   │  (tasks) │   │ (rules)  │  │
│   └──────────┘   └──────────┘   └──────────┘   └──────────┘  │
└────────────────────────┬───────────────────────────────────────┘
                         │  REST API  (External Task Pattern)
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
┌──────────────────────────────────────────────────────────────┐
│              PYTHON WORKERS  (6 workers, 46 topics)          │
│                                                              │
│  🔐 Auth     🤖 AI Engine   🧠 LLM Tutor   🏆 Gamification  │
│  📧 Email    📚 Learning Management                          │
└──────────────────────────────────────────────────────────────┘
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
      SQLite DB      Mock AI/LLM    Gmail SMTP
      (lms.db)       Responses      (email)
```

---

## 📦 Project Deliverables — Alvenv\Scripts\activatel Complete

| # | Deliverable | Files | Status |
|---|---|---|---|
| 1 | **BPMN Diagrams** | `bpmn/01` → `bpmn/06` | ✅ 6 diagrams |
| 2 | **DMN Tables** | `dmn/*.dmn` | ✅ 4 tables, 52 rules |
| 3 | **Camunda Forms** | `forms/*.form` | ✅ 11 forms |
| 4 | **Python Workers** | `workers/*.py` | ✅ 6 workers, 46 topics |
| 5 | **Email Integration** | `workers/email_service.py` | ✅ Gmail SMTP + 5 templates |
| 6 | **Database** | `workers/database.py` | ✅ SQLite with mock users |
| 7 | **Deploy Script** | `deploy.py` | ✅ Auto-deploys everything |
| 8 | **E2E Tests** | `test_e2e.py` | ✅ 4 process tests |
| 9 | **Demo Runner** | `demo_runner.py` | ✅ Interactive live demo |
| 10 | **Camunda User Setup** | `setup_camunda_users.py` | ✅ Creates 7 users + 3 groups |

---

## 🗺️ BPMN Diagrams (6 Executable Processes)

| # | File | Process Name | Swim Lanes | Key Elements |
|---|---|---|---|---|
| 1 | `01-authentication.bpmn` | Authentication & Role Assignment | User, LMS | XOR × 2, DMN 3, Email |
| 2 | `02-onboarding.bpmn` | Student Onboarding | Student, LMS, AI | Parallel + Inclusive |
| 3 | `03-adaptive-learning.bpmn` | Adaptive Learning Process | Student, LMS, AI, LLM | Event-Based, DMN 1 |
| 4 | `04-hybrid-classroom.bpmn` | Hybrid Classroom Process | Student, Instructor, LMS, AI, Physical | All 4 gateway types |
| 5 | `05-adaptive-quiz.bpmn` | Adaptive Quiz Generation | Student, LMS, LLM, AI | Parallel, DMN 4 |
| 6 | `06-gamification.bpmn` | Gamification & Reward Process | Student, LMS, Engine | Inclusive, DMN 2 |

### Gateway Coverage

| Gateway Type | Used In |
|---|---|
| **Exclusive (XOR)** | All 6 diagrams |
| **Parallel (AND)** | Diagrams 2, 3, 4, 5 |
| **Inclusive (OR)** | Diagrams 2, 3, 4, 6 |
| **Event-Based** | Diagrams 3 and 4 |

---

## 🧠 DMN Decision Tables (4 Tables, 52 Rules)

| # | File | Decision ID | Inputs | Outputs | Rules | Called By |
|---|---|---|---|---|---|---|
| 1 | `learning-path.dmn` | `LearningPathDecision` | Score, Style, Engagement | Path, Priority, Resources | 16 | BPMN 3 |
| 2 | `gamification-reward.dmn` | `GamificationRewardDecision` | Activity, Performance, Collaboration | Reward, Points, Badge | 17 | BPMN 6 |
| 3 | `role-assignment.dmn` | `RoleAssignmentDecision` | UserType, Domain, ValidCreds | Role, Dashboard, Permissions | 10 | BPMN 1 |
| 4 | `quiz-difficulty.dmn` | `QuizDifficultyDecision` | Score, Streak, AvgTime | Difficulty, Questions, Hints | 9 | BPMN 5 |

---

## 🖊️ Camunda Forms (11 Forms)

| Form File | User Task | Process |
|---|---|---|
| `enter-credentials.form` | Enter Credentials | Authentication |
| `show-error.form` | Show Error Message | Authentication |
| `submit-learning-goals.form` | Submit Learning Goals | Onboarding |
| `review-profile.form` | Review Learning Profile | Onboarding |
| `access-learning-materials.form` | Access Learning Materials | Adaptive Learning |
| `start-lecture.form` | Start Lecture Session | Hybrid Classroom |
| `live-poll.form` | Participate in Live Poll | Hybrid Classroom |
| `team-challenge.form` | Join Team Challenge | Hybrid Classroom |
| `post-lecture-quiz.form` | Complete Post-Lecture Quiz | Hybrid Classroom |
| `take-adaptive-quiz.form` | Take Adaptive Quiz | Adaptive Quiz |
| `view-achievement.form` | View Achievement | Gamification |

---

## 🐍 Python Workers (6 Workers, 46 Topics)

| Worker | File | Topics |
|---|---|---|
| 🔐 Authentication | `auth_worker.py` | `validate-credentials`, `init-*-session` |
| 🤖 AI Engine | `ai_engine_worker.py` | `analyze-*`, `assess-*`, `get-student-*` |
| 🧠 LLM Tutor | `llm_tutor_worker.py` | `generate-*-quiz`, `generate-*-feedback` |
| 🏆 Gamification | `gamification_worker.py` | `award-*`, `update-*`, `unlock-*` |
| 📧 Email | `email_worker.py` | `send-*-email`, `notify-*` |
| 📚 Learning | `learning_worker.py` | `create-*`, `assign-*`, `grade-*` |

---

## 🚀 Quick Start (5 Steps)

### Prerequisites
- Java 17+ (for Camunda engine)
- Python 3.10+
- [Camunda Platform 7 Run](https://camunda.com/download/) — Community Edition
- [Camunda Modeler](https://camunda.com/download/modeler/) — for viewing BPMN/DMN/Forms

---

### Step 1 — Start Camunda

**Windows:**
```bash
cd C:\camunda-run
start.bat --rest
```
**Mac / Linux:**
```bash
cd ~/camunda-run
./start.sh --rest
```

Wait for the Spring Boot banner, then open:
- **Cockpit** → http://localhost:8080/camunda/app/cockpit/
- **Tasklist** → http://localhost:8080/camunda/app/tasklist/
- Default admin login: `demo` / `demo`
- LMS user logins are created by `python setup_camunda_users.py` (see Mock Users below)

---

### Step 2 — Install Python Dependencies

```bash
cd AI-Enhanced-LMS
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

---

### Step 3 — Deploy Everything to Camunda

```bash
cp .env.example .env    # configure if needed
python deploy.py        # deploys all 4 DMN + 6 BPMN automatically
```

Expected output:
```
✅ learning-path.dmn          deployed
✅ gamification-reward.dmn    deployed
✅ role-assignment.dmn        deployed
✅ quiz-difficulty.dmn        deployed
✅ 01-authentication.bpmn     deployed
✅ 02-onboarding.bpmn         deployed
✅ 03-adaptive-learning.bpmn  deployed
✅ 04-hybrid-classroom.bpmn   deployed
✅ 05-adaptive-quiz.bpmn      deployed
✅ 06-gamification.bpmn       deployed
🎉 All 10 files deployed successfully!
```

---

### Step 4 — Create Camunda Users (one-time)

```bash
python setup_camunda_users.py
```

This creates 7 LMS users + 3 groups (`students`, `instructors`, `admins`) and grants Tasklist/Cockpit access. Re-runs are idempotent.

> **Note:** Camunda's default resource ID validator rejects underscores, so user IDs use **hyphens** (e.g. `john-doe`, `dr-sara`). Passwords meet the default policy (≥10 chars, upper/lower/digit/special).

---

### Step 5 — Start Workers

Open a **second terminal**:
```bash
python -m workers.main
```

All 6 workers start and poll Camunda every 5 seconds. Go to **Tasklist → Start process** and pick any process.

---

## 🎬 Demo & Testing Scripts

```bash
python demo_runner.py   # Interactive step-by-step demo (press ENTER each step)
python test_e2e.py      # Automated end-to-end test of 4 processes
python diagnose.py      # Checks Camunda connection, packages, files
```

---

## 🗂️ Project Structure

```
AI-Enhanced-LMS/
│
├── bpmn/                           # 6 Executable BPMN diagrams
│   ├── 01-authentication.bpmn
│   ├── 02-onboarding.bpmn
│   ├── 03-adaptive-learning.bpmn
│   ├── 04-hybrid-classroom.bpmn
│   ├── 05-adaptive-quiz.bpmn
│   └── 06-gamification.bpmn
│
├── dmn/                            # 4 DMN Decision Tables (52 rules)
│   ├── learning-path.dmn
│   ├── gamification-reward.dmn
│   ├── role-assignment.dmn
│   └── quiz-difficulty.dmn
│
├── forms/                          # 11 Camunda Forms (.form JSON)
│   ├── enter-credentials.form
│   ├── submit-learning-goals.form
│   ├── take-adaptive-quiz.form
│   └── ...                         # 8 more forms
│
├── workers/                        # Python External Task Workers
│   ├── main.py                     # Orchestrator — starts all 6 workers
│   ├── config.py                   # Settings + 46 topic definitions
│   ├── database.py                 # SQLite DB — users, quizzes, badges
│   ├── email_service.py            # Gmail SMTP + 5 HTML email templates
│   ├── auth_worker.py              # Login validation + session setup
│   ├── ai_engine_worker.py         # Learning style + engagement analysis
│   ├── llm_tutor_worker.py         # Quiz generation + personalized feedback
│   ├── gamification_worker.py      # Badges + leaderboard + points
│   ├── email_worker.py             # All notification email topics
│   └── learning_worker.py          # Profile, resources, quiz grading
│
├── data/                           # Created at runtime (gitignored)
│   └── lms.db                      # SQLite database
│
├── docs/
│   ├── PROJECT_REQUIREMENTS.md     # Full project spec
│   ├── PHASE5_SCREENSHOT_GUIDE.md  # Submission screenshot checklist
│   └── GITHUB_SETUP.md             # Git/GitHub setup guide
│
├── screenshots/                    # Put your submission screenshots here
│
├── deploy.py                       # Auto-deploys DMN + BPMN to Camunda
├── test_e2e.py                     # End-to-end integration tests
├── demo_runner.py                  # Interactive live demo
├── diagnose.py                     # Startup health checker
├── requirements.txt
├── .env.example
└── README.md
```

---

## 👥 Mock Users

Created by `python setup_camunda_users.py` (and seeded into the LMS DB by the workers on first run).

| Username | Password | Role | Group |
|---|---|---|---|
| `ahmed` | `Password123!` | Student | `students` |
| `john-doe` | `Password123!` | Student | `students` |
| `jane-smith` | `Password123!` | Student | `students` |
| `ahmed-ali` | `Password123!` | Student | `students` |
| `dr-sara` | `Password123!` | Instructor | `instructors` |
| `prof-hassan` | `Password123!` | Instructor | `instructors` |
| `system-admin` | `Admin456!` | Admin | `admins` |

> **Why hyphens?** Camunda's default `GeneralResourceWhitelistPattern` doesn't allow underscores in user/group IDs. The same hyphenated IDs are used for both Camunda authentication and the LMS internal DB (`workers/database.py`).

---

## 🎯 End-to-End Flow

```
1.  python deploy.py            Deploy 4 DMN + 6 BPMN to Camunda
2.  python -m workers.main      Start 6 Python workers (keep open)
3.  Tasklist → Start process    Pick "Authentication and Role Assignment"
4.  Fill form                   username: ahmed | password: Password123!
5.  Watch terminal              Worker validates → DMN assigns STUDENT role
6.  Cockpit                     See highlighted process path (green = done)
7.  Tasklist → Start process    Pick "Gamification and Reward Process"
8.  Workers run DMN 2           Gold badge + 100 points calculated
9.  View Achievement form       Student acknowledges reward
10. Cockpit                     See Inclusive Gateway path highlighted
```

---

## 🌟 Innovation Feature

**Smart Engagement Detection + AI-Powered Lecture Games** (in `04-hybrid-classroom.bpmn`):
- AI monitors response time and quiz correctness in real-time during lectures
- **Event-Based Gateway** watches for student response OR timeout event
- Engagement drop automatically triggers AI-generated interactive games
- DMN 1 adjusts the post-lecture learning path based on live engagement score

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| Workers crash immediately | Run `python diagnose.py` — pinpoints the exact issue |
| `Login failed` for your user | Delete `data/lms.db` and restart workers (re-seeds DB) |
| Camunda rejects user ID (`invalid id`) | Use hyphens, not underscores — `john-doe`, not `john_doe` |
| Camunda rejects password | Default policy requires ≥10 chars + upper + lower + digit + special |
| `${initiator}` cannot be resolved | Add `camunda:initiator="initiator"` to the start event |
| No tasks in Tasklist | Run `python deploy.py` first |
| DMN not found error | `deploy.py` deploys DMN before BPMN — always use it |
| `NoneType get_task` error | All `task.complete()` calls need `return` before them |
| Email not sending | Set `EMAIL_MODE=mock` in `.env` — no Gmail needed for demo |
| Camunda unreachable | Start `start.bat --rest` and wait 30s for Spring Boot |

---

## 📸 Screenshots for Submission

See [`docs/PHASE5_SCREENSHOT_GUIDE.md`](docs/PHASE5_SCREENSHOT_GUIDE.md) for the full 8-screenshot checklist.

---

## 📖 More Documentation

- [`docs/GITHUB_SETUP.md`](docs/GITHUB_SETUP.md) — Push this project to GitHub step by step
- [`docs/PROJECT_REQUIREMENTS.md`](docs/PROJECT_REQUIREMENTS.md) — Original course spec
- [`dmn/README.md`](dmn/README.md) — DMN test cases and deployment guide
- [`bpmn/README.md`](bpmn/README.md) — BPMN diagram details and variable contracts

---

## 📄 License

MIT — Academic project for Software Process Engineering (SE396 / CSE4401).
