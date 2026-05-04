"""
LMS Diagnostic Script — run this before workers.main
It checks every dependency and connection so you know exactly what's wrong.

Run: python diagnose.py
"""
import sys
import os

print("\n" + "="*60)
print("  AI-Enhanced LMS — Startup Diagnostics")
print("="*60 + "\n")

issues = []
warnings = []

# ── 1. Python version ────────────────────────────────────────
v = sys.version_info
status = "✅" if v >= (3, 10) else "❌"
print(f"{status} Python version: {v.major}.{v.minor}.{v.micro}", end="")
if v < (3, 10):
    print(" ← Need 3.10+")
    issues.append("Upgrade Python to 3.10 or later")
else:
    print()

# ── 2. Virtual environment ────────────────────────────────────
in_venv = sys.prefix != sys.base_prefix
print(f"{'✅' if in_venv else '⚠️ '} Virtual environment: {'active (' + sys.prefix + ')' if in_venv else 'NOT active'}")
if not in_venv:
    warnings.append("No venv active — run: python -m venv venv && venv\\Scripts\\activate (Windows) or source venv/bin/activate (Mac/Linux)")

# ── 3. Required packages ──────────────────────────────────────
print("\n📦 Checking required packages:")
packages = {
    "camunda.external_task.external_task_worker": "camunda-external-task-client-python3",
    "dotenv":    "python-dotenv",
    "requests":  "requests",
    "fastapi":   "fastapi (optional)",
}

missing_installs = []
for module, pip_name in packages.items():
    try:
        __import__(module)
        print(f"  ✅ {pip_name}")
    except ImportError:
        optional = "(optional)" in pip_name
        pip_clean = pip_name.replace(" (optional)", "")
        marker = "⚠️ " if optional else "❌"
        print(f"  {marker} {pip_name} — NOT installed")
        if not optional:
            missing_installs.append(pip_clean)
            issues.append(f"Install: pip install {pip_clean}")

# ── 4. .env file ──────────────────────────────────────────────
print("\n📄 Checking .env file:")
env_path = ".env"
if os.path.exists(env_path):
    print(f"  ✅ .env found")
    from dotenv import load_dotenv
    load_dotenv()
    camunda_url = os.getenv("CAMUNDA_REST_URL", "http://localhost:8080/engine-rest")
    print(f"  ℹ️  CAMUNDA_REST_URL = {camunda_url}")
else:
    print("  ⚠️  .env not found — using defaults (localhost:8080)")
    warnings.append("Create .env from .env.example: cp .env.example .env")
    camunda_url = "http://localhost:8080/engine-rest"

# ── 5. Camunda connection ─────────────────────────────────────
print(f"\n🔌 Checking Camunda at {camunda_url}:")
try:
    import requests
    resp = requests.get(f"{camunda_url}/engine", timeout=4)
    if resp.status_code == 200:
        engines = resp.json()
        name = engines[0].get("name", "default") if engines else "default"
        print(f"  ✅ Camunda is RUNNING — engine: '{name}'")
    else:
        print(f"  ❌ Camunda returned HTTP {resp.status_code}")
        issues.append("Camunda returned unexpected status — check it started correctly")
except requests.exceptions.ConnectionError:
    print("  ❌ Camunda is NOT running (connection refused)")
    issues.append("Start Camunda first: run start.bat --rest (Windows) or ./start.sh --rest (Mac/Linux)")
except requests.exceptions.Timeout:
    print("  ❌ Camunda timed out — it may still be starting up, wait 30s and retry")
    issues.append("Camunda is slow to start — wait 30 seconds then retry")
except Exception as e:
    print(f"  ❌ Unexpected error: {e}")
    issues.append(f"Check Camunda manually: {e}")

# ── 6. data/ folder ───────────────────────────────────────────
print("\n📁 Checking project structure:")
folders = ["bpmn", "dmn", "workers", "data", "forms"]
for folder in folders:
    exists = os.path.isdir(folder)
    print(f"  {'✅' if exists else '❌'} {folder}/")
    if not exists:
        issues.append(f"Missing folder: {folder}/ — are you running from the project root (ai-enhanced-lms/)?")

# ── 7. BPMN & DMN files ───────────────────────────────────────
import glob
bpmn_files = glob.glob("bpmn/*.bpmn")
dmn_files  = glob.glob("dmn/*.dmn")
print(f"\n  📋 BPMN files found: {len(bpmn_files)}/6  {bpmn_files}")
print(f"  📋 DMN  files found: {len(dmn_files)}/4  {dmn_files}")
if len(bpmn_files) < 6:
    warnings.append(f"Only {len(bpmn_files)} BPMN files found — deploy all 6 from Camunda Modeler")

# ── Summary ───────────────────────────────────────────────────
print("\n" + "="*60)
if not issues:
    print("✅ ALL CHECKS PASSED — workers should start fine!")
    print("   Run: python -m workers.main")
else:
    print(f"❌ {len(issues)} issue(s) must be fixed:\n")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

if warnings:
    print(f"\n⚠️  {len(warnings)} warning(s):\n")
    for w in warnings:
        print(f"  • {w}")

# ── Quick fix commands ────────────────────────────────────────
if missing_installs:
    print(f"\n🔧 Run this to install missing packages:")
    print(f"   pip install {' '.join(missing_installs)}")

print("\n" + "="*60 + "\n")
