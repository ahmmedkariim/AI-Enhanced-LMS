"""
setup_camunda_users.py
Creates all required Camunda user accounts, groups, and memberships
via the Camunda REST API.

Run ONCE after starting Camunda:
    python setup_camunda_users.py

What it creates:
  Groups:  students, instructors, admins
  Users:   ahmed, john-doe, jane-smith, ahmed-ali, dr-sara, prof-hassan, system-admin
  Assigns: each user to their correct group
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

CAMUNDA_URL  = os.getenv("CAMUNDA_REST_URL", "http://localhost:8080/engine-rest")
ADMIN_AUTH   = (os.getenv("CAMUNDA_USERNAME", "demo"), os.getenv("CAMUNDA_PASSWORD", "demo"))

GREEN  = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"
BLUE   = "\033[94m"; BOLD = "\033[1m"; RESET  = "\033[0m"

# ─── Data to create ───────────────────────────────────────────

GROUPS = [
    {
        "id":   "students",
        "name": "LMS Students",
        "type": "WORKFLOW"
    },
    {
        "id":   "instructors",
        "name": "LMS Instructors",
        "type": "WORKFLOW"
    },
    {
        "id":   "admins",
        "name": "LMS Administrators",
        "type": "WORKFLOW"
    },
]

USERS = [
    # Students
    {
        "id":         "ahmed",
        "firstName":  "Ahmed",
        "lastName":   "Student",
        "email":      "ahmed@student.lms.edu",
        "password":   "Password123!",
        "group":      "students",
    },
    {
        "id":         "john-doe",
        "firstName":  "John",
        "lastName":   "Doe",
        "email":      "john.doe@student.lms.edu",
        "password":   "Password123!",
        "group":      "students",
    },
    {
        "id":         "jane-smith",
        "firstName":  "Jane",
        "lastName":   "Smith",
        "email":      "jane.smith@student.lms.edu",
        "password":   "Password123!",
        "group":      "students",
    },
    {
        "id":         "ahmed-ali",
        "firstName":  "Ahmed",
        "lastName":   "Ali",
        "email":      "ahmed.ali@student.lms.edu",
        "password":   "Password123!",
        "group":      "students",
    },
    # Instructors
    {
        "id":         "dr-sara",
        "firstName":  "Sara",
        "lastName":   "Elshorbagy",
        "email":      "sara@faculty.lms.edu",
        "password":   "Password123!",
        "group":      "instructors",
    },
    {
        "id":         "prof-hassan",
        "firstName":  "Hassan",
        "lastName":   "Professor",
        "email":      "hassan@faculty.lms.edu",
        "password":   "Password123!",
        "group":      "instructors",
    },
    # Admins
    {
        "id":         "system-admin",
        "firstName":  "System",
        "lastName":   "Administrator",
        "email":      "admin@admin.lms.edu",
        "password":   "Admin456!",
        "group":      "admins",
    },
]


# ─── Helpers ─────────────────────────────────────────────────

def req(method, path, **kwargs):
    url = f"{CAMUNDA_URL}{path}"
    try:
        r = getattr(requests, method)(url, auth=ADMIN_AUTH, timeout=10, **kwargs)
        return r
    except Exception as e:
        print(f"{RED}Request error: {e}{RESET}")
        return None


def create_group(group: dict) -> bool:
    """Create a Camunda group. Skip if already exists."""
    # Check if exists
    r = req("get", f"/group/{group['id']}")
    if r is not None and r.status_code == 200:
        print(f"  {YELLOW}⚠️  Group '{group['id']}' already exists — skipping{RESET}")
        return True

    r = req("post", "/group/create", json={
        "id":   group["id"],
        "name": group["name"],
        "type": group["type"],
    })
    if r is not None and r.status_code == 204:
        print(f"  {GREEN}✅ Group created: {group['id']} ({group['name']}){RESET}")
        return True
    else:
        err = f"HTTP {r.status_code}: {r.text[:200]}" if r is not None else "no response"
        print(f"  {RED}❌ Group failed: {group['id']} → {err}{RESET}")
        return False


def create_user(user: dict) -> bool:
    """Create a Camunda user account. Skip if already exists."""
    uid = user["id"]

    # Check if exists
    r = req("get", f"/user/{uid}/profile")
    if r is not None and r.status_code == 200:
        print(f"  {YELLOW}⚠️  User '{uid}' already exists — skipping{RESET}")
        return True

    r = req("post", "/user/create", json={
        "profile": {
            "id":        uid,
            "firstName": user["firstName"],
            "lastName":  user["lastName"],
            "email":     user["email"],
        },
        "credentials": {
            "password": user["password"],
        }
    })
    if r is not None and r.status_code == 204:
        print(f"  {GREEN}✅ User created: {uid} ({user['firstName']} {user['lastName']}){RESET}")
        return True
    else:
        err = f"HTTP {r.status_code}: {r.text[:300]}" if r is not None else "no response"
        print(f"  {RED}❌ User failed: {uid} → {err}{RESET}")
        return False


def add_to_group(user_id: str, group_id: str) -> bool:
    """Add a user to a Camunda group."""
    r = req("put", f"/group/{group_id}/members/{user_id}")
    if r is not None and r.status_code == 204:
        print(f"  {GREEN}✅ {user_id} → group '{group_id}'{RESET}")
        return True
    else:
        # 500 usually means already a member
        print(f"  {YELLOW}⚠️  {user_id} may already be in '{group_id}'{RESET}")
        return True


def grant_tasklist_access(user_id: str):
    """Grant the user access to Tasklist and Cockpit applications."""
    apps = ["tasklist", "cockpit"]
    for app in apps:
        r = req("post", f"/authorization/create", json={
            "type":         1,       # GRANT
            "permissions":  ["ALL"],
            "userId":       user_id,
            "groupId":      None,
            "resourceType": 0,       # APPLICATION
            "resourceId":   app,
        })
        # 204 = created, 400 = already exists — both are fine
        if r and r.status_code in (204, 400):
            pass


def verify_users():
    """Print all users currently in Camunda."""
    r = req("get", "/user?firstResult=0&maxResults=50")
    if r and r.status_code == 200:
        users = r.json()
        print(f"\n  {BOLD}All Camunda users ({len(users)} total):{RESET}")
        for u in users:
            print(f"  • {u['id']:<20} {u.get('firstName','')} {u.get('lastName','')}")


def print_login_table():
    """Print the login credentials for the demo."""
    print(f"""
{BOLD}{BLUE}╔══════════════════════════════════════════════════════════════════╗
║                   LMS User Login Credentials                     ║
╠══════════════════════════════════════════════════════════════════╣
║  Tasklist URL: http://localhost:8080/camunda/app/tasklist/       ║
╠══════════╦══════════════╦════════════╦══════════════════════════╣
║  Username║  Password    ║  Role      ║  Email                   ║
╠══════════╬══════════════╬════════════╬══════════════════════════╣
║  ahmed   ║  Password123!║  Student   ║  ahmed@student.lms.edu   ║
║  john-doe║  Password123!║  Student   ║  john.doe@student.lms.edu║
║  jane-   ║  Password123!║  Student   ║  jane.smith@student...   ║
║  dr-sara ║  Password123!║  Instructor║  sara@faculty.lms.edu    ║
║  prof-   ║  Password123!║  Instructor║  hassan@faculty.lms.edu  ║
║  system- ║  Admin456!   ║  Admin     ║  admin@admin.lms.edu     ║
╚══════════╩══════════════╩════════════╩══════════════════════════╝{RESET}
""")


def main():
    print(f"""
{BOLD}{BLUE}╔══════════════════════════════════════════════════════╗
║     AI-Enhanced LMS — Camunda User Setup Script    ║
╚══════════════════════════════════════════════════════╝{RESET}
""")

    # Check Camunda
    r = req("get", "/engine")
    if not r or r.status_code != 200:
        print(f"{RED}❌ Camunda not reachable at {CAMUNDA_URL}{RESET}")
        print(f"{YELLOW}   Start Camunda first: start.bat --rest{RESET}")
        sys.exit(1)
    print(f"{GREEN}✅ Camunda connected{RESET}\n")

    # Step 1: Create groups
    print(f"{BOLD}Step 1: Creating user groups{RESET}")
    print("─" * 45)
    for group in GROUPS:
        create_group(group)

    # Step 2: Create users
    print(f"\n{BOLD}Step 2: Creating user accounts{RESET}")
    print("─" * 45)
    for user in USERS:
        create_user(user)

    # Step 3: Assign users to groups
    print(f"\n{BOLD}Step 3: Assigning users to groups{RESET}")
    print("─" * 45)
    for user in USERS:
        add_to_group(user["id"], user["group"])

    # Step 4: Grant Tasklist/Cockpit access
    print(f"\n{BOLD}Step 4: Granting application access{RESET}")
    print("─" * 45)
    for user in USERS:
        grant_tasklist_access(user["id"])
        print(f"  {GREEN}✅ Access granted: {user['id']}{RESET}")

    # Step 5: Verify
    verify_users()

    # Print login table
    print_login_table()

    print(f"{GREEN}{BOLD}✅ Setup complete!{RESET}")
    print(f"Each user can now log into Tasklist with their own credentials.")
    print(f"Tasklist: {BLUE}http://localhost:8080/camunda/app/tasklist/{RESET}\n")


if __name__ == "__main__":
    main()
