# 🐙 GitHub Setup Guide

Step-by-step instructions to put this project on GitHub.

---

## 📋 Prerequisites

1. **GitHub account** — Sign up free at https://github.com
2. **Git installed** — Download from https://git-scm.com/downloads
3. **Verify install:**
   ```bash
   git --version
   ```

---

## 🚀 First-Time Git Setup

Configure Git with your name and email (use your GitHub email):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 📦 Option A: Create Repository via GitHub Website (Easiest)

### Step 1: Create the repo on GitHub
1. Go to https://github.com/new
2. **Repository name:** `ai-enhanced-lms` (or your preferred name)
3. **Description:** "AI-Enhanced LMS with Hybrid Learning, DMN & Executable BPMN — Software Process Engineering Project"
4. **Visibility:**
   - ⭐ **Public** (recommended — shows in your portfolio)
   - 🔒 **Private** (if you don't want others to see until grading)
5. ❌ **Do NOT** initialize with README (we already have one)
6. Click **Create repository**

### Step 2: Push your local project
GitHub will show you commands. Run them in your project folder:

```bash
cd ai-enhanced-lms

# Initialize Git
git init

# Add all files (gitignore handles exclusions)
git add .

# First commit
git commit -m "feat: initial project structure with Camunda 7 + Python setup"

# Set main branch
git branch -M main

# Connect to GitHub (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/ai-enhanced-lms.git

# Push
git push -u origin main
```

---

## 📦 Option B: Using GitHub Desktop (No command line)

If you prefer a GUI:
1. Download **GitHub Desktop**: https://desktop.github.com/
2. Sign in with your GitHub account
3. Click **File → Add Local Repository**
4. Select your `ai-enhanced-lms` folder
5. Click **Publish repository**

---

## 🔐 Authentication (Important!)

GitHub no longer accepts passwords for `git push`. You need either:

### Option 1: Personal Access Token (PAT) — Recommended
1. Go to https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Give it a name like "ai-enhanced-lms"
4. Select scopes: ✅ `repo`
5. **Copy the token immediately** (you won't see it again!)
6. When Git asks for password during `git push`, paste this token

### Option 2: SSH Key (More secure, one-time setup)
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Show public key
cat ~/.ssh/id_ed25519.pub
```
Then add to GitHub: https://github.com/settings/ssh/new

---

## 🔄 Daily Workflow

```bash
# Check what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "feat(dmn): add learning path decision table"

# Push to GitHub
git push
```

---

## 🛡️ Safety Checklist Before Pushing

Always verify:
- [ ] `.env` file is NOT being committed (`git status` shouldn't show it)
- [ ] No passwords in code
- [ ] No API keys in code
- [ ] No personal info in commit messages

**Quick check:**
```bash
git status
# .env should NOT appear in the list
```

If `.env` is being tracked by mistake:
```bash
git rm --cached .env
git commit -m "chore: untrack .env file"
```

---

## 📊 Useful Commands

| Command | What it does |
|---|---|
| `git status` | See what changed |
| `git log --oneline` | View commit history |
| `git diff` | See exact line changes |
| `git pull` | Get latest from GitHub |
| `git push` | Send your commits to GitHub |
| `git checkout -b new-branch` | Create & switch to new branch |
| `git branch` | List branches |

---

## 🆘 Common Issues & Fixes

### "Authentication failed"
→ Use a Personal Access Token (see above), not your password.

### "Permission denied (publickey)"
→ Add your SSH key to GitHub, or use HTTPS URL instead.

### "Updates were rejected because the remote contains work..."
→ Run: `git pull origin main --rebase` first, then push.

### Accidentally committed `.env`?
```bash
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "fix: remove .env from tracking"
git push
```
**Then immediately rotate any exposed credentials!**

---

## 🎓 Pro Tips for Academic Submission

1. **Tag the final version** before submitting:
   ```bash
   git tag -a v1.0-final -m "Final submission for Eng. Sara"
   git push origin v1.0-final
   ```

2. **Add the GitHub link to your report** — looks professional.

3. **Make releases** with the ZIP attached:
   - GitHub repo → Releases → Create new release
   - Attach your final ZIP for easy professor download.

4. **Star the project** — shows confidence in your work.

5. **Pin the repo** on your GitHub profile.

---

## 🚀 Next Steps

After your first push:
1. ✅ Verify all files appear on GitHub
2. ✅ Confirm `.env` is NOT visible (security check)
3. ✅ Check that README renders nicely on the repo page
4. 🎉 Share the repo link with teammates / professor
