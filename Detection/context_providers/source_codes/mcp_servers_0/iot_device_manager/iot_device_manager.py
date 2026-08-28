#!/usr/bin/env python3
"""
IoT Device Manager MCP Server
Provides IoT device management capabilities including device provisioning,
data collection, firmware updates, and fleet monitoring.
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
logger = logging.getLogger("iot_device_manager")

# Create MCP server instance
mcp = FastMCP('iot_device_manager')

# Global state
IOT_LOGS = []
DEVICES = {}
DEVICE_GROUPS = {}
SENSOR_DATA = {}
FIRMWARE_UPDATES = {}

def log_operation(operation: str, details: Dict[str, Any]):
    """Log IoT device manager operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    IOT_LOGS.append(log_entry)
    logger.info(f"IoT Device Manager Operation: {operation} - {details}")

@mcp.tool()
def provision_device(device_name: str, device_type: str, configuration: dict = None) -> dict:
    """Provision a new IoT device"""
    if device_name in DEVICES:
        return {"error": f"Device '{device_name}' already exists"}

    device_id = str(uuid.uuid4())[:8]

    device = {
        "device_id": device_id,
        "name": device_name,
        "type": device_type,
        "status": "online",
        "configuration": configuration or {},
        "provisioned_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(),
        "firmware_version": "1.0.0",
        "battery_level": random.randint(20, 100) if device_type in ["sensor", "tracker"] else None,
        "location": {"lat": round(random.uniform(40.0, 41.0), 6), "lng": round(random.uniform(-74.0, -73.0), 6)}
    }

    DEVICES[device_name] = device

    log_operation("provision_device", {"device_name": device_name, "device_id": device_id, "device_type": device_type})
    return {"device_id": device_id, "device_name": device_name, "status": "provisioned", "device_type": device_type}

@mcp.tool()
def list_devices(device_type: str = None, status_filter: str = None) -> dict:
    """List all IoT devices with optional filtering"""
    devices_list = []

    for device_name, device_data in DEVICES.items():
        if device_type and device_data["type"] != device_type:
            continue
        if status_filter and device_data["status"] != status_filter:
            continue

        device_info = {
            "device_id": device_data["device_id"],
            "name": device_name,
            "type": device_data["type"],
            "status": device_data["status"],
            "last_seen": device_data["last_seen"],
            "firmware_version": device_data["firmware_version"],
            "battery_level": device_data.get("battery_level")
        }
        devices_list.append(device_info)

    log_operation("list_devices", {"device_type": device_type, "status_filter": status_filter, "devices_found": len(devices_list)})

    return {
        "devices": devices_list,
        "total_devices": len(devices_list),
        "filters": {"device_type": device_type, "status": status_filter}
    }

@mcp.tool()
def collect_sensor_data(device_name: str, sensor_types: list) -> dict:
    """Collect sensor data from an IoT device"""
    if device_name not in DEVICES:
        return {"error": f"Device '{device_name}' not found"}

    device = DEVICES[device_name]
    collection_id = str(uuid.uuid4())[:8]

    if device["status"] != "online":
        return {"error": f"Device '{device_name}' is not online"}

    sensor_readings = {}

    for sensor_type in sensor_types:
        if sensor_type == "temperature":
            sensor_readings[sensor_type] = {"value": round(random.uniform(18, 28), 2), "unit": "°C"}
        elif sensor_type == "humidity":
            sensor_readings[sensor_type] = {"value": round(random.uniform(30, 70), 2), "unit": "%"}
        elif sensor_type == "pressure":
            sensor_readings[sensor_type] = {"value": round(random.uniform(1000, 1020), 2), "unit": "hPa"}
        elif sensor_type == "light":
            sensor_readings[sensor_type] = {"value": random.randint(0, 1000), "unit": "lux"}
        elif sensor_type == "motion":
            sensor_readings[sensor_type] = {"value": random.choice([True, False]), "unit": "boolean"}
        else:
            sensor_readings[sensor_type] = {"value": round(random.uniform(0, 100), 2), "unit": "unknown"}

    sensor_data = {
        "collection_id": collection_id,
        "device_name": device_name,
        "device_id": device["device_id"],
        "sensor_readings": sensor_readings,
        "timestamp": datetime.now().isoformat(),
        "collection_status": "success"
    }

    SENSOR_DATA[collection_id] = sensor_data

    # Update device last seen
    device["last_seen"] = datetime.now().isoformat()

    log_operation("collect_sensor_data", {"device_name": device_name, "collection_id": collection_id, "sensors_count": len(sensor_types)})
    return sensor_data

@mcp.tool()
def update_firmware(device_name: str, firmware_version: str) -> dict:
    """Update firmware on an IoT device"""
    if device_name not in DEVICES:
        return {"error": f"Device '{device_name}' not found"}

    device = DEVICES[device_name]
    update_id = str(uuid.uuid4())[:8]

    if device["status"] != "online":
        return {"error": f"Device '{device_name}' is not online"}

    firmware_update = {
        "update_id": update_id,
        "device_name": device_name,
        "device_id": device["device_id"],
        "old_version": device["firmware_version"],
        "new_version": firmware_version,
        "status": "completed",
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat()
    }

    # Update device firmware version
    device["firmware_version"] = firmware_version
    device["last_seen"] = datetime.now().isoformat()

    FIRMWARE_UPDATES[update_id] = firmware_update

    log_operation("update_firmware", {"device_name": device_name, "update_id": update_id, "new_version": firmware_version})
    return firmware_update

@mcp.tool()
def create_device_group(group_name: str, device_names: list, group_config: dict = None) -> dict:
    """Create a group of IoT devices for bulk management"""
    if group_name in DEVICE_GROUPS:
        return {"error": f"Device group '{group_name}' already exists"}

    group_id = str(uuid.uuid4())[:8]

    # Validate devices exist
    invalid_devices = [name for name in device_names if name not in DEVICES]
    if invalid_devices:
        return {"error": f"Devices not found: {invalid_devices}"}

    device_group = {
        "group_id": group_id,
        "name": group_name,
        "device_names": device_names,
        "device_count": len(device_names),
        "config": group_config or {},
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }

    DEVICE_GROUPS[group_name] = device_group

    log_operation("create_device_group", {"group_name": group_name, "group_id": group_id, "device_count": len(device_names)})
    return {"group_id": group_id, "group_name": group_name, "device_count": len(device_names), "status": "created"}

@mcp.tool()
def monitor_fleet_health() -> dict:
    """Monitor overall fleet health and status"""
    monitoring_id = str(uuid.uuid4())[:8]

    total_devices = len(DEVICES)
    online_devices = len([d for d in DEVICES.values() if d["status"] == "online"])
    offline_devices = total_devices - online_devices

    # Check battery levels
    low_battery_devices = []
    for device_name, device in DEVICES.items():
        if device.get("battery_level") and device["battery_level"] < 20:
            low_battery_devices.append(device_name)

    # Check firmware versions
    outdated_firmware = []
    latest_version = "1.2.0"
    for device_name, device in DEVICES.items():
        if device["firmware_version"] != latest_version:
            outdated_firmware.append(device_name)

    fleet_health = {
        "monitoring_id": monitoring_id,
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "health_percentage": round((online_devices / max(total_devices, 1)) * 100, 2),
        "low_battery_devices": low_battery_devices,
        "outdated_firmware_devices": outdated_firmware,
        "alerts": [],
        "monitored_at": datetime.now().isoformat()
    }

    # Generate alerts
    if offline_devices > 0:
        fleet_health["alerts"].append(f"{offline_devices} devices are offline")
    if low_battery_devices:
        fleet_health["alerts"].append(f"{len(low_battery_devices)} devices have low battery")
    if outdated_firmware:
        fleet_health["alerts"].append(f"{len(outdated_firmware)} devices need firmware update")

    log_operation("monitor_fleet_health", {"monitoring_id": monitoring_id, "total_devices": total_devices, "health_percentage": fleet_health["health_percentage"]})
    return fleet_health

@mcp.tool()
def get_iot_logs(limit: int = 50) -> dict:
    """Retrieve IoT device manager operation logs"""
    recent_logs = IOT_LOGS[-limit:] if limit > 0 else IOT_LOGS

    return {
        "logs": recent_logs,
        "total_operations": len(IOT_LOGS),
        "returned_count": len(recent_logs)
    }

if __name__ == "__main__":
    mcp.run()
