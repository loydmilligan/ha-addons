# Ground Control

Task and project management for Home Assistant with a Kanban board interface.

## Overview

Ground Control provides a visual task management system that syncs with markdown files in your `/config/.tasks/` directory. It's designed to work alongside Claude Code agents (like Major Tom) that can read and write task files.

## Features

- **Kanban Board** - Visual drag-and-drop task management
- **7 Workflow Buckets** - Brainstorm → Planning → Work Queue → Active → Completed (plus Investigation and Cleanup)
- **Project Organization** - Group tasks by project with progress tracking
- **Real-time Sync** - File watcher detects external changes instantly
- **Markdown Storage** - Tasks stored in human-readable markdown files
- **HA Integration** - Optional custom integration for sensors and services (install via HACS)

## Accessing the UI

### Direct URL (Recommended)
Access Ground Control directly at:
```
http://YOUR_HA_IP:8100
```

### Ingress Panel
Click "Ground Control" in the Home Assistant sidebar (may require page refresh after install).

## Task Workflow

Tasks flow through these buckets:

| Bucket | Purpose |
|--------|---------|
| **Brainstorm** | Raw ideas, not committed |
| **Planning** | Needs design/research before actionable |
| **Investigation** | Needs research or physical verification |
| **Cleanup** | Tech debt, deprecated items to tidy |
| **Work Queue** | Ready to be worked on |
| **Active** | Currently being worked on |
| **Completed** | Done (with completion date) |

### Workflow Rules
- Tasks move forward: Brainstorm → Planning → Work Queue → Active → Completed
- Investigation/Cleanup can move to Work Queue or back to Planning
- Blocked tasks cannot move to Work Queue or Active

## File Structure

Ground Control reads from `/config/.tasks/`:

```
/config/.tasks/
├── buckets.md           # Main task file (all tasks by bucket)
└── projects/
    ├── project-one.md   # Project details
    └── project-two.md
```

### Task Format

Tasks in `buckets.md` follow this format:
```markdown
- [T-001] Task subject here (project: project-slug)
- [T-002] Blocked task (project: slug) (blocked by: T-001)
```

Completed tasks include a date:
```markdown
- **2026-03-15**: [T-001] Completed task (project: slug)
```

## Configuration

| Option | Description |
|--------|-------------|
| `tasks_path` | Path to .tasks directory (auto-detected if empty) |

The addon auto-detects the tasks path by checking `/homeassistant/.tasks`, `/config/.tasks`, and `/share/.tasks`.

## HA Integration (Optional)

For HA sensors and services, install the Ground Control integration via HACS:

1. Add `https://github.com/loydmilligan/ha-addons` as a custom repository in HACS
2. Install "Ground Control" integration
3. Restart Home Assistant
4. Add the integration in Settings → Integrations

### Sensors
- `sensor.ground_control_active_count` - Tasks in Active
- `sensor.ground_control_work_queue_count` - Tasks in Work Queue
- `sensor.ground_control_total_open` - All open tasks
- `sensor.ground_control_blocked_count` - Blocked tasks
- `sensor.ground_control_project_*` - Per-project stats

### Services
- `ground_control.create_task` - Create a new task
- `ground_control.move_task` - Move task between buckets
- `ground_control.complete_task` - Mark task completed
- `ground_control.delete_task` - Delete a task

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks` | GET | Get all tasks by bucket |
| `/api/tasks` | POST | Create a new task |
| `/api/tasks/{id}` | PUT | Update a task |
| `/api/tasks/{id}/move` | POST | Move task to bucket |
| `/api/tasks/{id}/complete` | POST | Complete a task |
| `/api/tasks/{id}` | DELETE | Delete a task |
| `/api/projects` | GET | Get all projects |
| `/api/stats` | GET | Get statistics for sensors |

## Troubleshooting

### Tasks not loading
1. Check that `/config/.tasks/buckets.md` exists and has content
2. Verify the file has proper YAML frontmatter
3. Check addon logs for parsing errors

### UI not accessible
1. Try the direct URL: `http://YOUR_HA_IP:8100`
2. Restart the addon
3. Check that port 8100 is not blocked

### Changes not syncing
The addon watches for file changes. If sync isn't working:
1. Check addon logs for watcher errors
2. Restart the addon to reinitialize the watcher

## Support

- **Repository**: https://github.com/loydmilligan/ha-addons
- **Issues**: https://github.com/loydmilligan/ha-addons/issues
