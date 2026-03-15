"""Parser for .tasks/ markdown files with YAML frontmatter."""

import re
import yaml
from pathlib import Path
from typing import Tuple, Dict, List, Optional
from datetime import date

from models import Task, Project, BucketsFile, BUCKETS


def parse_frontmatter(content: str) -> Tuple[dict, str]:
    """
    Split YAML frontmatter from markdown content.
    Returns (frontmatter_dict, markdown_body).
    """
    if not content.startswith("---"):
        return {}, content

    # Find the closing ---
    end_match = re.search(r"\n---\s*\n", content[3:])
    if not end_match:
        return {}, content

    end_pos = end_match.end() + 3
    yaml_content = content[3 : end_match.start() + 3]
    markdown_body = content[end_pos:]

    try:
        frontmatter = yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, markdown_body


def parse_task_line(line: str, bucket: str) -> Optional[Task]:
    """
    Parse a single task line from buckets.md.

    Formats:
    - [T-001] Subject text (project: slug) (blocked by: T-002)
    - **2026-03-15**: [T-001] Subject text (project: slug)
    - Subject text (project: slug)  # No ID yet
    """
    line = line.strip()
    if not line.startswith("- "):
        return None

    line = line[2:]  # Remove "- " prefix

    # Skip empty markers
    if line in ("— empty —", ""):
        return None

    task = Task(id="", subject="", bucket=bucket)

    # Check for completed date prefix: **YYYY-MM-DD**:
    completed_match = re.match(r"\*\*(\d{4}-\d{2}-\d{2})\*\*:\s*", line)
    if completed_match:
        task.completed_date = completed_match.group(1)
        line = line[completed_match.end() :]

    # Check for task ID: [T-XXX]
    id_match = re.match(r"\[([Tt]-\d+)\]\s*", line)
    if id_match:
        task.id = id_match.group(1).upper()
        line = line[id_match.end() :]

    # Check for blocked by: (blocked by: T-XXX, T-YYY)
    blocked_match = re.search(r"\(blocked by:\s*([^)]+)\)\s*$", line)
    if blocked_match:
        blocked_ids = [b.strip().upper() for b in blocked_match.group(1).split(",")]
        task.blocked_by = blocked_ids
        line = line[: blocked_match.start()].strip()

    # Check for project: (project: slug)
    project_match = re.search(r"\(project:\s*([^)]+)\)\s*$", line)
    if project_match:
        task.project = project_match.group(1).strip()
        line = line[: project_match.start()].strip()

    # Remaining text is the subject
    task.subject = line.strip()

    if not task.subject:
        return None

    return task


def parse_buckets_file(path: str) -> BucketsFile:
    """Parse buckets.md file."""
    content = Path(path).read_text()
    frontmatter, body = parse_frontmatter(content)

    buckets_file = BucketsFile(
        version=frontmatter.get("version", "1.0.0"),
        next_id=frontmatter.get("next_id", 1),
        created=frontmatter.get("created", ""),
        updated=frontmatter.get("updated", ""),
        task_count=frontmatter.get("task_count", {}),
        tasks={bucket: [] for bucket in BUCKETS},
    )

    # Parse markdown body
    current_bucket = None
    bucket_map = {
        "active": "active",
        "work queue": "work_queue",
        "completed": "completed",
        "cleanup": "cleanup",
        "investigation": "investigation",
        "planning": "planning",
        "brainstorm": "brainstorm",
    }

    for line in body.split("\n"):
        # Check for bucket header
        header_match = re.match(r"^##\s+(.+)$", line)
        if header_match:
            header_text = header_match.group(1).strip().lower()
            current_bucket = bucket_map.get(header_text)
            continue

        # Parse task lines
        if current_bucket and line.strip().startswith("- "):
            task = parse_task_line(line, current_bucket)
            if task:
                buckets_file.tasks[current_bucket].append(task)

    # Update counts
    buckets_file.update_counts()

    return buckets_file


def parse_project_file(path: str) -> Project:
    """Parse a project file (projects/*.md)."""
    content = Path(path).read_text()
    frontmatter, body = parse_frontmatter(content)

    project = Project(
        slug=frontmatter.get("slug", Path(path).stem),
        name=frontmatter.get("title", "").replace("Project: ", ""),
        status=frontmatter.get("status", "not_started"),
        goal=frontmatter.get("goal", ""),
        description="",
    )

    return project


def parse_all_projects(tasks_path: str) -> Dict[str, Project]:
    """Parse all project files in the projects directory."""
    projects_dir = Path(tasks_path) / "projects"
    projects = {}

    if not projects_dir.exists():
        return projects

    for project_file in projects_dir.glob("*.md"):
        try:
            project = parse_project_file(str(project_file))
            projects[project.slug] = project
        except Exception as e:
            print(f"Error parsing project {project_file}: {e}")

    return projects


def load_task_state(tasks_path: str) -> "TaskState":
    """Load complete task state from .tasks/ directory."""
    from models import TaskState

    state = TaskState()

    # Load buckets
    buckets_path = Path(tasks_path) / "buckets.md"
    if buckets_path.exists():
        state.buckets = parse_buckets_file(str(buckets_path))

    # Load projects
    state.projects = parse_all_projects(tasks_path)

    return state
