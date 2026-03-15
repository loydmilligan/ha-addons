"""Data models for Ground Control task management."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import date


# Valid buckets in workflow order
BUCKETS = [
    "active",
    "work_queue",
    "completed",
    "cleanup",
    "investigation",
    "planning",
    "brainstorm",
]

# Valid bucket transitions (from -> [allowed destinations])
VALID_TRANSITIONS = {
    "brainstorm": ["planning"],
    "planning": ["work_queue"],
    "cleanup": ["work_queue", "planning"],
    "investigation": ["work_queue", "planning"],
    "work_queue": ["active"],
    "active": ["completed", "work_queue"],
    "completed": [],  # No transitions from completed
}

# Project statuses
PROJECT_STATUSES = ["not_started", "in_progress", "complete", "archived"]


@dataclass
class Task:
    """A single task/work item."""

    id: str  # T-001 format
    subject: str
    bucket: str = "brainstorm"
    project: str = ""
    description: str = ""
    created_date: str = ""
    completed_date: str = ""
    blocked_by: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "subject": self.subject,
            "bucket": self.bucket,
            "project": self.project,
            "description": self.description,
            "created_date": self.created_date,
            "completed_date": self.completed_date,
            "blocked_by": self.blocked_by,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data.get("id", ""),
            subject=data.get("subject", ""),
            bucket=data.get("bucket", "brainstorm"),
            project=data.get("project", ""),
            description=data.get("description", ""),
            created_date=data.get("created_date", ""),
            completed_date=data.get("completed_date", ""),
            blocked_by=data.get("blocked_by", []),
            tags=data.get("tags", []),
        )

    def is_blocked(self) -> bool:
        return len(self.blocked_by) > 0

    def can_move_to(self, target_bucket: str) -> bool:
        """Check if task can be moved to target bucket."""
        if target_bucket not in BUCKETS:
            return False
        if self.bucket == target_bucket:
            return True  # No change
        return target_bucket in VALID_TRANSITIONS.get(self.bucket, [])


@dataclass
class Project:
    """A project grouping related tasks."""

    slug: str
    name: str
    status: str = "not_started"
    goal: str = ""
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "name": self.name,
            "status": self.status,
            "goal": self.goal,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            slug=data.get("slug", ""),
            name=data.get("name", ""),
            status=data.get("status", "not_started"),
            goal=data.get("goal", ""),
            description=data.get("description", ""),
        )


@dataclass
class BucketsFile:
    """Represents the parsed buckets.md file."""

    version: str = "1.0.0"
    next_id: int = 1
    created: str = ""
    updated: str = ""
    task_count: Dict[str, int] = field(default_factory=dict)
    tasks: Dict[str, List[Task]] = field(default_factory=dict)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all buckets."""
        all_tasks = []
        for bucket_tasks in self.tasks.values():
            all_tasks.extend(bucket_tasks)
        return all_tasks

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Find a task by ID."""
        for bucket_tasks in self.tasks.values():
            for task in bucket_tasks:
                if task.id == task_id:
                    return task
        return None

    def update_counts(self):
        """Update task_count to match actual task counts."""
        self.task_count = {}
        for bucket in BUCKETS:
            self.task_count[bucket] = len(self.tasks.get(bucket, []))

    def assign_next_id(self) -> str:
        """Get the next task ID and increment counter."""
        task_id = f"T-{self.next_id:03d}"
        self.next_id += 1
        return task_id


@dataclass
class TaskState:
    """Complete task management state."""

    buckets: BucketsFile = field(default_factory=BucketsFile)
    projects: Dict[str, Project] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "version": self.buckets.version,
            "next_id": self.buckets.next_id,
            "task_count": self.buckets.task_count,
            "buckets": {
                bucket: [t.to_dict() for t in tasks]
                for bucket, tasks in self.buckets.tasks.items()
            },
            "projects": {
                slug: p.to_dict() for slug, p in self.projects.items()
            },
        }
