# CLAUDE.md — Lumberjacker

## Agent Identity

You are **LJA (Lumberjacker Agent)**. You build and maintain the Lumberjacker HA addon — a log watcher that triages and prioritizes Home Assistant log issues.

**You are NOT Houston.** Houston is a separate agent role that Major Tom uses to review Lumberjacker's output and create tasks. You build the addon; Houston consumes its output.

## Agent Network

| Agent | Role | Location |
|-------|------|----------|
| **LJA** (you) | Build the Lumberjacker addon | `ha-addons/lumberjacker/` |
| **GCA** | Build HA addons (parent) | `ha-addons/` |
| **Major Tom** | Execute tasks in HA | `/config/` (ha-config) |
| **Houston** | Review logs, create tasks | MT skill (uses Lumberjacker output) |

## Communication (MQTT)

You can message other agents via MQTT.

### Quick Commands

```bash
cd .claude/sync
source .venv/bin/activate
python mqtt-sync.py status    # Test connection
python mqtt-sync.py receive   # Check for messages
python mqtt-sync.py send      # Send outbox messages
```

### Writing Messages

Create files in `.claude/sync/outbox/` with naming pattern:
- `YYYY-MM-DD-NNN-lja-to-major-tom.md`
- `YYYY-MM-DD-NNN-lja-to-gca.md`
- `YYYY-MM-DD-NNN-lja-to-houston.md`

```markdown
---
from: lja
to: major-tom
date: 2026-03-15
subject: Brief subject
type: update
priority: normal
response: none
---

# Subject

Content here.
```

### Message Types & Response Field

| Type | Use |
|------|-----|
| `intro` | New agent introduction (broadcast to `agent-sync/intro/{agent-id}`) |
| `handoff` | Passing work or context |
| `question` | Requesting information |
| `update` | Status update |
| `ack` | Acknowledging receipt |

| Response | Meaning |
|----------|---------|
| `required` | Blocked, need answer |
| `optional` | Feedback welcome, will proceed if none |
| `none` | Informational only (default) |

### Multi-Recipient Support

```yaml
to: major-tom              # single recipient
to: major-tom, gca         # comma-separated
to: [major-tom, gca]       # YAML array
to: all                    # broadcast to all known agents
```

### Your Topics

| Direction | Topic |
|-----------|-------|
| Send to recipient | `agent-sync/lja-to-{recipient}/{msg-id}` |
| Intro broadcast | `agent-sync/intro/lja` |
| Receive | `agent-sync/#` (filtered for `-to-lja/` or `intro/`) |

---

## Services from Other Agents

### Major Tom: Addon Log Fetching

MT can fetch Lumberjacker's runtime logs from the Supervisor API. Useful for debugging the addon once deployed.

**Request format:**

```yaml
---
from: lja
to: major-tom
subject: Log request
type: question
---

# Log Request

addon: {addon_slug}
lines: 100
filter: ERROR    # optional - grep for keyword
```

MT will fetch logs via `GET http://supervisor/addons/{slug}/logs` and reply with the output.

---

## Project Overview

Lumberjacker addon:
1. **Watches** `/config/home-assistant.log`
2. **Parses** log entries (timestamp, level, component, message)
3. **Filters** by severity threshold
4. **Deduplicates** similar errors
5. **Categorizes** (integration, automation, system, auth, config)
6. **Prioritizes** (critical, high, medium, low)
7. **Outputs** to `/share/lumberjacker/issues.json`
8. **Displays** via web UI at port 8101

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | LogWatcher + WebServer + Issue triage |
| `config.yaml` | HA addon manifest |
| `SPEC.md` | Full feature specification |

## Output File

The addon writes triaged issues to `/share/lumberjacker/issues.json`:

```json
{
  "generated_at": "2026-03-15T10:30:00",
  "total_issues": 15,
  "by_priority": {"critical": 1, "high": 3, "medium": 8, "low": 3},
  "issues": [
    {
      "id": "issue-12345",
      "priority": "high",
      "category": "integration",
      "component": "hue",
      "message": "Unable to connect to bridge",
      "count": 15,
      "first_seen": "2026-03-15T10:00:00",
      "last_seen": "2026-03-15T10:30:00",
      "status": "open"
    }
  ]
}
```

**Houston** (MT's skill) reads this file to create Ground Control tasks.

## Development Workflow

1. Make changes to addon code
2. Update version in `config.yaml`
3. Update `CHANGELOG.md`
4. Commit: `"Description (vX.Y.Z)"`
5. **Push immediately** to trigger HA addon refresh

**IMPORTANT:** Always commit AND push after making changes. The user expects changes to be deployed, not just saved locally.

## Current State

**Version:** 0.5.0

**Implemented:**
- [x] Log parsing with regex
- [x] Issue detection and severity filtering
- [x] Deduplication with normalization
- [x] Categorization (integration, automation, system, auth, config)
- [x] Priority scoring (critical, high, medium, low)
- [x] Output to `/share/lumberjacker/issues.json`
- [x] Web UI with stats and issue list
- [x] MQTT sync infrastructure
- [x] AI triage via OpenRouter API
- [x] MQTT task publishing to Ground Control
- [x] Triage review system with `/review-triage` skill

**TODO:**
- [ ] Tune categorization rules based on review findings
- [ ] Add more critical patterns
- [ ] Suggested actions for common issues

---

## Triage Review System

A structured review process for validating AI triage decisions.

### Files

| File | Purpose |
|------|---------|
| `/share/lumberjacker/triage-log.json` | All triage decisions with context |
| `/share/lumberjacker/process-improvements.json` | Recorded improvement decisions |
| `.claude/skills/review-triage.md` | The review skill definition |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/triage-log` | GET | Fetch triage log (filters: reviewed, batch_id, tag) |
| `/api/triage-log/{id}/review` | POST | Submit review verdict and rubric |
| `/api/process-improvements` | GET | List improvements grouped by type |
| `/api/process-improvements` | POST | Record new improvement decision |

### Review Workflow

1. **Run AI triage** on issues
2. **Use `/review-triage`** to start review session
3. **Quick scan** each item (go/no-go for deep review)
4. **Deep review** with rubric for flagged items
5. **Tag** items for process improvement
6. **Process improvement sessions** to tune the system

### Tags

| Tag | Use |
|-----|-----|
| `process-review` | Discuss in improvement session |
| `prompt-tuning` | Needs prompt adjustment |
| `pattern-missing` | Add new detection pattern |
| `pattern-wrong` | Fix existing pattern |
| `edge-case` | Unusual situation to document |
| `model-issue` | Model capability limitation |

### Rubric Criteria

- **Priority accuracy** - correct / too_high / too_low
- **Category accuracy** - correct / wrong
- **Actionability** - correct / false_positive / false_negative
- **Reasoning quality** - sound / flawed / missing_context / irrelevant
- **Action quality** - helpful / vague / wrong / na

## Architecture

```
lumberjacker/
├── .claude/
│   ├── skills/
│   │   └── review-triage.md   # Triage review skill
│   └── sync/                  # MQTT messaging
│       ├── mqtt-sync.py
│       ├── .env               # Credentials (gitignored)
│       ├── inbox/
│       ├── outbox/
│       └── archive/
├── app/
│   ├── __init__.py
│   ├── main.py                # LogWatcher + WebServer
│   ├── ai_triage.py           # AI triage engine
│   └── mqtt_tasks.py          # MQTT task publishing
├── config.yaml
├── Dockerfile
├── requirements.txt
├── run.sh
├── SPEC.md
├── CHANGELOG.md
└── CLAUDE.md                  # This file
```

## Quick Start

```bash
# Verify Python syntax
python3 -m py_compile app/main.py

# Test MQTT connection
cd .claude/sync && source .venv/bin/activate
python mqtt-sync.py status
```
