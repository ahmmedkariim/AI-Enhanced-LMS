"""
deploy.py — Auto-deploy all DMN, BPMN, and Camunda Forms to Camunda Platform 7

Run ONCE before starting workers or tests:
    python deploy.py

This script:
  1. Deploys all DMN files first (BPMN references them)
  2. Deploys each BPMN file together with its referenced .form files in a
     single deployment, so that camunda:formKey values of the form
     "camunda-forms:deployment:<file>.form" resolve correctly
  3. Verifies each deployment succeeded
  4. Prints a summary
"""
import os
import sys
import glob
from typing import List, Optional
import requests
from datetime import datetime

# ─── Config ──────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

CAMUNDA_URL  = os.getenv("CAMUNDA_REST_URL", "http://localhost:8080/engine-rest")
CAMUNDA_USER = os.getenv("CAMUNDA_USERNAME", "demo")
CAMUNDA_PASS = os.getenv("CAMUNDA_PASSWORD", "demo")
AUTH         = (CAMUNDA_USER, CAMUNDA_PASS)

# Colors for terminal output
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def print_banner():
    print(f"""
{BOLD}{BLUE}╔══════════════════════════════════════════════════════════╗
║       AI-Enhanced LMS — Camunda Deployment Script       ║
║       Deploying DMN + BPMN to {CAMUNDA_URL[:28]:<28} ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

def check_camunda():
    """Verify Camunda is running before deploying."""
    try:
        r = requests.get(f"{CAMUNDA_URL}/engine", auth=AUTH, timeout=5)
        if r.status_code == 200:
            engine = r.json()[0].get("name", "default") if r.json() else "default"
            print(f"{GREEN}✅ Camunda connected — engine: '{engine}'{RESET}\n")
            return True
    except Exception as e:
        pass
    print(f"{RED}❌ Cannot connect to Camunda at {CAMUNDA_URL}{RESET}")
    print(f"{YELLOW}   Make sure Camunda is running: start.bat --rest{RESET}")
    return False


def deploy_file(filepath: str, deployment_name: str, extra_files: Optional[List[str]] = None) -> dict:
    """Deploy a .bpmn or .dmn file (optionally bundled with extra resources
    such as .form files) to Camunda in a single deployment."""
    filename = os.path.basename(filepath)
    extra_files = extra_files or []
    open_handles = []
    try:
        files = {}
        main_handle = open(filepath, "rb")
        open_handles.append(main_handle)
        files[filename] = (filename, main_handle, "application/octet-stream")

        bundled_names = []
        for extra in extra_files:
            extra_name = os.path.basename(extra)
            extra_handle = open(extra, "rb")
            open_handles.append(extra_handle)
            files[extra_name] = (extra_name, extra_handle, "application/octet-stream")
            bundled_names.append(extra_name)

        data = {
            "deployment-name":        deployment_name,
            "deployment-source":      "AI-Enhanced LMS Deploy Script",
            "deploy-changed-only":    "true",
            "enable-duplicate-filtering": "true",
        }
        r = requests.post(
            f"{CAMUNDA_URL}/deployment/create",
            auth=AUTH,
            files=files,
            data=data,
            timeout=15
        )

        if r.status_code in (200, 201):
            result = r.json()
            dep_id = result.get("id", "?")
            return {"success": True, "deployment_id": dep_id, "file": filename, "bundled": bundled_names}
        else:
            return {"success": False, "error": f"HTTP {r.status_code}: {r.text[:200]}", "file": filename, "bundled": bundled_names}

    except FileNotFoundError as e:
        return {"success": False, "error": f"File not found: {e.filename}", "file": filename, "bundled": []}
    except Exception as e:
        return {"success": False, "error": str(e), "file": filename, "bundled": []}
    finally:
        for h in open_handles:
            try:
                h.close()
            except Exception:
                pass


def verify_deployments():
    """List all deployed process definitions and decisions."""
    print(f"\n{BOLD}📋 Verifying deployed resources:{RESET}")

    # Process definitions (BPMN)
    r = requests.get(f"{CAMUNDA_URL}/process-definition?latestVersion=true", auth=AUTH)
    if r.status_code == 200:
        processes = r.json()
        print(f"\n  {BOLD}BPMN Processes ({len(processes)} deployed):{RESET}")
        for p in processes:
            print(f"  {GREEN}✅{RESET} [{p['key']}] {p['name']} (v{p['version']})")
    else:
        print(f"  {RED}❌ Could not fetch process definitions{RESET}")

    # Decision definitions (DMN)
    r = requests.get(f"{CAMUNDA_URL}/decision-definition?latestVersion=true", auth=AUTH)
    if r.status_code == 200:
        decisions = r.json()
        print(f"\n  {BOLD}DMN Decisions ({len(decisions)} deployed):{RESET}")
        for d in decisions:
            print(f"  {GREEN}✅{RESET} [{d['key']}] {d['name']} (v{d['version']})")
    else:
        print(f"  {RED}❌ Could not fetch decision definitions{RESET}")


def main():
    print_banner()

    if not check_camunda():
        sys.exit(1)

    # ── Deploy DMN first (BPMN references them by ID) ────────
    print(f"{BOLD}📊 Step 1: Deploying DMN Decision Tables{RESET}")
    print("─" * 50)

    dmn_files = sorted(glob.glob("dmn/*.dmn"))
    if not dmn_files:
        print(f"{RED}❌ No DMN files found in dmn/ folder{RESET}")
        print(f"{YELLOW}   Make sure you're running from the project root (ai-enhanced-lms/){RESET}")
        sys.exit(1)

    dmn_results = []
    for f in dmn_files:
        name = os.path.splitext(os.path.basename(f))[0]
        result = deploy_file(f, f"LMS-DMN-{name}")
        dmn_results.append(result)
        if result["success"]:
            print(f"  {GREEN}✅ {result['file']:<35}{RESET} → deployment ID: {result['deployment_id'][:8]}...")
        else:
            print(f"  {RED}❌ {result['file']:<35}{RESET} → {result['error']}")

    dmn_ok  = sum(1 for r in dmn_results if r["success"])
    dmn_fail = len(dmn_results) - dmn_ok
    print(f"\n  DMN: {GREEN}{dmn_ok} deployed{RESET}" + (f", {RED}{dmn_fail} failed{RESET}" if dmn_fail else ""))

    # ── Deploy BPMN ───────────────────────────────────────────
    print(f"\n{BOLD}📋 Step 2: Deploying BPMN Process Diagrams{RESET}")
    print("─" * 50)

    bpmn_files = sorted(glob.glob("bpmn/*.bpmn"))
    if not bpmn_files:
        print(f"{RED}❌ No BPMN files found in bpmn/ folder{RESET}")
        sys.exit(1)

    BPMN_NAMES = {
        "01-authentication.bpmn":    "Authentication & Role Assignment",
        "02-onboarding.bpmn":        "Student Onboarding Process",
        "03-adaptive-learning.bpmn": "Adaptive Learning Process",
        "04-hybrid-classroom.bpmn":  "Hybrid Classroom Process",
        "05-adaptive-quiz.bpmn":     "Adaptive Quiz Generation",
        "06-gamification.bpmn":      "Gamification & Reward Process",
    }

    # Forms bundled with each BPMN. The formKey "camunda-forms:deployment:<file>"
    # only resolves when the .form is in the SAME deployment as the BPMN.
    BPMN_FORMS = {
        "01-authentication.bpmn":    ["enter-credentials.form", "show-error.form",
                                      "welcome-role-assigned.form"],
        "02-onboarding.bpmn":        ["submit-learning-goals.form", "review-profile.form"],
        "03-adaptive-learning.bpmn": ["access-learning-materials.form"],
        "04-hybrid-classroom.bpmn":  ["live-poll.form", "team-challenge.form",
                                      "post-lecture-quiz.form"],
        "05-adaptive-quiz.bpmn":     ["take-adaptive-quiz.form", "quiz-result.form"],
        "06-gamification.bpmn":      ["view-achievement.form"],
    }

    bpmn_results = []
    for f in bpmn_files:
        fname = os.path.basename(f)
        name  = BPMN_NAMES.get(fname, fname)
        form_paths = [os.path.join("forms", form) for form in BPMN_FORMS.get(fname, [])]
        result = deploy_file(f, f"LMS-BPMN-{name}", extra_files=form_paths)
        bpmn_results.append(result)
        if result["success"]:
            forms_note = f" {BLUE}(+{len(result['bundled'])} forms){RESET}" if result.get("bundled") else ""
            print(f"  {GREEN}✅ {result['file']:<35}{RESET} → {name}{forms_note}")
        else:
            print(f"  {RED}❌ {result['file']:<35}{RESET} → {result['error']}")

    bpmn_ok   = sum(1 for r in bpmn_results if r["success"])
    bpmn_fail = len(bpmn_results) - bpmn_ok
    forms_ok  = sum(len(r.get("bundled", [])) for r in bpmn_results if r["success"])
    print(f"\n  BPMN: {GREEN}{bpmn_ok} deployed{RESET}" + (f", {RED}{bpmn_fail} failed{RESET}" if bpmn_fail else ""))
    print(f"  Forms bundled: {GREEN}{forms_ok}{RESET}")

    # ── Verify ────────────────────────────────────────────────
    verify_deployments()

    # ── Summary ───────────────────────────────────────────────
    total_ok   = dmn_ok + bpmn_ok
    total_fail = dmn_fail + bpmn_fail

    print(f"\n{'═'*50}")
    if total_fail == 0:
        print(f"{BOLD}{GREEN}🎉 All {total_ok} files deployed successfully!{RESET}")
        print(f"\n{BOLD}Next steps:{RESET}")
        print(f"  1. Start workers:  {YELLOW}python -m workers.main{RESET}")
        print(f"  2. Run e2e test:   {YELLOW}python test_e2e.py{RESET}")
        print(f"  3. Cockpit:        {BLUE}http://localhost:8080/camunda/app/cockpit/{RESET}")
        print(f"  4. Tasklist:       {BLUE}http://localhost:8080/camunda/app/tasklist/{RESET}")
    else:
        print(f"{BOLD}{YELLOW}⚠️  {total_ok} deployed, {total_fail} failed — check errors above{RESET}")

    print()


if __name__ == "__main__":
    main()
