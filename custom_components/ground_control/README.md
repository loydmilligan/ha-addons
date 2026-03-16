# Ground Control Integration

Home Assistant custom integration for Ground Control task management.

## Installation

Copy the `ground_control` folder to your Home Assistant config directory:

```bash
cp -r ground_control /config/custom_components/
```

Or from inside HA:
```bash
cp -r /addons/local/ground-control/integration/ground_control /config/custom_components/
```

Then restart Home Assistant.

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "Ground Control"
3. Enter the addon URL (default: `http://localhost:8100`)

## Entities

### Sensors
- `sensor.ground_control_active_count` - Tasks in Active bucket
- `sensor.ground_control_work_queue_count` - Tasks in Work Queue
- `sensor.ground_control_total_open` - All non-completed tasks
- `sensor.ground_control_completed_count` - Completed tasks
- `sensor.ground_control_blocked_count` - Blocked tasks
- `sensor.ground_control_project_{slug}_status` - Per-project status
- `sensor.ground_control_project_{slug}_open_tasks` - Per-project open tasks
- `sensor.ground_control_project_{slug}_progress` - Per-project progress %

### Binary Sensors
- `binary_sensor.ground_control_has_active` - True if any active task
- `binary_sensor.ground_control_has_blocked` - True if any blocked task

## Services

### Task Management
- `ground_control.create_task` - Create a new task
- `ground_control.update_task` - Update task details
- `ground_control.move_task` - Move task between buckets
- `ground_control.complete_task` - Mark task as completed
- `ground_control.delete_task` - Delete a task

### Project Management
- `ground_control.create_project` - Create a new project
- `ground_control.update_project` - Update project details
- `ground_control.archive_project` - Archive a project

## Example Service Calls

```yaml
# Create a task
service: ground_control.create_task
data:
  subject: "Fix kitchen light"
  bucket: planning
  project: reorg

# Move task to work queue
service: ground_control.move_task
data:
  task_id: "T-001"
  target_bucket: work_queue

# Complete a task
service: ground_control.complete_task
data:
  task_id: "T-001"
```

## Dashboard Cards

Use the sensors in standard HA cards:

```yaml
type: entities
entities:
  - entity: sensor.ground_control_active_count
  - entity: sensor.ground_control_work_queue_count
  - entity: sensor.ground_control_total_open
  - entity: binary_sensor.ground_control_has_blocked
```
