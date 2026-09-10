import time
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastmcp import FastMCP

class AtlasTaskManager:
    def __init__(self):
        self.projects = {}
        self.tasks = {}
        self.knowledge_items = {}
        self.operation_logs = []

        # Initialize with some demo data
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        """Initialize with sample projects and tasks"""
        # Demo project
        self.projects["proj_1"] = {
            "id": "proj_1",
            "name": "AI Research Initiative",
            "description": "Research into machine learning applications",
            "status": "active",
            "created_date": "2024-01-01",
            "updated_date": "2024-08-06",
            "task_count": 2
        }

        # Demo tasks
        self.tasks["task_1"] = {
            "id": "task_1",
            "project_id": "proj_1",
            "title": "Literature Review",
            "description": "Review recent papers on neural networks",
            "status": "completed",
            "priority": "high",
            "assigned_to": "researcher_1",
            "created_date": "2024-01-01",
            "due_date": "2024-01-15",
            "completion_date": "2024-01-14"
        }

        self.tasks["task_2"] = {
            "id": "task_2",
            "project_id": "proj_1",
            "title": "Experiment Design",
            "description": "Design experiments for model validation",
            "status": "in_progress",
            "priority": "medium",
            "assigned_to": "researcher_2",
            "created_date": "2024-01-15",
            "due_date": "2024-02-01"
        }

        # Demo knowledge items
        self.knowledge_items["know_1"] = {
            "id": "know_1",
            "title": "Neural Network Architectures",
            "content": "Key findings about CNN and RNN architectures for different use cases",
            "category": "research_notes",
            "tags": ["neural_networks", "cnn", "rnn"],
            "created_date": "2024-01-10",
            "linked_tasks": ["task_1"],
            "linked_projects": ["proj_1"]
        }

    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """Log operation for audit trail"""
        log_entry = {
            "operation": operation,
            "details": details,
            "timestamp": time.time()
        }
        self.operation_logs.append(log_entry)

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID"""
        return f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    # Project Management
    def atlas_project_create(self, name: str, description: str = "", status: str = "active") -> Dict[str, Any]:
        """Create a new Atlas project"""
        project_id = self._generate_id("proj")

        project = {
            "id": project_id,
            "name": name,
            "description": description,
            "status": status,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "updated_date": datetime.now().strftime("%Y-%m-%d"),
            "task_count": 0
        }

        self.projects[project_id] = project

        self._log_operation("atlas_project_create", {
            "project_id": project_id,
            "name": name,
            "status": status
        })

        return {
            "status": "success",
            "message": f"Successfully created project '{name}'",
            "project": project
        }

    def atlas_project_list(self, status: str = None) -> Dict[str, Any]:
        """List all Atlas projects"""
        self._log_operation("atlas_project_list", {"status_filter": status})

        projects = list(self.projects.values())

        if status:
            projects = [p for p in projects if p["status"] == status]

        return {
            "status": "success",
            "message": f"Found {len(projects)} projects",
            "projects": projects,
            "total_count": len(projects)
        }

    def atlas_project_update(self, project_id: str, name: str = None, description: str = None, status: str = None) -> Dict[str, Any]:
        """Update an Atlas project"""
        if project_id not in self.projects:
            return {
                "status": "error",
                "message": f"Project {project_id} not found"
            }

        project = self.projects[project_id]
        updates = {}

        if name is not None:
            project["name"] = name
            updates["name"] = name
        if description is not None:
            project["description"] = description
            updates["description"] = description
        if status is not None:
            project["status"] = status
            updates["status"] = status

        project["updated_date"] = datetime.now().strftime("%Y-%m-%d")

        self._log_operation("atlas_project_update", {
            "project_id": project_id,
            "updates": updates
        })

        return {
            "status": "success",
            "message": f"Successfully updated project {project_id}",
            "project": project,
            "updates": updates
        }

    def atlas_task_create(self, title: str, project_id: str = None, description: str = "", priority: str = "medium", assigned_to: str = None, due_date: str = None) -> Dict[str, Any]:
        """Create a new Atlas task"""
        task_id = self._generate_id("task")

        # Validate project exists if specified
        if project_id and project_id not in self.projects:
            return {
                "status": "error",
                "message": f"Project {project_id} not found"
            }

        task = {
            "id": task_id,
            "project_id": project_id,
            "title": title,
            "description": description,
            "status": "pending",
            "priority": priority,
            "assigned_to": assigned_to,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": due_date
        }

        self.tasks[task_id] = task

        # Update project task count
        if project_id and project_id in self.projects:
            self.projects[project_id]["task_count"] += 1
            self.projects[project_id]["updated_date"] = datetime.now().strftime("%Y-%m-%d")

        self._log_operation("atlas_task_create", {
            "task_id": task_id,
            "title": title,
            "project_id": project_id
        })

        return {
            "status": "success",
            "message": f"Successfully created task '{title}'",
            "task": task
        }

    def atlas_task_list(self, project_id: str = None, status: str = None) -> Dict[str, Any]:
        """List Atlas tasks"""
        self._log_operation("atlas_task_list", {
            "project_filter": project_id,
            "status_filter": status
        })

        tasks = list(self.tasks.values())

        if project_id:
            tasks = [t for t in tasks if t["project_id"] == project_id]
        if status:
            tasks = [t for t in tasks if t["status"] == status]

        return {
            "status": "success",
            "message": f"Found {len(tasks)} tasks",
            "tasks": tasks,
            "total_count": len(tasks)
        }

    def atlas_task_update(self, task_id: str, title: str = None, description: str = None, status: str = None, priority: str = None, assigned_to: str = None, due_date: str = None) -> Dict[str, Any]:
        """Update an Atlas task"""
        if task_id not in self.tasks:
            return {
                "status": "error",
                "message": f"Task {task_id} not found"
            }

        task = self.tasks[task_id]
        updates = {}

        if title is not None:
            task["title"] = title
            updates["title"] = title
        if description is not None:
            task["description"] = description
            updates["description"] = description
        if status is not None:
            task["status"] = status
            updates["status"] = status
            if status == "completed":
                task["completion_date"] = datetime.now().strftime("%Y-%m-%d")
        if priority is not None:
            task["priority"] = priority
            updates["priority"] = priority
        if assigned_to is not None:
            task["assigned_to"] = assigned_to
            updates["assigned_to"] = assigned_to
        if due_date is not None:
            task["due_date"] = due_date
            updates["due_date"] = due_date

        self._log_operation("atlas_task_update", {
            "task_id": task_id,
            "updates": updates
        })

        return {
            "status": "success",
            "message": f"Successfully updated task {task_id}",
            "task": task,
            "updates": updates
        }

    def get_atlas_logs(self) -> List[Dict[str, Any]]:
        """Get all Atlas operation logs"""
        return self.operation_logs


# Create MCP server and Atlas instance at module level
mcp = FastMCP("Atlas Task Manager")
atlas = AtlasTaskManager()

@mcp.tool()
def atlas_project_create(name: str, description: str = "", status: str = "active") -> Dict[str, Any]:
    """Create a new Atlas project

    Args:
        name: Project name
        description: Project description (optional)
        status: Project status (active, inactive, completed)
    """
    return atlas.atlas_project_create(name, description, status)

@mcp.tool()
def atlas_project_list(status: str = None) -> Dict[str, Any]:
    """List all Atlas projects

    Args:
        status: Filter by project status (optional)
    """
    return atlas.atlas_project_list(status)

@mcp.tool()
def atlas_project_update(project_id: str, name: str = None, description: str = None, status: str = None) -> Dict[str, Any]:
    """Update an Atlas project

    Args:
        project_id: ID of the project to update
        name: New project name (optional)
        description: New project description (optional)
        status: New project status (optional)
    """
    return atlas.atlas_project_update(project_id, name, description, status)

@mcp.tool()
def atlas_task_create(title: str, project_id: str = None, description: str = "", priority: str = "medium", assigned_to: str = None, due_date: str = None) -> Dict[str, Any]:
    """Create a new Atlas task

    Args:
        title: Task title
        project_id: ID of the project this task belongs to (optional)
        description: Task description (optional)
        priority: Task priority (low, medium, high)
        assigned_to: Person assigned to the task (optional)
        due_date: Due date in YYYY-MM-DD format (optional)
    """
    return atlas.atlas_task_create(title, project_id, description, priority, assigned_to, due_date)

@mcp.tool()
def atlas_task_list(project_id: str = None, status: str = None) -> Dict[str, Any]:
    """List Atlas tasks

    Args:
        project_id: Filter by project ID (optional)
        status: Filter by task status (optional)
    """
    return atlas.atlas_task_list(project_id, status)

@mcp.tool()
def atlas_task_update(task_id: str, title: str = None, description: str = None, status: str = None, priority: str = None, assigned_to: str = None, due_date: str = None) -> Dict[str, Any]:
    """Update an Atlas task

    Args:
        task_id: ID of the task to update
        title: New task title (optional)
        description: New task description (optional)
        status: New task status (pending, in_progress, completed, cancelled) (optional)
        priority: New task priority (optional)
        assigned_to: New assignee (optional)
        due_date: New due date (optional)
    """
    return atlas.atlas_task_update(task_id, title, description, status, priority, assigned_to, due_date)

@mcp.tool()
def get_atlas_logs() -> List[Dict[str, Any]]:
    """Get all Atlas operation logs"""
    return atlas.get_atlas_logs()

def main():
    """Function to return the server for compatibility"""
    return mcp

if __name__ == "__main__":
    mcp.run()
