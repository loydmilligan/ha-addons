# Triage Review Skill

<skill-definition>
name: review-triage
triggers:
  - "review triage"
  - "triage review"
  - "review lumberjacker triage"
  - "check triage decisions"
  - "evaluate triage"
  - "triage audit"
  - "/review-triage"
</skill-definition>

## Purpose

Review AI triage decisions from Lumberjacker to validate accuracy, catch errors, and improve the triage process over time. This is especially important in early days when the triage model is being tuned.

## Workflow Overview

1. **Load** - Read triage log from `/share/lumberjacker/triage-log.json`
2. **Filter** - Show only unreviewed items (or specific batch/tag)
3. **Summary** - Present overview of pending reviews
4. **Review Loop** - For each item:
   - Quick overview (go/no-go for deep review)
   - Deep review with rubric (if needed)
   - Record verdict and tags
5. **Save** - Update triage log with review results
6. **Report** - Generate session summary

---

## Phase 1: Load & Summary

When skill is invoked:

1. Read `/share/lumberjacker/triage-log.json`
2. Filter to unreviewed items (`review.reviewed == false`)
3. Present summary:

```
## Triage Review Session

**Pending reviews:** {count}
**Batches:** {list unique batch_ids}
**Priority breakdown:**
- P1 (Urgent): {count}
- P2 (High): {count}
- P3 (Normal): {count}
- P4 (Low): {count}

**By decision type:**
- Actionable (task created): {count}
- Actionable (no task): {count}
- Not actionable: {count}
```

4. Ask user how to proceed:
   - "Review all" - Go through everything
   - "Review by batch" - Pick a specific batch
   - "Review actionables only" - Focus on task-creating decisions
   - "Review non-actionables only" - Check for false negatives

---

## Phase 2: Quick Scan (Go/No-Go)

For each item, present a one-line summary:

```
## Item {n}/{total}: {triage_id}

**Issue:** [{severity}] {component} - {message_truncated}
**Decision:** {actionable ? "ACTIONABLE" : "IGNORED"} | {priority} | {category}
**Reasoning:** {reasoning_truncated}
```

Then ask:
- **"Looks fine"** - Mark as reviewed, verdict="correct", move to next
- **"Dig deeper"** - Go to deep review
- **"Flag for process review"** - Tag with "process-review", mark reviewed, move on
- **"Skip"** - Leave unreviewed, move to next

---

## Phase 3: Deep Review (Rubric)

When "Dig deeper" is selected, walk through each rubric criterion:

### Rubric Questions

**Q1: Priority Accuracy**
> Does the assigned priority ({priority}) match the actual severity?
- Correct
- Too high (over-escalated)
- Too low (under-escalated)

**Q2: Category Accuracy**
> Is "{category}" the right category for this issue?
- Correct
- Wrong (specify correct category)

**Q3: Actionability Decision**
> The AI decided this is {actionable ? "ACTIONABLE" : "NOT ACTIONABLE"}. Is that right?
- Correct
- False positive (said actionable but isn't)
- False negative (said not actionable but should be)

**Q4: Reasoning Quality**
> Does the AI's reasoning make sense?
> "{reasoning}"
- Sound reasoning
- Flawed logic
- Missing context
- Irrelevant justification

**Q5: Suggested Action Quality** (if actionable)
> Is the suggested action useful?
> "{suggested_action}"
- Helpful and specific
- Too vague
- Wrong approach
- N/A (not actionable)

**Q6: Overall Verdict**
- Correct - Triage was accurate
- Minor issues - Small problems, acceptable
- Incorrect - Significant triage error
- Needs tuning - Systemic issue to address

### Tags to Apply

After rubric, offer tagging options:
- `process-review` - Discuss in process improvement session
- `prompt-tuning` - Needs prompt adjustment
- `pattern-missing` - Add new detection pattern
- `pattern-wrong` - Fix existing pattern
- `edge-case` - Unusual situation, document it
- `model-issue` - Model capability limitation
- Custom tag (free text)

---

## Phase 4: Save Results

After each item review, update the triage log entry:

```json
"review": {
  "reviewed": true,
  "reviewed_at": "ISO timestamp",
  "verdict": "correct|minor_issues|incorrect|needs_tuning",
  "rubric": {
    "priority_accuracy": "correct|too_high|too_low",
    "category_accuracy": "correct|wrong",
    "actionability": "correct|false_positive|false_negative",
    "reasoning_quality": "sound|flawed|missing_context|irrelevant",
    "action_quality": "helpful|vague|wrong|na"
  },
  "notes": "any freeform notes",
  "tags": ["process-review", "pattern-missing"]
}
```

Write back to `/share/lumberjacker/triage-log.json` after each item.

---

## Phase 5: Session Report

At end of session (or when user says "done"), generate summary:

```
## Review Session Complete

**Reviewed this session:** {count}
**Remaining unreviewed:** {count}

### Verdicts
- Correct: {count} ({percent}%)
- Minor issues: {count}
- Incorrect: {count}
- Needs tuning: {count}

### Common Issues Found
- {list any patterns in incorrect verdicts}

### Tags Applied
- process-review: {count}
- prompt-tuning: {count}
- pattern-missing: {count}
- ...

### Recommended Actions
{Generate recommendations based on findings}
```

---

## Process Improvement Mode

When user says "process review" or "improve process":

1. Filter triage log for items tagged `process-review`
2. Group by tag type
3. For each group, discuss:
   - What pattern do these share?
   - What change would fix this category?
   - Priority of the fix

4. Generate improvement tasks:
   - Prompt changes to SYSTEM_PROMPT in ai_triage.py
   - New patterns to add to detection
   - Documentation updates

5. Save improvement decisions to `/share/lumberjacker/process-improvements.json`

---

## Commands During Review

- **"skip"** - Move to next item without reviewing
- **"done"** - End session, generate report
- **"stats"** - Show current session stats
- **"back"** - Re-review previous item
- **"tag {name}"** - Add tag to current item
- **"process"** - Switch to process improvement mode
- **"filter {criteria}"** - Filter remaining items

---

## File Locations

| File | Purpose |
|------|---------|
| `/share/lumberjacker/triage-log.json` | Triage decisions + reviews |
| `/share/lumberjacker/process-improvements.json` | Process improvement decisions |
| `/share/lumberjacker/review-sessions.json` | Historical session summaries |

---

## Example Session

```
User: /review-triage

LJA: ## Triage Review Session
**Pending reviews:** 12
**Batches:** batch-20260319-025100
...

How would you like to proceed?
[Review all] [Review by batch] [Actionables only] [Non-actionables only]

User: Review all

LJA: ## Item 1/12: tr-20260319-025102-abc123
**Issue:** [ERROR] hue - Unable to connect to bridge at 192.168.1.100
**Decision:** ACTIONABLE | P2 | integration
**Reasoning:** Repeated connection failures suggest config issue...

[Looks fine] [Dig deeper] [Flag for process] [Skip]

User: Looks fine

LJA: Marked as correct. Moving to next...

## Item 2/12: tr-20260319-025103-def456
...
```

## Remember

1. **Be thorough early** - Frequent reviews now save headaches later
2. **Tag generously** - Tags help spot patterns
3. **Process reviews matter** - The meta-improvement loop is key
4. **Document edge cases** - They become test cases
