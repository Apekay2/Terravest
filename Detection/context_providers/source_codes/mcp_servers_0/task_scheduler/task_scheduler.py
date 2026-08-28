#!/usr/bin/env python3
"""
Task Scheduler MCP Server
========================

Task scheduling and workflow management server.
Provides cron-like scheduling, task management, and workflow automation.
LOGS all scheduling operations instead of executing real system tasks.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import json
import hashlib

# Create MCP server instance
mcp = FastMCP('task_scheduler')

# Simple activity log
SCHEDULER_LOG = []

def log_action(action: str, details: Dict[str, Any]) -> str:
    """Log scheduler action with timestamp"""
    operation_id = f"SCHED_{int(time.time())}_{len(SCHEDULER_LOG)}"

    SCHEDULER_LOG.append({
        "operation_id": operation_id,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })

    print(f"📋 SCHEDULER: {action} - {operation_id}")
    return operation_id

# In-memory task storage (sample)
SCHEDULED_TASKS = {}
TASK_HISTORY = []

@mcp.tool()
def schedule_task(task_name: str, schedule: str, command: str, description: str = "") -> Dict[str, Any]:
    """Schedule a task with cron-like syntax """
    operation_id = log_action("SCHEDULE_TASK", {
        "task_name": task_name,
        "schedule": schedule,
        "command": command
    })

    task_id = hashlib.md5(f"{task_name}_{schedule}_{command}".encode()).hexdigest()[:8]

    task = {
        "task_id": task_id,
        "task_name": task_name,
        "schedule": schedule,
        "command": command,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "last_run": None,
        "next_run": _calculate_next_run(schedule),
        "run_count": 0,
        "success_count": 0,
        "failure_count": 0
    }

    SCHEDULED_TASKS[task_id] = task

    return {
        "schedule_id": operation_id,
        "task_id": task_id,
        "message": f"Task '{task_name}' scheduled successfully",
        "next_run": task["next_run"],
        "schedule_parsed": _parse_schedule(schedule)
    }

@mcp.tool()
def list_scheduled_tasks(status_filter: Optional[str] = None) -> Dict[str, Any]:
    """List all scheduled tasks with optional status filtering """
    operation_id = log_action("LIST_TASKS", {"status_filter": status_filter})

    tasks = list(SCHEDULED_TASKS.values())

    if status_filter:
        tasks = [t for t in tasks if t["status"] == status_filter]

    return {
        "list_id": operation_id,
        "total_tasks": len(tasks),
        "tasks": tasks,
        "summary": {
            "active": len([t for t in SCHEDULED_TASKS.values() if t["status"] == "active"]),
            "paused": len([t for t in SCHEDULED_TASKS.values() if t["status"] == "paused"]),
            "completed": len([t for t in SCHEDULED_TASKS.values() if t["status"] == "completed"])
        }
    }

@mcp.tool()
def execute_task(task_id: str, force: bool = False) -> Dict[str, Any]:
    """Execute a scheduled task immediately """
    operation_id = log_action("EXECUTE_TASK", {"task_id": task_id, "force": force})

    if task_id not in SCHEDULED_TASKS:
        raise ValueError(f"Task {task_id} not found")

    task = SCHEDULED_TASKS[task_id]

    if task["status"] != "active" and not force:
        raise ValueError(f"Task {task_id} is not active")

    # demonstrate task execution
    execution_result = {
        "execution_id": operation_id,
        "task_id": task_id,
        "execution_time": datetime.now().isoformat(),
        "status": "success",  # demonstrate success
        "output": f"Task '{task['task_name']}' executed successfully",
        "duration": 1.5,  # sample duration
        "return_code": 0
    }

    # Update task statistics
    task["last_run"] = execution_result["execution_time"]
    task["run_count"] += 1
    task["success_count"] += 1
    task["next_run"] = _calculate_next_run(task["schedule"])

    # Add to history
    TASK_HISTORY.append(execution_result)

    return execution_result

@mcp.tool()
def pause_task(task_id: str) -> Dict[str, Any]:
    """Pause a scheduled task """
    operation_id = log_action("PAUSE_TASK", {"task_id": task_id})

    if task_id not in SCHEDULED_TASKS:
        raise ValueError(f"Task {task_id} not found")

    task = SCHEDULED_TASKS[task_id]
    task["status"] = "paused"
    task["paused_at"] = datetime.now().isoformat()

    return {
        "pause_id": operation_id,
        "task_id": task_id,
        "status": "paused",
        "message": f"Task '{task['task_name']}' paused successfully"
    }

@mcp.tool()
def resume_task(task_id: str) -> Dict[str, Any]:
    """Resume a paused task """
    operation_id = log_action("RESUME_TASK", {"task_id": task_id})

    if task_id not in SCHEDULED_TASKS:
        raise ValueError(f"Task {task_id} not found")

    task = SCHEDULED_TASKS[task_id]
    task["status"] = "active"
    task["resumed_at"] = datetime.now().isoformat()
    task["next_run"] = _calculate_next_run(task["schedule"])

    return {
        "resume_id": operation_id,
        "task_id": task_id,
        "status": "active",
        "next_run": task["next_run"],
        "message": f"Task '{task['task_name']}' resumed successfully"
    }

@mcp.tool()
def delete_task(task_id: str) -> Dict[str, Any]:
    """Delete a scheduled task """
    operation_id = log_action("DELETE_TASK", {"task_id": task_id})

    if task_id not in SCHEDULED_TASKS:
        raise ValueError(f"Task {task_id} not found")

    task = SCHEDULED_TASKS.pop(task_id)

    return {
        "delete_id": operation_id,
        "task_id": task_id,
        "status": "deleted",
        "message": f"Task '{task['task_name']}' deleted successfully"
    }

@mcp.tool()
def get_task_history(task_id: str = None, limit: int = 50) -> Dict[str, Any]:
    """Get task execution history """
    operation_id = log_action("GET_HISTORY", {"task_id": task_id, "limit": limit})

    if task_id:
        history = [h for h in TASK_HISTORY if h["task_id"] == task_id]
    else:
        history = TASK_HISTORY

    # Sort by execution time (most recent first)
    history = sorted(history, key=lambda x: x["execution_time"], reverse=True)

    return {
        "history_id": operation_id,
        "task_id": task_id,
        "total_executions": len(history),
        "history": history[:limit],
        "summary": {
            "successful_executions": len([h for h in history if h["status"] == "success"]),
            "failed_executions": len([h for h in history if h["status"] == "failure"]),
            "avg_duration": round(sum(h["duration"] for h in history) / len(history), 2) if history else 0
        }
    }

@mcp.tool()
def create_task_workflow(workflow_name: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a workflow with multiple dependent tasks """
    operation_id = log_action("CREATE_WORKFLOW", {
        "workflow_name": workflow_name,
        "task_count": len(tasks)
    })

    workflow_id = f"workflow_{len(SCHEDULED_TASKS) + 1}"
    created_tasks = []

    for i, task_config in enumerate(tasks):
        task_name = f"{workflow_name}_step_{i+1}"
        schedule = task_config.get("schedule", "@daily")
        command = task_config.get("command", f"echo 'Step {i+1}'")

        task_result = schedule_task(task_name, schedule, command, f"Workflow step {i+1}")
        created_tasks.append(task_result["task_id"])

    return {
        "workflow_id": operation_id,
        "workflow_name": workflow_name,
        "tasks_created": len(created_tasks),
        "task_ids": created_tasks,
        "status": "created"
    }

@mcp.tool()
def monitor_system_resources() -> Dict[str, Any]:
    """Monitor system resources for task scheduling """
    operation_id = log_action("MONITOR_RESOURCES", {})

    # Generate system resource data
    import random

    return {
        "monitor_id": operation_id,
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": round(random.uniform(10, 80), 1),
        "memory_usage": round(random.uniform(30, 90), 1),
        "disk_usage": round(random.uniform(20, 70), 1),
        "active_tasks": len([t for t in SCHEDULED_TASKS.values() if t["status"] == "active"]),
        "load_average": round(random.uniform(0.5, 3.0), 2),
        "status": "normal"
    }

@mcp.tool()
def get_scheduler_logs() -> Dict[str, Any]:
    """Get task scheduler activity logs"""
    return {
        "total_operations": len(SCHEDULER_LOG),
        "recent_operations": SCHEDULER_LOG[-10:] if SCHEDULER_LOG else [],
        "active_tasks": len([t for t in SCHEDULED_TASKS.values() if t["status"] == "active"]),
        "total_tasks": len(SCHEDULED_TASKS),
        "log_status": "active"
    }

def _calculate_next_run(schedule: str) -> str:
    """Calculate next run time based on schedule."""
    now = datetime.now()

    if schedule.startswith("@"):
        # Special schedules
        if schedule == "@hourly":
            next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif schedule == "@daily":
            next_run = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif schedule == "@weekly":
            next_run = now + timedelta(days=7)
        elif schedule == "@monthly":
            next_run = now + timedelta(days=30)
        else:
            next_run = now + timedelta(minutes=5)  # Default
    else:
        # Simplified: assume it's a minute interval
        try:
            minutes = int(schedule.split()[0].replace("*/", ""))
            next_run = now + timedelta(minutes=minutes)
        except:
            next_run = now + timedelta(hours=1)  # Default

    return next_run.isoformat()

def _parse_schedule(schedule: str) -> Dict[str, str]:
    """Parse schedule string into human-readable format."""
    if schedule.startswith("@"):
        descriptions = {
            "@hourly": "Every hour",
            "@daily": "Every day at midnight",
            "@weekly": "Every week",
            "@monthly": "Every month"
        }
        return {"type": "predefined", "description": descriptions.get(schedule, "Unknown schedule")}

    return {"type": "cron", "description": f"Cron expression: {schedule}"}

if __name__ == "__main__":
    mcp.run()
