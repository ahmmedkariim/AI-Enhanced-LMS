# 🎯 DMN Decision Tables — Complete Guide

This folder contains **4 executable DMN decision tables** for the AI-Enhanced LMS project.

---

## 📊 Overview

| # | File | Decision ID | Inputs | Outputs | Rules |
|---|---|---|---|---|---|
| 1 | `learning-path.dmn` | `LearningPathDecision` | 3 | 1 | 16 |
| 2 | `gamification-reward.dmn` | `GamificationRewardDecision` | 3 | 3 | 17 |
| 3 | `role-assignment.dmn` | `RoleAssignmentDecision` | 3 | 4 | 10 |
| 4 | `quiz-difficulty.dmn` | `QuizDifficultyDecision` | 3 | 4 | 9 |

All tables use **`hitPolicy="FIRST"`** — the first matching rule wins, and a default fallback rule at the end ensures every input combination produces a decision.

---

## 🚀 How to Deploy

### Option 1: Camunda Modeler (Recommended)
1. Open Camunda Modeler
2. **File → Open** → Select any `.dmn` file
3. Click the **🚀 Deploy** button (top-right)
4. Set Endpoint URL: `http://localhost:8080/engine-rest`
5. Username/Password: `demo` / `demo`
6. Click **Deploy**

### Option 2: REST API (curl)
```bash
curl -X POST http://localhost:8080/engine-rest/deployment/create \
  -u demo:demo \
  -F "deployment-name=DMN-LearningPath" \
  -F "deploy-changed-only=true" \
  -F "learning-path.dmn=@learning-path.dmn"
```

### Verify Deployment
1. Open Cockpit: http://localhost:8080/camunda/app/cockpit/
2. Click **Decisions** tab
3. You should see all 4 decisions listed

---

## 🧪 Testing in Cockpit

Camunda Cockpit lets you test DMN evaluations directly:

1. Go to **Cockpit → Decisions**
2. Click on a decision name
3. Click **Evaluate** (top-right)
4. Enter test input values
5. View the result

---

## 📝 Test Cases

### DMN 1: Learning Path Decision

**Input variables expected:**
- `quizScore` (string): `"High"`, `"Medium"`, `"Low"`
- `learningStyle` (string): `"Visual"`, `"Auditory"`, `"Reading"`, `"Kinesthetic"`, `"Active"`, `"Reflective"`
- `engagementLevel` (string): `"High"`, `"Medium"`, `"Low"`

| Test | quizScore | learningStyle | engagementLevel | Expected Output |
|---|---|---|---|---|
| 1 | High | Visual | High | "Advanced Visual Content with Interactive Diagrams" |
| 2 | Medium | Active | High | "Practice Exercises with Solved Examples" |
| 3 | Low | Reflective | Low | "Remedial Content with One-on-One LLM Tutor Sessions" |
| 4 | Medium | Visual | Low | "Gamified Learning Modules to Boost Engagement" |
| 5 | High | Kinesthetic | High | "Lab Simulations and Practical Workshops" |

---

### DMN 2: Gamification Reward Decision

**Input variables expected:**
- `activityType` (string): `"Quiz"`, `"TeamTask"`, `"Exploration"`, `"LiveQuiz"`, `"Poll"`, `"Discussion"`, `"LectureGame"`
- `performance` (string): `"High"`, `"Medium"`, `"Low"`
- `collaborationLevel` (string): `"High"`, `"Medium"`, `"Low"`, `"None"`

**Outputs:**
- `rewardType` (string): The badge/trophy name
- `pointsAwarded` (integer): Points to add to score
- `badgeIcon` (string): Icon identifier for UI

| Test | activityType | performance | collaboration | rewardType | points |
|---|---|---|---|---|---|
| 1 | Quiz | High | - | Gold Badge - Quiz Master | 100 |
| 2 | TeamTask | High | High | Team Champion Trophy | 200 |
| 3 | Exploration | High | - | Hidden Discovery Badge | 75 |
| 4 | LectureGame | High | - | AI Game Champion Trophy | 120 |
| 5 | Poll | Medium | Medium | Voice Heard Badge | 20 |

---

### DMN 3: Role Assignment Decision

**Input variables expected:**
- `userType` (string): `"student"`, `"instructor"`, `"admin"`, `"ai_service"`, `"llm_service"`
- `emailDomain` (string): `"student.edu"`, `"faculty.edu"`, `"admin.lms.edu"`, etc.
- `credentialsValid` (boolean): `true` or `false`

**Outputs:**
- `assignedRole` (string): Role name
- `dashboardRoute` (string): URL to redirect to
- `permissions` (string): Comma-separated permission list
- `accessGranted` (boolean): Final access decision

| Test | userType | emailDomain | credentialsValid | assignedRole | accessGranted |
|---|---|---|---|---|---|
| 1 | student | student.edu | true | STUDENT | true |
| 2 | instructor | faculty.edu | true | INSTRUCTOR | true |
| 3 | admin | admin.lms.edu | true | ADMIN | true |
| 4 | student | - | false | GUEST | false |
| 5 | ai_service | - | true | AI_SERVICE | true |

---

### DMN 4: Quiz Difficulty Adjustment

**Input variables expected:**
- `previousScore` (integer): 0-100
- `consecutiveCorrect` (integer): Number of correct answers in a row
- `averageTimeSeconds` (integer): Average response time per question

**Outputs:**
- `nextDifficulty` (string): `"Expert"`, `"Hard"`, `"Medium"`, `"Easy"`
- `questionCount` (integer): How many questions in next quiz
- `provideHints` (boolean): Whether to show hints
- `timeLimitSeconds` (integer): Time limit for next quiz

| Test | previousScore | consecutiveCorrect | avgTime | nextDifficulty | questions |
|---|---|---|---|---|---|
| 1 | 95 | 7 | 25 | Expert | 15 |
| 2 | 80 | 3 | 45 | Hard | 10 |
| 3 | 65 | 1 | 60 | Medium | 8 |
| 4 | 40 | 0 | 90 | Easy | 6 |
| 5 | 20 | 0 | 120 | Easy | 5 |

---

## 🔗 How These Connect to BPMN

In your BPMN diagrams, you'll use **Business Rule Tasks** that reference these decisions:

```xml
<bpmn:businessRuleTask id="Task_DetermineLearningPath"
    name="Determine Learning Path"
    camunda:decisionRef="LearningPathDecision"
    camunda:resultVariable="learningPathResult"
    camunda:mapDecisionResult="singleEntry">
</bpmn:businessRuleTask>
```

### Decision Result Mapping Options

| Map Mode | When to Use | What's Returned |
|---|---|---|
| `singleEntry` | One output, one rule matches | The single value |
| `singleResult` | Multiple outputs, one rule matches | A map of outputs |
| `collectEntries` | One output, multiple rules match | A list of values |
| `resultList` | Multiple outputs, multiple rules match | A list of maps |

### Example: Calling DMN 2 (Gamification) from BPMN

```xml
<bpmn:businessRuleTask id="Task_CalculateReward"
    name="Calculate Reward"
    camunda:decisionRef="GamificationRewardDecision"
    camunda:resultVariable="rewardResult"
    camunda:mapDecisionResult="singleResult">
</bpmn:businessRuleTask>
```

After execution, your process will have access to:
- `rewardResult.rewardType` → "Gold Badge - Quiz Master"
- `rewardResult.pointsAwarded` → 100
- `rewardResult.badgeIcon` → "trophy_gold"

---

## 💡 FEEL Expression Cheat Sheet

The expressions used in input entries:

| Expression | Meaning |
|---|---|
| `"High"` | Exact match |
| `"High","Medium"` | Match either value (OR) |
| `>= 90` | Number ≥ 90 |
| `< 30` | Number < 30 |
| `[60..74]` | Number in range (inclusive) |
| `[60..74)` | Number in range (exclusive end) |
| `-` | Match anything (wildcard) |
| `not("Low")` | Anything except "Low" |
| `true` / `false` | Boolean literals |

In XML, **`<`** must be written as **`&lt;`** and **`>`** as **`&gt;`**.

---

## ✅ Validation Status

All 4 DMN files have been validated:
- ✅ Valid XML structure
- ✅ Camunda namespace declared
- ✅ DMN 1.3 schema compliance
- ✅ Default fallback rules present
- ✅ DMN diagram interchange (DMNDI) included
- ✅ Ready for deployment to Camunda 7
