# 📸 Phase 5 — Screenshots & Submission Guide

This is your step-by-step checklist to capture all required screenshots
for Eng. Sara's submission.

---

## 🚀 The Exact Order to Follow

### Step 1 — Deploy Everything
```bash
cd AI-Enhanced-LMS
python deploy.py
```
Expected output:
```
✅ learning-path.dmn         → deployment ID: abc123...
✅ gamification-reward.dmn   → deployment ID: def456...
✅ role-assignment.dmn       → deployment ID: ghi789...
✅ quiz-difficulty.dmn       → deployment ID: jkl012...
✅ 01-authentication.bpmn    → Authentication & Role Assignment
✅ 02-onboarding.bpmn        → Student Onboarding Process
...
🎉 All 10 files deployed successfully!
```

---

### Step 2 — Start Workers (keep this terminal open)
```bash
python -m workers.main
```

---

### Step 3 — Run the Demo
```bash
python demo_runner.py
```
Press ENTER at each step while taking screenshots.

---

## 📸 Required Screenshots (minimum 8)

### Screenshot 1: Cockpit — Process List
**URL:** http://localhost:8080/camunda/app/cockpit/default/#/processes

What to capture:
- All 6 BPMN processes listed
- Name, version, instance count visible

**Filename:** `SS1_cockpit_process_list.png`

---

### Screenshot 2: Cockpit — Authentication Process Instance
**How to get it:**
1. Run `python demo_runner.py` — it starts the auth process
2. Open Cockpit → Processes → "Authentication and Role Assignment"
3. Click the running/completed instance
4. You'll see the **highlighted path** (green = completed, blue = active)

What to capture:
- Full BPMN diagram with highlighted path
- Variables panel on the right (username, role, sessionId)

**Filename:** `SS2_cockpit_auth_instance.png`

---

### Screenshot 3: Cockpit — DMN Evaluation
**How to get it:**
1. Cockpit → Decisions tab
2. Click "Determine Learning Path" or "Role Assignment Decision"
3. You'll see the decision table with recent evaluation results

What to capture:
- DMN table with input/output columns
- Recent evaluation in the history tab

**Filename:** `SS3_cockpit_dmn_evaluation.png`

---

### Screenshot 4: Tasklist — Available User Tasks
**URL:** http://localhost:8080/camunda/app/tasklist/

How to get tasks showing:
1. Keep workers running
2. Start a process from Tasklist (click "Start process" top right)
3. Select "Authentication and Role Assignment"
4. The "Enter Credentials" task appears in the list

What to capture:
- Task list showing "Enter Credentials" task
- Task assignee, process name visible

**Filename:** `SS4_tasklist_tasks.png`

---

### Screenshot 5: Tasklist — Filling a Form
**How:**
1. In Tasklist, click "Enter Credentials" task
2. The embedded form appears on the right
3. Fill in: username=johndoe, password=Password123!

What to capture:
- Form with all fields filled in
- "Complete" button visible

**Filename:** `SS5_tasklist_form.png`

---

### Screenshot 6: Terminal — Workers Running
What to capture:
- Terminal showing all 6 workers started
- Worker log lines showing tasks being processed:
```
🔐 Auth task received: topic=validate-credentials
✅ Login valid: ahmed → student-004
📧 [MOCK EMAIL] To: ahmed@student.lms.edu
✅ Student session created
```

**Filename:** `SS6_terminal_workers.png`

---

### Screenshot 7: Cockpit — Parallel Gateway in Action
**How:**
1. Start the Onboarding process
2. Complete "Submit Learning Goals" in Tasklist
3. Open Cockpit → the parallel gateway lights up

What to capture:
- Both parallel branches highlighted
- AI Engine tasks visible

**Filename:** `SS7_cockpit_parallel_gateway.png`

---

### Screenshot 8: Cockpit — Gamification Process Completed
**How:**
1. Run `python demo_runner.py` — it runs gamification automatically
2. After demo, open Cockpit → Gamification process
3. Click a completed instance

What to capture:
- Full gamification BPMN highlighted
- Inclusive gateway showing 3 branches fired

**Filename:** `SS8_cockpit_gamification_complete.png`

---

## 🎬 Optional: Record a Demo Video (Bonus marks)

Use any screen recorder (OBS, ShareX, Windows Game Bar Win+G):

Script to follow:
1. Show Cockpit with all 6 processes deployed
2. Go to Tasklist → Start "Authentication and Role Assignment"
3. Fill form → Complete
4. Switch to worker terminal → show logs processing
5. Back to Cockpit → click instance → show highlighted path
6. Click on a variable → show roleResult from DMN
7. Go to Decisions tab → show DMN table

Duration: 3-5 minutes is ideal.

---

## ✅ Final Submission ZIP Contents

```
AI-Enhanced-LMS-Submission/
├── bpmn/
│   ├── 01-authentication.bpmn
│   ├── 02-onboarding.bpmn
│   ├── 03-adaptive-learning.bpmn
│   ├── 04-hybrid-classroom.bpmn
│   ├── 05-adaptive-quiz.bpmn
│   └── 06-gamification.bpmn
├── dmn/
│   ├── learning-path.dmn
│   ├── gamification-reward.dmn
│   ├── role-assignment.dmn
│   └── quiz-difficulty.dmn
├── workers/                  ← Python source code
├── screenshots/              ← All 8+ screenshots
├── docs/
│   ├── Report.docx           ← Phase 6
│   └── Presentation.pptx     ← Phase 6
├── deploy.py
├── test_e2e.py
├── demo_runner.py
├── requirements.txt
└── README.md
```

---

## 🧾 Mock Users Reference

| Username | Password | Role | Email |
|---|---|---|---|
| ahmed | Password123! | Student | ahmed@student.lms.edu |
| johndoe | Password123! | Student | john.doe@student.lms.edu |
| janesmith | Password123! | Student | jane.smith@student.lms.edu |
| ahmedali | Password123! | Student | ahmed.ali@student.lms.edu |
| drsara | Password123! | Instructor | sara@faculty.lms.edu |
| profhassan | Password123! | Instructor | hassan@faculty.lms.edu |
| systemadmin | Admin456! | Admin | admin@admin.lms.edu |

---

## 🆘 Quick Troubleshooting

| Problem | Fix |
|---|---|
| Deploy fails | Make sure Camunda is running first |
| Worker crashes | Replace workers/ folder with latest ZIP |
| Login fails | Delete data/lms.db and restart workers |
| No tasks in Tasklist | Deploy BPMN first via deploy.py |
| Process stuck | Check worker terminal for errors |
| DMN not found | Deploy DMN files before BPMN files |
