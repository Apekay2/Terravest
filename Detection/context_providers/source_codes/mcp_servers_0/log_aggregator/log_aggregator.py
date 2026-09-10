#!/usr/bin/env python3
"""
Log Aggregator MCP Server
Provides centralized log aggregation and analysis capabilities
with parsing, alerting, and pattern detection.
"""

import json
import logging
import uuid
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("log_aggregator")

# Create MCP server instance
mcp = FastMCP('log_aggregator')

# Global state
AGGREGATOR_LOGS = []
LOG_SOURCES = {}
PARSED_LOGS = []
ALERT_RULES = {}
LOG_PATTERNS = {}

def log_operation(operation: str, details: Dict[str, Any]):
    """Log aggregator operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    AGGREGATOR_LOGS.append(log_entry)
    logger.info(f"Log Aggregator Operation: {operation} - {details}")

@mcp.tool()
def add_log_source(source_name: str, source_type: str, connection_config: dict) -> dict:
    """Add a new log source for aggregation"""
    if source_name in LOG_SOURCES:
        return {"error": f"Log source '{source_name}' already exists"}

    source_id = str(uuid.uuid4())[:8]

    log_source = {
        "source_id": source_id,
        "name": source_name,
        "type": source_type,
        "config": connection_config,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "logs_collected": 0,
        "last_collection": None,
        "errors": 0
    }

    LOG_SOURCES[source_name] = log_source

    log_operation("add_log_source", {
        "source_name": source_name,
        "source_id": source_id,
        "source_type": source_type
    })

    return {
        "source_id": source_id,
        "source_name": source_name,
        "source_type": source_type,
        "status": "created"
    }

@mcp.tool()
def parse_logs(source_name: str, log_format: str = "common", custom_pattern: str = None) -> dict:
    """Parse logs from a specific source using defined patterns"""
    if source_name not in LOG_SOURCES:
        return {"error": f"Log source '{source_name}' not found"}

    source = LOG_SOURCES[source_name]
    parse_id = str(uuid.uuid4())[:8]

    # Simulate log parsing
    sample_logs = [
        "2024-01-15 10:30:01 INFO [UserService] User login successful: user123",
        "2024-01-15 10:30:15 ERROR [DatabaseService] Connection timeout: db-server-1",
        "2024-01-15 10:30:30 WARN [PaymentService] High response time: 2.5s",
        "2024-01-15 10:31:00 INFO [AuthService] Password reset requested: user456",
        "2024-01-15 10:31:15 ERROR [FileService] Disk space low: 95% full"
    ]

    parsed_entries = []
    for i, log_line in enumerate(sample_logs):
        # Basic parsing simulation
        if log_format == "common":
            parts = log_line.split(' ', 4)
            if len(parts) >= 5:
                parsed_entry = {
                    "entry_id": str(uuid.uuid4())[:8],
                    "timestamp": f"{parts[0]} {parts[1]}",
                    "level": parts[2],
                    "service": parts[3].strip('[]'),
                    "message": parts[4] if len(parts) > 4 else "",
                    "source": source_name,
                    "parsed_at": datetime.now().isoformat()
                }
                parsed_entries.append(parsed_entry)
                PARSED_LOGS.append(parsed_entry)

    # Update source statistics
    source["logs_collected"] += len(parsed_entries)
    source["last_collection"] = datetime.now().isoformat()

    log_operation("parse_logs", {
        "source_name": source_name,
        "parse_id": parse_id,
        "log_format": log_format,
        "entries_parsed": len(parsed_entries)
    })

    return {
        "parse_id": parse_id,
        "source_name": source_name,
        "log_format": log_format,
        "entries_parsed": len(parsed_entries),
        "parsed_entries": parsed_entries[:10]  # Return first 10 for display
    }

@mcp.tool()
def search_logs(query: str, source_filter: str = None, level_filter: str = None, time_range: dict = None) -> dict:
    """Search through parsed logs with various filters"""
    search_id = str(uuid.uuid4())[:8]

    # Filter logs based on criteria
    filtered_logs = PARSED_LOGS

    if source_filter:
        filtered_logs = [log for log in filtered_logs if log["source"] == source_filter]

    if level_filter:
        filtered_logs = [log for log in filtered_logs if log["level"].upper() == level_filter.upper()]

    if time_range:
        # Simple time range filtering (would be more sophisticated in real implementation)
        start_time = time_range.get("start")
        end_time = time_range.get("end")
        if start_time or end_time:
            # For demo, just filter based on recent entries
            filtered_logs = filtered_logs[-50:]

    # Search in message content
    search_results = []
    for log_entry in filtered_logs:
        if query.lower() in log_entry["message"].lower():
            search_results.append(log_entry)

    log_operation("search_logs", {
        "search_id": search_id,
        "query": query,
        "source_filter": source_filter,
        "level_filter": level_filter,
        "results_found": len(search_results)
    })

    return {
        "search_id": search_id,
        "query": query,
        "filters": {
            "source": source_filter,
            "level": level_filter,
            "time_range": time_range
        },
        "total_results": len(search_results),
        "results": search_results[:20]  # Return first 20 results
    }

@mcp.tool()
def create_alert_rule(rule_name: str, condition: dict, action: dict, severity: str = "medium") -> dict:
    """Create an alert rule for log monitoring"""
    if rule_name in ALERT_RULES:
        return {"error": f"Alert rule '{rule_name}' already exists"}

    rule_id = str(uuid.uuid4())[:8]

    alert_rule = {
        "rule_id": rule_id,
        "name": rule_name,
        "condition": condition,
        "action": action,
        "severity": severity,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "trigger_count": 0,
        "last_triggered": None
    }

    ALERT_RULES[rule_name] = alert_rule

    log_operation("create_alert_rule", {
        "rule_name": rule_name,
        "rule_id": rule_id,
        "severity": severity
    })

    return {
        "rule_id": rule_id,
        "rule_name": rule_name,
        "severity": severity,
        "status": "created",
        "condition": condition,
        "action": action
    }

@mcp.tool()
def analyze_log_patterns(source_name: str = None, time_window: int = 60) -> dict:
    """Analyze log patterns and detect anomalies"""
    analysis_id = str(uuid.uuid4())[:8]

    # Filter logs for analysis
    logs_to_analyze = PARSED_LOGS
    if source_name:
        logs_to_analyze = [log for log in logs_to_analyze if log["source"] == source_name]

    # Analyze patterns
    level_distribution = {}
    service_activity = {}
    error_patterns = []

    for log_entry in logs_to_analyze[-100:]:  # Analyze last 100 entries
        # Count log levels
        level = log_entry["level"]
        level_distribution[level] = level_distribution.get(level, 0) + 1

        # Count service activity
        service = log_entry.get("service", "unknown")
        service_activity[service] = service_activity.get(service, 0) + 1

        # Identify error patterns
        if level == "ERROR":
            error_patterns.append({
                "timestamp": log_entry["timestamp"],
                "service": service,
                "message": log_entry["message"]
            })

    # Calculate anomaly score
    total_logs = len(logs_to_analyze[-100:]) if logs_to_analyze else 0
    error_rate = level_distribution.get("ERROR", 0) / max(total_logs, 1)
    anomaly_score = min(error_rate * 100, 100)

    analysis_result = {
        "analysis_id": analysis_id,
        "source_name": source_name or "all",
        "time_window_minutes": time_window,
        "total_logs_analyzed": total_logs,
        "level_distribution": level_distribution,
        "service_activity": service_activity,
        "error_patterns": error_patterns[-10:],  # Last 10 errors
        "anomaly_score": round(anomaly_score, 2),
        "anomaly_status": "high" if anomaly_score > 50 else "medium" if anomaly_score > 20 else "low",
        "analyzed_at": datetime.now().isoformat()
    }

    log_operation("analyze_log_patterns", {
        "analysis_id": analysis_id,
        "source_name": source_name,
        "logs_analyzed": total_logs,
        "anomaly_score": anomaly_score
    })

    return analysis_result

@mcp.tool()
def get_aggregator_logs(limit: int = 50) -> dict:
    """Retrieve log aggregator operation logs"""
    recent_logs = AGGREGATOR_LOGS[-limit:] if limit > 0 else AGGREGATOR_LOGS

    return {
        "logs": recent_logs,
        "total_operations": len(AGGREGATOR_LOGS),
        "returned_count": len(recent_logs)
    }

if __name__ == "__main__":
    mcp.run()
