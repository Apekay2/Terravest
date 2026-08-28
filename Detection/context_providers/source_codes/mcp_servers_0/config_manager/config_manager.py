#!/usr/bin/env python3
"""
Configuration Manager MCP Server
Provides configuration management capabilities including environment
configuration, deployment automation, and infrastructure as code.
"""

import json
import logging
import yaml
import uuid
from datetime import datetime
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("config_manager")

# Create MCP server instance
mcp = FastMCP('config_manager')

# Global state
CONFIG_LOGS = []
ENVIRONMENTS = {
    "development": {"status": "active", "configs": {}, "last_updated": datetime.now().isoformat()},
    "staging": {"status": "active", "configs": {}, "last_updated": datetime.now().isoformat()},
    "production": {"status": "active", "configs": {}, "last_updated": datetime.now().isoformat()}
}
TEMPLATES = {}
DEPLOYMENTS = []

def log_operation(operation: str, details: Dict[str, Any]):
    """Log configuration operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    CONFIG_LOGS.append(log_entry)
    logger.info(f"Config Manager Operation: {operation} - {details}")

@mcp.tool()
def deploy_configuration(environment: str, config_data: dict, deployment_strategy: str = "rolling") -> dict:
    """Deploy configuration to an environment"""
    if environment not in ENVIRONMENTS:
        return {"error": f"Environment '{environment}' not found"}

    deployment_id = str(uuid.uuid4())[:8]

    # Update environment configuration
    ENVIRONMENTS[environment]["configs"].update(config_data)
    ENVIRONMENTS[environment]["last_updated"] = datetime.now().isoformat()

    # Record deployment
    deployment = {
            "deployment_id": deployment_id,
            "environment": environment,
            "strategy": deployment_strategy,
        "config_data": config_data,
            "status": "completed",
        "timestamp": datetime.now().isoformat()
    }
    DEPLOYMENTS.append(deployment)

    log_operation("deploy_configuration", {
        "environment": environment,
        "deployment_id": deployment_id,
        "strategy": deployment_strategy
    })

    return {
            "deployment_id": deployment_id,
            "environment": environment,
        "status": "deployed",
        "config_count": len(config_data),
        "strategy": deployment_strategy
    }

@mcp.tool()
def validate_configuration(config_data: dict, schema: dict = None) -> dict:
    """Validate configuration data against schema"""
    validation_errors = []
    warnings = []

    # Basic validation
    if not isinstance(config_data, dict):
        validation_errors.append("Configuration must be a dictionary")

    # Check for required keys
    required_keys = ["name", "environment"]
    for key in required_keys:
        if key not in config_data:
            validation_errors.append(f"Missing required key: {key}")

    # Environment-specific validation
    if "environment" in config_data:
        if config_data["environment"] not in ENVIRONMENTS:
            warnings.append(f"Environment '{config_data['environment']}' is not defined")

    # Schema validation if provided
    if schema:
        for key, expected_type in schema.items():
            if key in config_data:
                actual_value = config_data[key]
                if expected_type == "string" and not isinstance(actual_value, str):
                    validation_errors.append(f"Key '{key}' must be a string")
                elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                    validation_errors.append(f"Key '{key}' must be a number")

    log_operation("validate_configuration", {
        "errors": len(validation_errors),
        "warnings": len(warnings)
    })

    return {
        "valid": len(validation_errors) == 0,
        "errors": validation_errors,
        "warnings": warnings,
        "validated_keys": list(config_data.keys()) if isinstance(config_data, dict) else []
    }

@mcp.tool()
def rollback_deployment(deployment_id: str, environment: str) -> dict:
    """Rollback a deployment to previous configuration"""
    # Find the deployment to rollback
    target_deployment = None
    for deployment in DEPLOYMENTS:
        if deployment["deployment_id"] == deployment_id and deployment["environment"] == environment:
            target_deployment = deployment
            break

    if not target_deployment:
        return {"error": f"Deployment {deployment_id} not found for environment {environment}"}

    # Find previous deployment
    previous_deployments = [
        d for d in DEPLOYMENTS
        if d["environment"] == environment and d["timestamp"] < target_deployment["timestamp"]
    ]

    if not previous_deployments:
        return {"error": "No previous deployment found to rollback to"}

    # Get the most recent previous deployment
    previous_deployment = max(previous_deployments, key=lambda x: x["timestamp"])

    # Rollback configuration
    ENVIRONMENTS[environment]["configs"] = previous_deployment["config_data"].copy()
    ENVIRONMENTS[environment]["last_updated"] = datetime.now().isoformat()

    # Record rollback
    rollback_deployment = {
        "deployment_id": str(uuid.uuid4())[:8],
        "environment": environment,
        "strategy": "rollback",
        "config_data": previous_deployment["config_data"],
        "rollback_from": deployment_id,
        "rollback_to": previous_deployment["deployment_id"],
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }
    DEPLOYMENTS.append(rollback_deployment)

    log_operation("rollback_deployment", {
        "environment": environment,
        "rollback_from": deployment_id,
        "rollback_to": previous_deployment["deployment_id"]
    })

    return {
        "deployment_id": rollback_deployment["deployment_id"],
        "environment": environment,
        "status": "rollback_completed",
        "rollback_from": deployment_id,
        "rollback_to": previous_deployment["deployment_id"]
    }

@mcp.tool()
def list_environments() -> dict:
    """List all available environments and their status"""
    environments_info = {}

    for env_name, env_data in ENVIRONMENTS.items():
        environments_info[env_name] = {
            "status": env_data["status"],
            "last_updated": env_data["last_updated"],
            "config_count": len(env_data["configs"]),
            "configs": list(env_data["configs"].keys())
        }

    log_operation("list_environments", {"environment_count": len(ENVIRONMENTS)})

    return {
        "environments": environments_info,
        "total_count": len(ENVIRONMENTS)
    }

@mcp.tool()
def get_environment_config(environment: str) -> dict:
    """Get configuration for a specific environment"""
    if environment not in ENVIRONMENTS:
        return {"error": f"Environment '{environment}' not found"}

    env_data = ENVIRONMENTS[environment]

    log_operation("get_environment_config", {"environment": environment})

    return {
        "environment": environment,
        "status": env_data["status"],
        "last_updated": env_data["last_updated"],
        "configurations": env_data["configs"]
    }

@mcp.tool()
def create_config_template(template_name: str, template_data: dict, description: str = "") -> dict:
    """Create a reusable configuration template"""
    template_id = str(uuid.uuid4())[:8]

    template = {
        "template_id": template_id,
        "name": template_name,
        "description": description,
        "template_data": template_data,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

    TEMPLATES[template_id] = template

    log_operation("create_config_template", {
        "template_name": template_name,
        "template_id": template_id
    })

    return {
        "template_id": template_id,
        "name": template_name,
        "status": "created",
        "template_keys": list(template_data.keys()) if isinstance(template_data, dict) else []
    }

@mcp.tool()
def get_config_logs(limit: int = 50) -> dict:
    """Retrieve configuration management operation logs"""
    recent_logs = CONFIG_LOGS[-limit:] if limit > 0 else CONFIG_LOGS

    return {
        "logs": recent_logs,
        "total_operations": len(CONFIG_LOGS),
        "returned_count": len(recent_logs)
    }

if __name__ == "__main__":
    mcp.run()
