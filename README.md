# 🎓 AI-Enhanced LMS with Hybrid Learning, DMN & Executable BPMN

![Camunda](https://img.shields.io/badge/Camunda-7%20Community-orange)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)

> **Course:** Software Process Engineering (SE396 / CSE4401)
> **Platform:** Camunda 7 Community Edition + Python

An executable BPMN-based Learning Management System featuring adaptive learning paths, LLM-generated quizzes, gamification, DMN decisions, and hybrid classroom engagement.

> 📖 **New to Git/GitHub?** See [`docs/GITHUB_SETUP.md`](docs/GITHUB_SETUP.md) for step-by-step instructions.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              CAMUNDA PLATFORM (localhost:8080)              │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │ Engine  │  │ Cockpit  │  │ Tasklist │  │ DMN Engine  │  │
│  └─────────┘  └──────────┘  └──────────┘  └─────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (External Tasks)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PYTHON WORKERS (External Tasks)                │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────┐  │
│  │ AI Engine│ │LLM Tutor │ │Gamification│ │Email Service│  │
│  └──────────┘ └──────────┘ └────────────┘ └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

- **Java 17+** (for Camunda)
- **Python 3.10+**
- **Camunda Modeler** (desktop app for BPMN/DMN design)
- **Camunda Platform 7 Run** (the engine)

---

## 🚀 Setup Instructions

### Step 1: Install Camunda Modeler
Download from: https://camunda.com/download/modeler/

Used to design BPMN diagrams and DMN tables.

### Step 2: Install Camunda Platform 7 Run

Download "Camunda Platform 7 Run" (Community) from:
https://camunda.com/download/

Extract the ZIP file to a location like:
- **Windows:** `C:\camunda\`
- **Linux/Mac:** `~/camunda/`

### Step 3: Start Camunda

**Windows:**
```bash
cd C:\camunda
start.bat --rest
```

**Linux/Mac:**
```bash
cd ~/camunda
./start.sh --rest
```

This starts Camunda on **http://localhost:8080**

Default login: `demo` / `demo`

You'll see:
- **Cockpit:** http://localhost:8080/camunda/app/cockpit/
- **Tasklist:** http://localhost:8080/camunda/app/tasklist/
- **Admin:** http://localhost:8080/camunda/app/admin/

### Step 4: Install Python Dependencies

```bash
cd ai-enhanced-lms
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (especially Gmail credentials)
```

### Step 6: Run Python Workers

```bash
python -m workers.main
```

You'll see workers polling Camunda for external tasks.

### Step 7: Deploy BPMN/DMN Files

In **Camunda Modeler**:
1. Open any `.bpmn` or `.dmn` file from this project
2. Click the **"Deploy"** button (rocket icon)
3. Set Endpoint URL: `http://localhost:8080/engine-rest`
4. Click **Deploy**

---

## 📁 Project Structure

```
ai-enhanced-lms/
├── bpmn/                  # 6 BPMN executable diagrams
│   ├── 01-authentication.bpmn
│   ├── 02-onboarding.bpmn
│   ├── 03-adaptive-learning.bpmn
│   ├── 04-hybrid-classroom.bpmn
│   ├── 05-adaptive-quiz.bpmn
│   └── 06-gamification.bpmn
├── dmn/                   # 4 DMN decision tables
│   ├── learning-path.dmn
│   ├── gamification-reward.dmn
│   ├── role-assignment.dmn
│   └── quiz-difficulty.dmn
├── forms/                 # Camunda forms (JSON)
├── workers/               # Python external task workers
│   ├── ai_engine_worker.py
│   ├── llm_tutor_worker.py
│   ├── gamification_worker.py
│   ├── email_worker.py
│   └── main.py            # Worker orchestrator
├── api/                   # FastAPI for custom endpoints
├── data/                  # SQLite DB + mock data
├── docs/                  # Final report + diagrams
├── screenshots/           # Cockpit/Tasklist screenshots
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🎯 Demo Flow (End-to-End)

1. **Start a process** in Tasklist → Authentication
2. **Login** with credentials → role assigned via DMN
3. **Submit learning goals** → AI analyzes profile (parallel with LLM generation)
4. **Adaptive Learning Path** assigned via DMN 1
5. **Hybrid Lecture** → live quiz, team challenge, polls
6. **Adaptive Quiz** generated by LLM
7. **Gamification** rewards calculated via DMN 2
8. **Email notification** sent
9. **View execution** in Cockpit

---

## 🧠 DMN Decision Tables

| # | Table | Purpose |
|---|---|---|
| 1 | Learning Path Decision | Score + Style + Engagement → Path |
| 2 | Gamification Reward | Activity + Performance → Reward |
| 3 | Role Assignment | Username → Role |
| 4 | Quiz Difficulty | Past Score → Next Difficulty |

---

## 🚀 Innovation Feature

**Smart Engagement Detection + AI-Powered Lecture Games**
- AI monitors student response time/correctness during live quizzes
- Detects engagement drops → triggers AI-generated lecture games
- Dynamic difficulty adjustment based on real-time performance

---

## 📦 Deliverables Checklist

- [ ] 6 BPMN files (executable on Camunda)
- [ ] 4 DMN tables
- [ ] Camunda Forms for all User Tasks
- [ ] Python worker backend
- [ ] Email integration (Gmail)
- [ ] Cockpit screenshots
- [ ] Tasklist screenshots
- [ ] Final Report (Word doc)
- [ ] Presentation (PowerPoint)
