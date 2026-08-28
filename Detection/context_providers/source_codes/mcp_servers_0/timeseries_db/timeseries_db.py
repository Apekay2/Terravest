#!/usr/bin/env python3
"""
Time Series Database MCP Server
Provides InfluxDB-like time series database capabilities for metrics storage,
querying, and aggregation with temporal data handling.
"""

import json
import logging
import uuid
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("timeseries_db")

# Create MCP server instance
mcp = FastMCP('timeseries_db')

# Global state
TIMESERIES_LOGS = []
DATABASES = {}
MEASUREMENT_POINTS = {}

def log_operation(operation: str, details: Dict[str, Any]):
    """Log time series database operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    TIMESERIES_LOGS.append(log_entry)
    logger.info(f"TimeSeries DB Operation: {operation} - {details}")

@mcp.tool()
def create_database(database_name: str, retention_policy: dict = None) -> dict:
    """Create a new time series database"""
    if database_name in DATABASES:
        return {"error": f"Database '{database_name}' already exists"}

    database_id = str(uuid.uuid4())[:8]
    retention_policy = retention_policy or {"duration": "30d", "replication": 1, "shard_duration": "1h"}

    database = {
        "database_id": database_id,
        "name": database_name,
        "retention_policy": retention_policy,
            "created_at": datetime.now().isoformat(),
        "measurements": {},
        "total_points": 0,
        "status": "active",
        "size_bytes": 0
    }

    DATABASES[database_name] = database
    MEASUREMENT_POINTS[database_name] = []

    log_operation("create_database", {
        "database_name": database_name,
        "database_id": database_id,
        "retention_policy": retention_policy
    })

    return {
        "database_id": database_id,
        "database_name": database_name,
        "retention_policy": retention_policy,
        "status": "created"
    }

@mcp.tool()
def write_points(database_name: str, measurement: str, fields: dict, tags: dict = None, timestamp: str = None) -> dict:
    """Write data points to a measurement in the time series database"""
    if database_name not in DATABASES:
        return {"error": f"Database '{database_name}' does not exist"}

    database = DATABASES[database_name]
    point_id = str(uuid.uuid4())[:8]
    timestamp = timestamp or datetime.now().isoformat()
    tags = tags or {}

    # Create data point
    data_point = {
        "point_id": point_id,
        "measurement": measurement,
        "fields": fields,
        "tags": tags,
        "timestamp": timestamp,
        "written_at": datetime.now().isoformat()
    }

    # Store the point
    MEASUREMENT_POINTS[database_name].append(data_point)

    # Update database statistics
    database["total_points"] += 1
    if measurement not in database["measurements"]:
        database["measurements"][measurement] = {
            "point_count": 0,
            "first_timestamp": timestamp,
            "last_timestamp": timestamp,
            "fields": set(),
            "tags": set()
        }

    measurement_info = database["measurements"][measurement]
    measurement_info["point_count"] += 1
    measurement_info["last_timestamp"] = timestamp
    measurement_info["fields"].update(fields.keys())
    measurement_info["tags"].update(tags.keys())

    # Convert sets to lists for JSON serialization
    measurement_info["fields"] = list(measurement_info["fields"])
    measurement_info["tags"] = list(measurement_info["tags"])

    log_operation("write_points", {
        "database_name": database_name,
        "measurement": measurement,
        "point_id": point_id,
        "fields_count": len(fields)
    })

    return {
        "point_id": point_id,
        "database": database_name,
        "measurement": measurement,
        "timestamp": timestamp,
        "status": "written"
    }

@mcp.tool()
def query_data(database_name: str, query: str, time_range: dict = None) -> dict:
    """Query data from the time series database"""
    if database_name not in DATABASES:
        return {"error": f"Database '{database_name}' does not exist"}

    query_id = str(uuid.uuid4())[:8]

    # Get all points for the database
    all_points = MEASUREMENT_POINTS.get(database_name, [])

    # Simple query parsing (in real implementation, would be much more sophisticated)
    query_parts = query.lower().split()
    measurement_filter = None
    field_filter = None

    if "from" in query_parts:
        from_index = query_parts.index("from")
        if from_index + 1 < len(query_parts):
            measurement_filter = query_parts[from_index + 1].strip('"\'')

    if "select" in query_parts:
        select_index = query_parts.index("select")
        if select_index + 1 < len(query_parts):
            field_filter = query_parts[select_index + 1].strip('"\'')

    # Filter points based on query
    filtered_points = []
    for point in all_points[-100:]:  # Limit to recent 100 points
        if measurement_filter and point["measurement"] != measurement_filter:
            continue
        if field_filter and field_filter not in point["fields"]:
            continue
        filtered_points.append(point)

    # Apply time range filter if provided
    if time_range:
        start_time = time_range.get("start")
        end_time = time_range.get("end")
        if start_time or end_time:
            # Simple time filtering (would be more sophisticated in real implementation)
            filtered_points = filtered_points[-50:]  # Get recent points

    result = {
        "query_id": query_id,
        "database": database_name,
        "query": query,
        "result_count": len(filtered_points),
        "results": filtered_points,
        "execution_time_ms": random.randint(10, 100),
        "queried_at": datetime.now().isoformat()
    }

    log_operation("query_data", {
        "database_name": database_name,
        "query_id": query_id,
        "result_count": len(filtered_points)
    })

    return result

@mcp.tool()
def list_databases() -> dict:
    """List all available time series databases"""
    databases_info = {}

    for db_name, db_data in DATABASES.items():
        databases_info[db_name] = {
            "database_id": db_data["database_id"],
            "name": db_data["name"],
            "total_points": db_data["total_points"],
            "measurements": list(db_data["measurements"].keys()),
            "measurement_count": len(db_data["measurements"]),
            "retention_policy": db_data["retention_policy"],
            "created_at": db_data["created_at"],
            "status": db_data["status"]
        }

    log_operation("list_databases", {"database_count": len(DATABASES)})

    return {
        "databases": databases_info,
        "total_databases": len(DATABASES)
    }

@mcp.tool()
def aggregate_data(database_name: str, measurement: str, aggregation_type: str, time_window: str = "1h", group_by: list = None) -> dict:
    """Aggregate time series data using various aggregation functions"""
    if database_name not in DATABASES:
        return {"error": f"Database '{database_name}' does not exist"}

    aggregation_id = str(uuid.uuid4())[:8]

    # Get points for the measurement
    measurement_points = [
        point for point in MEASUREMENT_POINTS.get(database_name, [])
        if point["measurement"] == measurement
    ]

    if not measurement_points:
        return {"error": f"No data found for measurement '{measurement}' in database '{database_name}'"}

    # Simulate aggregation (in real implementation, would do actual calculations)
    aggregation_functions = ["sum", "avg", "min", "max", "count", "stddev"]
    if aggregation_type not in aggregation_functions:
        return {"error": f"Unsupported aggregation type. Supported: {aggregation_functions}"}

    # Generate mock aggregated results
    aggregated_results = []
    for i in range(5):  # Generate 5 time buckets
        bucket_time = (datetime.now() - timedelta(hours=4-i)).isoformat()

        if aggregation_type == "sum":
            value = round(random.uniform(100, 1000), 2)
        elif aggregation_type == "avg":
            value = round(random.uniform(10, 100), 2)
        elif aggregation_type == "count":
            value = random.randint(1, 50)
        elif aggregation_type == "min":
            value = round(random.uniform(1, 10), 2)
        elif aggregation_type == "max":
            value = round(random.uniform(90, 100), 2)
        else:  # stddev
            value = round(random.uniform(1, 15), 2)

        result = {
            "time": bucket_time,
            "value": value,
            "count": random.randint(5, 25)
        }

        if group_by:
            result["groups"] = {tag: f"value_{i}" for tag in group_by}

        aggregated_results.append(result)

    aggregation_result = {
        "aggregation_id": aggregation_id,
        "database": database_name,
        "measurement": measurement,
        "aggregation_type": aggregation_type,
        "time_window": time_window,
        "group_by": group_by or [],
        "results": aggregated_results,
        "result_count": len(aggregated_results),
        "aggregated_at": datetime.now().isoformat()
    }

    log_operation("aggregate_data", {
        "database_name": database_name,
        "measurement": measurement,
        "aggregation_id": aggregation_id,
        "aggregation_type": aggregation_type
    })

    return aggregation_result

@mcp.tool()
def get_timeseries_logs(limit: int = 50) -> dict:
    """Retrieve time series database operation logs"""
    recent_logs = TIMESERIES_LOGS[-limit:] if limit > 0 else TIMESERIES_LOGS

    return {
        "logs": recent_logs,
        "total_operations": len(TIMESERIES_LOGS),
        "returned_count": len(recent_logs)
    }

if __name__ == "__main__":
    mcp.run()
