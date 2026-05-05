# 🎨 BPMN Executable Diagrams

This folder contains **6 executable BPMN diagrams** for the AI-Enhanced LMS project.

---

## 📊 Diagram Index

| # | File | Status | Description |
|---|---|---|---|
| 1 | `01-authentication.bpmn` | ✅ Done | Login & role-based routing |
| 2 | `02-onboarding.bpmn` | 🔜 Pending | Student onboarding & profile creation |
| 3 | `03-adaptive-learning.bpmn` | 🔜 Pending | AI-driven personalized learning paths |
| 4 | `04-hybrid-classroom.bpmn` | 🔜 Pending | Before/During/After lecture process |
| 5 | `05-adaptive-quiz.bpmn` | 🔜 Pending | LLM-generated adaptive quizzes |
| 6 | `06-gamification.bpmn` | 🔜 Pending | Reward calculation & notification |

---

## 🔐 Diagram 1: Authentication & Role Assignment

### What It Does
Handles user login, validates credentials, and routes users to their role-specific dashboard.

### Elements Used
| Element | Count | Where |
|---|---|---|
| Start Event | 1 | "Login Request" trigger |
| User Tasks | 2 | Enter Credentials, Show Error |
| Service Tasks | 5 | Validate, SendEmail, 3 Init Sessions |
| Business Rule Task | 1 | Determine Role (calls DMN 3) |
| Exclusive Gateways | 2 | Credentials Valid?, Which Role? |
| End Events | 4 | Student/Instructor/Admin/Denied |
| Sequence Flows | 15 | All connections |
| Lanes | 2 | User, LMS System |

### Process Variables

**Inputs (set during Enter Credentials):**
- `username` (string) — required, min 3 chars
- `password` (string) — required, min 6 chars
- `userType` (string) — "student", "instructor", "admin"
- `emailDomain` (string) — e.g., "student.lms.edu"

**Set by Service Tasks:**
- `credentialsValid` (boolean) — set by `validate-credentials` worker
- `userId` (string) — set by validation worker

**Set by Business Rule Task (DMN 3):**
- `roleResult.assignedRole` (string)
- `roleResult.dashboardRoute` (string)
- `roleResult.permissions` (string)
- `roleResult.accessGranted` (boolean)

### External Task Topics
The Python workers must subscribe to these topics:

| Topic | Purpose | Returns |
|---|---|---|
| `validate-credentials` | Check username/password | `credentialsValid: boolean`, `userId: string` |
| `send-welcome-email` | Email user on login | (no return needed) |
| `init-student-session` | Set up student dashboard data | (no return needed) |
| `init-instructor-session` | Set up instructor dashboard | (no return needed) |
| `init-admin-session` | Set up admin dashboard | (no return needed) |

### Flow Logic
1. **Start** — User initiates login
2. **Enter Credentials** — Form with username/password/userType/emailDomain
3. **Validate Credentials** — External task checks against database
4. **Gateway: Valid?**
   - **No** → Show error → Loop back to Enter Credentials
   - **Yes** → Continue to role determination
5. **Determine Role (DMN)** — Calls `RoleAssignmentDecision` from `role-assignment.dmn`
6. **Send Welcome Email** — Personalized email based on role
7. **Gateway: Which Role?**
   - **STUDENT** → Init Student Session → End "Student Logged In"
   - **INSTRUCTOR** → Init Instructor Session → End "Instructor Logged In"
   - **ADMIN** → Init Admin Session → End "Admin Logged In"
   - **Default (GUEST)** → End "Access Denied"

### How to Test in Tasklist

1. Deploy the BPMN file (and `role-assignment.dmn` first!)
2. Open Tasklist: http://localhost:8080/camunda/app/tasklist/
3. Click **Start process** → Select "Authentication and Role Assignment"
4. Complete the **Enter Credentials** form:
   - Username: `john-doe`
   - Password: `Password123!`
   - User Type: `student`
   - Email Domain: `student.lms.edu`
5. Click **Complete**
6. The Python worker (must be running!) will validate, then DMN assigns role
7. Watch the process complete in Cockpit

### How to View in Cockpit

1. Open Cockpit: http://localhost:8080/camunda/app/cockpit/
2. Click **Processes** → "Authentication and Role Assignment"
3. View running and completed instances
4. Click any instance to see the path it took (highlighted)

---

## 🛠️ Deployment Order

**IMPORTANT:** Deploy DMN files first, then BPMN. The BPMN references DMN by ID, so DMN must exist first.

```
1. Deploy all 4 .dmn files (any order)
2. Deploy 01-authentication.bpmn
3. Start Python workers
4. Test in Tasklist
```

---

## 🔄 Process Variables Reference

When you need the workers to handle these BPMN diagrams, this is the variable contract:

### Authentication Process
```python
# Variables the worker receives
{
    "username": "john-doe",
    "password": "secret123",
    "userType": "student",
    "emailDomain": "student.lms.edu"
}

# Variables the worker should set
{
    "credentialsValid": True,
    "userId": "user_42"
}
```

---

## 📝 Notes

- All processes have `camunda:historyTimeToLive="180"` (180 days) — required for Camunda 7.13+
- Service tasks use the **External Task pattern** (not Java delegates)
- This works perfectly with our Python workers via REST polling
- Each Service Task has a `camunda:topic` that the Python worker subscribes to
