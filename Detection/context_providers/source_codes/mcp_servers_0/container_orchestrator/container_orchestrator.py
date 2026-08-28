#!/usr/bin/env python3
"""
Container Orchestrator MCP Server
Provides container management and orchestration capabilities
similar to Docker and Kubernetes for deployment and scaling.
"""

import json
import logging
import uuid
import random
from datetime import datetime
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("container_orchestrator")

# Create MCP server instance
mcp = FastMCP('container_orchestrator')

# Global state
ORCHESTRATOR_LOGS = []
CONTAINERS = {}
SERVICES = {}
CLUSTERS = {"default": {"status": "running", "nodes": 3, "created_at": datetime.now().isoformat()}}

def log_operation(operation: str, details: Dict[str, Any]):
    """Log container operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    ORCHESTRATOR_LOGS.append(log_entry)
    logger.info(f"Container Orchestrator Operation: {operation} - {details}")

@mcp.tool()
def deploy_container(image_name: str, container_name: str = None, config: dict = None) -> dict:
    """Deploy a new container"""
    container_id = str(uuid.uuid4())
    container_name = container_name or f"container-{container_id[:8]}"

    container_info = {
        "container_id": container_id,
        "name": container_name,
        "image": image_name,
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "config": config or {},
        "resource_usage": {
            "cpu_percent": round(random.uniform(1, 50), 2),
            "memory_mb": random.randint(64, 512),
            "network_io": {"rx_bytes": 0, "tx_bytes": 0}
        }
    }

    CONTAINERS[container_id] = container_info

    log_operation("deploy_container", {
        "container_name": container_name,
        "image": image_name,
        "container_id": container_id
    })

    return {
        "container_id": container_id,
        "name": container_name,
        "image": image_name,
        "status": "deployed",
        "endpoint": f"http://localhost:{random.randint(3000, 9999)}"
    }

@mcp.tool()
def list_containers(status_filter: str = None) -> dict:
    """List all containers with optional status filtering"""
    containers_list = []

    for container_id, container in CONTAINERS.items():
        if status_filter and container["status"] != status_filter:
            continue

        containers_list.append({
            "container_id": container_id,
            "name": container["name"],
            "image": container["image"],
            "status": container["status"],
            "created_at": container["created_at"],
            "resource_usage": container["resource_usage"]
        })

    log_operation("list_containers", {"filter": status_filter, "count": len(containers_list)})

    return {
        "containers": containers_list,
        "total_count": len(containers_list),
        "status_filter": status_filter
    }

@mcp.tool()
def scale_service(service_name: str, replicas: int) -> dict:
    """Scale a service to the specified number of replicas"""
    if service_name not in SERVICES:
        # Create new service if it doesn't exist
        service_id = str(uuid.uuid4())[:8]
        SERVICES[service_name] = {
            "service_id": service_id,
            "name": service_name,
            "replicas": 0,
            "desired_replicas": replicas,
            "status": "scaling",
            "created_at": datetime.now().isoformat(),
            "containers": []
        }

    service = SERVICES[service_name]
    old_replicas = service["replicas"]
    service["desired_replicas"] = replicas
    service["replicas"] = replicas
    service["status"] = "running" if replicas > 0 else "stopped"

    # Simulate container creation/deletion for scaling
    if replicas > old_replicas:
        # Scale up - create new containers
        for i in range(old_replicas, replicas):
            container_id = str(uuid.uuid4())
            service["containers"].append(container_id)
    elif replicas < old_replicas:
        # Scale down - remove containers
        service["containers"] = service["containers"][:replicas]

    log_operation("scale_service", {
        "service_name": service_name,
        "old_replicas": old_replicas,
        "new_replicas": replicas
    })

    return {
        "service_name": service_name,
        "old_replicas": old_replicas,
        "new_replicas": replicas,
        "status": service["status"],
        "scaling_action": "up" if replicas > old_replicas else "down" if replicas < old_replicas else "no_change"
    }

@mcp.tool()
def get_container_logs(container_id: str, lines: int = 100) -> dict:
    """Get logs for a specific container"""
    if container_id not in CONTAINERS:
        return {"error": f"Container {container_id} not found"}

    container = CONTAINERS[container_id]

    # Generate mock log entries
    log_entries = []
    for i in range(min(lines, 50)):  # Limit to reasonable number
        timestamp = datetime.now().isoformat()
        level = random.choice(["INFO", "WARN", "ERROR", "DEBUG"])
        message = f"Application log entry {i+1}"
        log_entries.append(f"{timestamp} [{level}] {message}")

    log_operation("get_container_logs", {
        "container_id": container_id,
        "lines_requested": lines,
        "lines_returned": len(log_entries)
    })

    return {
        "container_id": container_id,
        "container_name": container["name"],
        "logs": log_entries,
        "lines_returned": len(log_entries)
    }

@mcp.tool()
def monitor_cluster_health() -> dict:
    """Monitor overall cluster health and resource usage"""
    total_containers = len(CONTAINERS)
    running_containers = len([c for c in CONTAINERS.values() if c["status"] == "running"])

    # Calculate aggregate resource usage
    total_cpu = sum(c["resource_usage"]["cpu_percent"] for c in CONTAINERS.values())
    total_memory = sum(c["resource_usage"]["memory_mb"] for c in CONTAINERS.values())
    avg_cpu = total_cpu / total_containers if total_containers > 0 else 0

    cluster_health = {
        "status": "healthy" if running_containers / max(total_containers, 1) > 0.8 else "degraded",
        "total_nodes": CLUSTERS["default"]["nodes"],
        "total_containers": total_containers,
        "running_containers": running_containers,
        "resource_usage": {
            "total_cpu_percent": round(total_cpu, 2),
            "average_cpu_percent": round(avg_cpu, 2),
            "total_memory_mb": total_memory,
            "cluster_load": "low" if avg_cpu < 30 else "medium" if avg_cpu < 70 else "high"
        },
        "timestamp": datetime.now().isoformat()
    }

    log_operation("monitor_cluster_health", {
        "cluster_status": cluster_health["status"],
        "total_containers": total_containers
    })

    return cluster_health

@mcp.tool()
def create_service(service_name: str, image_name: str, replicas: int = 1, config: dict = None) -> dict:
    """Create a new service with specified configuration"""
    if service_name in SERVICES:
        return {"error": f"Service '{service_name}' already exists"}

    service_id = str(uuid.uuid4())[:8]
    service_config = config or {}

    service = {
        "service_id": service_id,
        "name": service_name,
        "image": image_name,
        "replicas": replicas,
        "desired_replicas": replicas,
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "config": service_config,
        "containers": []
    }

    # Create containers for the service
    for i in range(replicas):
        container_id = str(uuid.uuid4())
        service["containers"].append(container_id)

        # Also add to global containers
        CONTAINERS[container_id] = {
            "container_id": container_id,
            "name": f"{service_name}-{i+1}",
            "image": image_name,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "config": service_config,
            "service": service_name,
            "resource_usage": {
                "cpu_percent": round(random.uniform(1, 50), 2),
                "memory_mb": random.randint(64, 512),
                "network_io": {"rx_bytes": 0, "tx_bytes": 0}
            }
        }

    SERVICES[service_name] = service

    log_operation("create_service", {
        "service_name": service_name,
        "service_id": service_id,
        "replicas": replicas,
        "image": image_name
    })

    return {
        "service_id": service_id,
        "service_name": service_name,
        "image": image_name,
        "replicas": replicas,
        "status": "created",
        "containers": len(service["containers"])
    }

@mcp.tool()
def get_orchestrator_logs(limit: int = 50) -> dict:
    """Retrieve container orchestrator operation logs"""
    recent_logs = ORCHESTRATOR_LOGS[-limit:] if limit > 0 else ORCHESTRATOR_LOGS

    return {
        "logs": recent_logs,
        "total_operations": len(ORCHESTRATOR_LOGS),
        "returned_count": len(recent_logs)
    }

if __name__ == "__main__":
    mcp.run()
