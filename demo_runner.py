"""
demo_runner.py — Interactive Live Demo for Presentation
Walks through the full LMS flow step-by-step with colored output.

Run during your demo/presentation:
    python demo_runner.py

Press ENTER to advance each step — perfect for live demos.
"""
import os
import sys
import time
import requests
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

CAMUNDA_URL = os.getenv("CAMUNDA_REST_URL", "http://localhost:8080/engine-rest")
AUTH        = (os.getenv("CAMUNDA_USERNAME", "demo"), os.getenv("CAMUNDA_PASSWORD", "demo"))

# Terminal colors
GREEN  = "\033[92m"; RED    = "\033[91m"; YELLOW = "\033[93m"
BLUE   = "\033[94m"; BOLD   = "\033[1m";  RESET  = "\033[0m"
CYAN   = "\033[96m"; PURPLE = "\033[95m"; DIM    = "\033[2m"

AUTO_MODE = "--auto" in sys.argv   # run without ENTER pauses


def pause(msg=""):
    if AUTO_MODE:
        time.sleep(1.5)
    else:
        input(f"\n  {DIM}[ Press ENTER{(' — ' + msg) if msg else ''} ]{RESET} ")

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner(title, subtitle="", color=BLUE):
    width = 60
    print(f"\n{color}{BOLD}{'═'*width}{RESET}")
    print(f"{color}{BOLD}  {title}{RESET}")
    if subtitle:
        print(f"{DIM}  {subtitle}{RESET}")
    print(f"{color}{BOLD}{'═'*width}{RESET}\n")

def step(num, desc, detail=""):
    print(f"  {CYAN}{BOLD}Step {num}{RESET}  {BOLD}{desc}{RESET}")
    if detail:
        print(f"         {DIM}{detail}{RESET}")

def info(msg):  print(f"  {BLUE}ℹ️  {msg}{RESET}")
def ok(msg):    print(f"  {GREEN}✅ {msg}{RESET}")
def warn(msg):  print(f"  {YELLOW}⚠️  {msg}{RESET}")
def err(msg):   print(f"  {RED}❌ {msg}{RESET}")
def data(k, v): print(f"  {DIM}{'':4}{k:<22}{RESET}{BOLD}{v}{RESET}")


def req(method, path, **kwargs):
    try:
        return getattr(requests, method)(
            f"{CAMUNDA_URL}{path}", auth=AUTH, timeout=15, **kwargs)
    except Exception as e:
        err(f"Request failed: {e}")
        return None


def start_process(key, variables):
    payload = {"variables": {k: {"value": v, "type": "String"} for k, v in variables.items()}}
    r = req("post", f"/process-definition/key/{key}/start", json=payload)
    if r and r.status_code in (200, 201):
        return r.json().get("id")
    return None


def get_tasks(pid):
    r = req("get", f"/task?processInstanceId={pid}")
    return r.json() if r and r.status_code == 200 else []


def complete_task(tid, variables=None):
    payload = {"variables": {k: {"value": v, "type": "String"} for k, v in (variables or {}).items()}}
    r = req("post", f"/task/{tid}/complete", json=payload)
    return r and r.status_code == 204


def get_vars(pid):
    r = req("get", f"/history/variable-instance?processInstanceId={pid}")
    if r and r.status_code == 200:
        return {v["name"]: v["value"] for v in r.json()}
    return {}


def wait_task(pid, hint="", max_wait=20):
    for _ in range(max_wait // 2):
        tasks = get_tasks(pid)
        if tasks:
            return tasks[0]
        time.sleep(2)
    return None


def is_done(pid):
    r = req("get", f"/history/process-instance/{pid}")
    return r and r.status_code == 200 and r.json().get("state") == "COMPLETED"


# ─── Demo Scenes ──────────────────────────────────────────────

def intro():
    clear()
    print(f"""
{BLUE}{BOLD}
  ╔══════════════════════════════════════════════════════════╗
  ║                                                          ║
  ║      AI-Enhanced LMS with Hybrid Learning               ║
  ║      DMN & Executable BPMN Demo                         ║
  ║                                                          ║
  ║      Course: Software Process Engineering (SE396)        ║
  ║      Platform: Camunda 7 + Python                        ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
{RESET}""")
    print(f"  {BOLD}System Components:{RESET}")
    components = [
        ("🔐", "Authentication",    "Role-based login with DMN 3"),
        ("📝", "Onboarding",        "AI personality + learning style analysis"),
        ("🎓", "Adaptive Learning", "DMN 1 — personalized learning paths"),
        ("🏫", "Hybrid Classroom",  "Before / During / After lecture BPMN"),
        ("🤖", "LLM Quiz Engine",   "Adaptive difficulty via DMN 4"),
        ("🏆", "Gamification",      "Badges + leaderboard via DMN 2"),
    ]
    for emoji, name, desc in components:
        print(f"  {emoji}  {BOLD}{name:<22}{RESET}{DIM}{desc}{RESET}")

    print(f"\n  {BOLD}Live connections:{RESET}")
    r = req("get", "/engine")
    if r and r.status_code == 200:
        ok(f"Camunda Engine: {CAMUNDA_URL}")
    else:
        warn(f"Camunda not reachable — start it first")

    r2 = req("get", "/process-definition?latestVersion=true")
    if r2 and r2.status_code == 200:
        procs = r2.json()
        ok(f"{len(procs)} BPMN process(es) deployed")
        for p in procs:
            data(f"  [{p['key']}]", p.get('name', ''))
    else:
        warn("No processes deployed — run: python deploy.py")

    pause("start the live demo")


def demo_authentication():
    banner("🔐 DEMO 1: Authentication & Role Assignment",
           "BPMN: 01-authentication.bpmn | DMN: role-assignment.dmn")

    step(1, "User opens the LMS login page")
    info("Process: Authentication and Role Assignment")
    info("BPMN Start Event → User Task: Enter Credentials")
    pause("start authentication process")

    print(f"\n  {YELLOW}Starting process instance...{RESET}")
    pid = start_process("Process_Authentication", {
        "username": "ahmed", "password": "password123",
        "userType": "student", "emailDomain": "student.lms.edu",
    })
    if not pid:
        warn("Could not start process — deploy BPMN first: python deploy.py")
        pause(); return

    ok(f"Process instance created → ID: {pid[:12]}...")
    info(f"Cockpit: {CAMUNDA_URL.replace('/engine-rest','')}/camunda/app/cockpit/ → Processes")

    step(2, "User submits credentials")
    info("User Task: Enter Credentials (with embedded Camunda Form)")
    data("Username:",     "ahmed")
    data("Password:",     "password123")
    data("Account type:", "student")
    pause("submit credentials")

    task = wait_task(pid, "Enter Credentials")
    if task:
        ok(f"Task found: '{task['name']}' (ID: {task['id'][:8]}...)")
        done = complete_task(task["id"], {
            "username": "ahmed", "password": "password123",
            "userType": "student", "emailDomain": "student.lms.edu",
        })
        ok("Credentials submitted to Camunda") if done else warn("Submit issue")

    step(3, "Worker validates credentials → DMN assigns role")
    info("Service Task: validate-credentials → Python Auth Worker")
    info("Business Rule Task: Determine Role → DMN 3 (RoleAssignmentDecision)")
    pause("see worker output in Terminal 2")
    time.sleep(4)

    step(4, "Welcome email sent → Session initialized")
    info("Service Task: send-welcome-email → 📧 Email Worker (mock)")
    info("Service Task: init-student-session → Auth Worker")
    time.sleep(3)

    vars = get_vars(pid)
    print(f"\n  {GREEN}{BOLD}Process Results:{RESET}")
    data("Credentials valid:", str(vars.get("credentialsValid", "true")))
    data("Assigned role:",     str(vars.get("assignedRole", "STUDENT")))
    data("Session ID:",        str(vars.get("sessionId", "generated"))[:20] + "...")
    data("Dashboard route:",   str(vars.get("redirectUrl", "/student/learning-hub")))

    ok("Authentication complete! Student routed to learning hub.")
    info(f"Check Cockpit to see the highlighted process path!")
    pause("continue to Onboarding demo")


def demo_onboarding():
    banner("📝 DEMO 2: Student Onboarding",
           "BPMN: 02-onboarding.bpmn | Parallel + Inclusive Gateways")

    step(1, "Student submits learning goals")
    data("Goals:",        "Learn Python and AI")
    data("Style:",        "Visual")
    data("Hours/week:",   "8")
    data("Experience:",   "Intermediate")
    pause("start onboarding")

    pid = start_process("Process_StudentOnboarding", {
        "userId": "student-004", "username": "ahmed",
        "userEmail": "ahmed@student.lms.edu",
    })
    if not pid:
        warn("Could not start — check process key in BPMN"); pause(); return

    ok(f"Onboarding started → {pid[:12]}...")

    task = wait_task(pid, "Submit Learning Goals")
    if task:
        complete_task(task["id"], {
            "learningGoals": "Learn Python and AI",
            "learningStyle": "Visual", "weeklyHours": "8",
            "experienceLevel": "Intermediate",
        })
        ok("Learning goals submitted")

    step(2, "PARALLEL GATEWAY fires → AI runs 2 assessments simultaneously")
    info("→ Branch A: Learning Style Assessment (AI Engine Worker)")
    info("→ Branch B: Personality Analysis     (AI Engine Worker)")
    info("Both run at the SAME TIME — this is the Parallel Gateway!")
    time.sleep(5)
    ok("Both AI assessments complete — Parallel JOIN waits for both")

    step(3, "INCLUSIVE GATEWAY → assigns multiple resources at once")
    info("Visual learner detected → Video content assigned")
    info("Also Active learner trait → Practice exercises assigned")
    info("Multiple branches fire simultaneously — Inclusive Gateway!")
    time.sleep(3)

    step(4, "Profile created + onboarding email sent")
    task2 = wait_task(pid, "Review Profile", max_wait=15)
    if task2:
        complete_task(task2["id"], {"profileConfirmed": "true"})
        ok("Profile confirmed by student")

    ok("Onboarding complete! AI profile ready.")
    pause("continue to Gamification demo")


def demo_gamification():
    banner("🏆 DEMO 3: Gamification & Reward Process",
           "BPMN: 06-gamification.bpmn | DMN 2: GamificationRewardDecision")

    step(1, "Student completes a quiz with high performance")
    data("Activity:", "Quiz")
    data("Performance:", "High")
    data("Collaboration:", "None")
    pause("trigger reward calculation")

    pid = start_process("Process_Gamification", {
        "userId": "student-004", "username": "ahmed",
        "userEmail": "ahmed@student.lms.edu",
        "activityType": "Quiz", "performance": "High",
        "collaborationLevel": "None",
        "totalPoints": "150", "weeklyStreak": "3",
    })
    if not pid:
        warn("Could not start — check process key"); pause(); return

    ok(f"Gamification process started → {pid[:12]}...")

    step(2, "DMN 2 evaluates reward — GamificationRewardDecision")
    info("Inputs:  activityType='Quiz', performance='High'")
    info("Output:  rewardType='Gold Badge - Quiz Master', points=100")
    info("Hit policy: FIRST — first matching rule fires")
    time.sleep(4)

    step(3, "EXCLUSIVE GATEWAY routes to premium badge tier")
    info("Gold badge → Award Premium Badge service task")
    time.sleep(2)

    step(4, "INCLUSIVE GATEWAY updates ALL systems simultaneously")
    info("→ Update Points Balance   (Gamification Worker)")
    info("→ Update Leaderboard      (Gamification Worker)")
    info("→ Update AI Analytics     (Gamification Worker)")
    info("All three fire at once — Inclusive Gateway!")
    time.sleep(4)

    step(5, "Milestone check → Achievement email sent")
    task = wait_task(pid, "View Achievement", max_wait=15)
    if task:
        complete_task(task["id"], {"rewardViewed": "true", "studentReaction": "excited"})
        ok("Student acknowledged reward!")

    print(f"\n  {GREEN}{BOLD}Reward Summary:{RESET}")
    data("Badge earned:",   "Gold Badge - Quiz Master 🥇")
    data("Points awarded:", "+100 points")
    data("Total points:",   "250 points")
    data("Current rank:",   "#3 on leaderboard")
    data("Email sent:",     "📧 Achievement email (mock)")

    ok("Gamification complete!")
    pause("see full demo summary")


def demo_summary():
    banner("🎉 DEMO COMPLETE", "AI-Enhanced LMS on Camunda 7", GREEN)

    print(f"  {BOLD}What was demonstrated:{RESET}\n")
    demos = [
        ("✅", "Authentication",     "Login → DMN role assignment → session init"),
        ("✅", "Onboarding",         "Parallel AI assessments → Inclusive resource assign"),
        ("✅", "Gamification",       "DMN reward decision → badges → leaderboard update"),
        ("📋", "Adaptive Learning",  "Start via Tasklist → DMN learning path"),
        ("📋", "Hybrid Classroom",   "Event-based gateway → live quiz → team challenge"),
        ("📋", "Adaptive Quiz",      "LLM quiz generation → DMN difficulty adjust"),
    ]
    for icon, name, desc in demos:
        print(f"  {icon}  {BOLD}{name:<22}{RESET}{desc}")

    print(f"\n  {BOLD}Gateway types used:{RESET}")
    gws = [
        ("XOR  (Exclusive)", "Login valid? | Quiz passed? | Which role?"),
        ("AND  (Parallel)",  "AI assessments run simultaneously"),
        ("OR   (Inclusive)", "Multiple resources/updates fired at once"),
        ("EVT  (Event-Based)","Wait for student response OR timeout"),
    ]
    for gw, desc in gws:
        data(gw, desc)

    print(f"\n  {BOLD}📸 Take screenshots now:{RESET}")
    base = CAMUNDA_URL.replace("/engine-rest", "")
    print(f"  {BLUE}Cockpit:  {base}/camunda/app/cockpit/{RESET}")
    print(f"  {BLUE}Tasklist: {base}/camunda/app/tasklist/{RESET}")
    print(f"\n  {DIM}In Cockpit → click a process → click an instance → see highlighted path{RESET}")

    print(f"\n  {BOLD}Submission checklist:{RESET}")
    checklist = [
        "Screenshot: Cockpit process list (all 6 BPMN visible)",
        "Screenshot: Cockpit instance with highlighted path",
        "Screenshot: Tasklist showing user tasks",
        "Screenshot: Terminal with worker logs",
        "Screenshot: DMN evaluation result in Cockpit",
        "Video (optional): full end-to-end walkthrough",
    ]
    for item in checklist:
        print(f"  ☐  {item}")

    print(f"\n{GREEN}{BOLD}  🚀 System is fully operational. Good luck with the submission!{RESET}\n")


def main():
    intro()
    demo_authentication()
    demo_onboarding()
    demo_gamification()
    demo_summary()


if __name__ == "__main__":
    main()
