# Contributing Guide

> For team collaboration on the AI-Enhanced LMS project.

## 🌳 Branch Strategy

```
main (protected)
├── develop
│   ├── feature/dmn-tables
│   ├── feature/bpmn-authentication
│   ├── feature/python-workers
│   └── feature/email-integration
```

## 📝 Commit Message Convention

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

| Type | Use for |
|---|---|
| `feat:` | New feature (BPMN diagram, worker, DMN table) |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `refactor:` | Code restructuring |
| `test:` | Adding tests |
| `chore:` | Maintenance, deps update |

### Examples
```bash
git commit -m "feat: add learning-path DMN decision table"
git commit -m "feat(bpmn): create authentication & role assignment diagram"
git commit -m "fix(worker): handle email service connection timeout"
git commit -m "docs: update README with deployment steps"
```

## 🔄 Workflow

1. **Pull latest** before starting work:
   ```bash
   git pull origin develop
   ```

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make small, focused commits**

4. **Push and open a Pull Request:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Review with teammates** before merging to `develop`

6. **Only merge `develop` → `main`** for milestones / submissions

## 👥 Team Roles (Suggested)

| Member | Primary Responsibility |
|---|---|
| Member 1 | BPMN Diagrams (1, 2, 3) + Forms |
| Member 2 | BPMN Diagrams (4, 5, 6) + Forms |
| Member 3 | DMN Tables + Decision Logic |
| Member 4 | Python Workers + Email Integration |
| All | Report + Presentation + Testing |

## ✅ Pull Request Checklist

Before requesting a review:
- [ ] Code runs locally
- [ ] BPMN deploys to Camunda without errors
- [ ] No `.env`, passwords, or API keys committed
- [ ] README updated if needed
- [ ] Screenshots added for visual changes (Cockpit/Tasklist)
