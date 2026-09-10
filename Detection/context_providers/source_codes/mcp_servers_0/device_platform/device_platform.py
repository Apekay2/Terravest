#!/usr/bin/env python3
"""
Device Manager MCP Server
=========================

IoT device management and testing server.
Provides virtual device creation, behavior management, and testing environments.
Manages all device operations with comprehensive logging of device control.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import random

# Create MCP server instance
mcp = FastMCP('device_platform')

# Simple activity log
DEVICE_LOG = []

def log_action(action: str, details: Dict[str, Any]) -> str:
    """Log device demonstration action with timestamp"""
    operation_id = f"DEVICE_{int(time.time())}_{len(DEVICE_LOG)}"

    DEVICE_LOG.append({
        "operation_id": operation_id,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })

    print(f"📋 DEVICE: {action} - {operation_id}")
    return operation_id

DEVICE_TYPES = ["sensor", "actuator", "gateway", "camera", "thermostat", "lock", "light", "speaker"]
PROTOCOLS = ["mqtt", "http", "coap", "zigbee", "zwave", "bluetooth", "wifi"]
DEVICE_STATES = ["online", "offline", "error", "maintenance", "updating"]

@mcp.tool()
def create_virtual_device(device_config: Dict[str, Any]) -> Dict[str, Any]:
    """Create a virtual IoT device """
    operation_id = log_action("CREATE_DEVICE", {
        "device_type": device_config.get("type", "unknown"),
        "protocol": device_config.get("protocol", "mqtt")
    })

    device_id = f"dev_{random.randint(1000, 9999)}"
    device_hash = hash(str(device_config))
    random.seed(device_hash)

    # Generate device creation
    virtual_device = {
        "device_id": device_id,
        "device_name": device_config.get("name", f"Device {device_id}"),
        "device_type": device_config.get("type", random.choice(DEVICE_TYPES)),
        "protocol": device_config.get("protocol", random.choice(PROTOCOLS)),
        "firmware_version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
        "ip_address": f"192.168.1.{random.randint(100, 254)}",
        "mac_address": f"02:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
        "status": "online",
        "capabilities": device_config.get("capabilities", ["basic_control", "status_report"]),
        "power_consumption": round(random.uniform(0.5, 50.0), 1),
        "signal_strength": random.randint(-80, -30),
        "last_seen": datetime.now().isoformat()
    }

    # Add device-specific properties
    if virtual_device["device_type"] == "sensor":
        virtual_device.update({
            "sensor_type": random.choice(["temperature", "humidity", "motion", "light"]),
            "measurement_unit": random.choice(["°C", "%", "lux", "count"]),
            "sampling_rate": f"{random.randint(1, 60)}s"
        })
    elif virtual_device["device_type"] == "camera":
        virtual_device.update({
            "resolution": random.choice(["720p", "1080p", "4K"]),
            "frame_rate": f"{random.choice([15, 30, 60])}fps",
            "night_vision": random.choice([True, False])
        })

    return {
        "creation_id": operation_id,
        "virtual_device": virtual_device,
        "setup_time": round(random.uniform(2, 10), 1),
        "created_at": datetime.now().isoformat()
    }

@mcp.tool()
def demonstrate_device_behavior(device_id: str, behavior_config: Dict[str, Any]) -> Dict[str, Any]:
    """demonstrate device behavior patterns """
    operation_id = log_action("DEMONSTRATE_BEHAVIOR", {
        "device_id": device_id,
        "behavior_type": behavior_config.get("type", "normal")
    })

    behavior_hash = hash(f"{device_id}_{str(behavior_config)}")
    random.seed(behavior_hash)

    behavior_type = behavior_config.get("type", "normal")
    duration = behavior_config.get("duration", 3600)  # 1 hour default

    # Generate behavior demonstration
    behavior_events = []
    event_count = random.randint(5, 20)

    for i in range(event_count):
        event_time = random.randint(0, duration)
        event = {
            "timestamp": (datetime.now() + timedelta(seconds=event_time)).isoformat(),
            "event_type": random.choice(["data_update", "status_change", "error", "maintenance"]),
            "event_data": {}
        }

        if behavior_type == "anomalous":
            event["event_data"] = {
                "anomaly_detected": True,
                "anomaly_type": random.choice(["spike", "dropout", "irregular_pattern"]),
                "severity": random.choice(["low", "medium", "high"])
            }
        elif behavior_type == "failure":
            event["event_data"] = {
                "failure_mode": random.choice(["connectivity_loss", "sensor_failure", "power_issue"]),
                "error_code": f"ERR_{random.randint(100, 999)}"
            }
        else:  # normal
            event["event_data"] = {
                "value": round(random.uniform(0, 100), 2),
                "unit": random.choice(["°C", "%", "lux", "count"]),
                "quality": round(random.uniform(0.8, 1.0), 2)
            }

        behavior_events.append(event)

    behavior_summary = {
        "behavior_type": behavior_type,
        "duration_seconds": duration,
        "events_generated": len(behavior_events),
        "average_interval": round(duration / len(behavior_events), 1),
        "status_changes": len([e for e in behavior_events if e["event_type"] == "status_change"]),
        "errors_generated": len([e for e in behavior_events if e["event_type"] == "error"])
    }

    return {
        "demonstration_id": operation_id,
        "device_id": device_id,
        "behavior_events": behavior_events[:10],  # Limit output
        "behavior_summary": behavior_summary,
        "demonstrated_at": datetime.now().isoformat()
    }

@mcp.tool()
def manage_device_fleet(fleet_config: Dict[str, Any]) -> Dict[str, Any]:
    """Manage a fleet of virtual devices """
    operation_id = log_action("MANAGE_FLEET", {
        "fleet_size": fleet_config.get("size", 10),
        "device_types": fleet_config.get("types", ["sensor"])
    })

    fleet_size = fleet_config.get("size", 10)
    device_types = fleet_config.get("types", DEVICE_TYPES[:3])

    fleet_hash = hash(str(fleet_config))
    random.seed(fleet_hash)

    # Generate fleet
    fleet_devices = []
    for i in range(min(fleet_size, 50)):  # Limit to 50 devices
        device = {
            "device_id": f"fleet_dev_{i+1:03d}",
            "device_type": random.choice(device_types),
            "status": random.choice(DEVICE_STATES),
            "last_update": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "battery_level": random.randint(10, 100) if random.random() > 0.3 else None,
            "signal_strength": random.randint(-80, -30),
            "location": f"Zone {random.randint(1, 10)}"
        }
        fleet_devices.append(device)

    # Fleet statistics
    online_count = len([d for d in fleet_devices if d["status"] == "online"])
    low_battery = len([d for d in fleet_devices if d.get("battery_level", 100) < 20])

    fleet_stats = {
        "total_devices": len(fleet_devices),
        "online_devices": online_count,
        "offline_devices": len(fleet_devices) - online_count,
        "low_battery_devices": low_battery,
        "fleet_health": round(online_count / len(fleet_devices), 2) if fleet_devices else 0,
        "average_signal": round(sum(d["signal_strength"] for d in fleet_devices) / len(fleet_devices), 1)
    }

    return {
        "fleet_id": operation_id,
        "fleet_devices": fleet_devices,
        "fleet_statistics": fleet_stats,
        "management_actions": [
            "Update firmware on devices",
            "Replace low battery devices",
            "Optimize network connectivity"
        ][:random.randint(1, 3)],
        "managed_at": datetime.now().isoformat()
    }

@mcp.tool()
def test_device_scenarios(device_id: str, test_scenarios: List[str]) -> Dict[str, Any]:
    """Test device with various scenarios """
    operation_id = log_action("TEST_SCENARIOS", {
        "device_id": device_id,
        "scenarios_count": len(test_scenarios)
    })

    test_hash = hash(f"{device_id}_{'_'.join(test_scenarios)}")
    random.seed(test_hash)

    # Generate test results
    test_results = []

    for scenario in test_scenarios:
        test_result = {
            "scenario": scenario,
            "test_status": random.choice(["pass", "pass", "fail", "warning"]),  # 50% pass rate
            "execution_time": round(random.uniform(0.5, 5.0), 1),
            "performance_metrics": {
                "response_time": round(random.uniform(10, 500), 1),
                "throughput": round(random.uniform(1, 100), 1),
                "error_rate": round(random.uniform(0, 0.1), 3)
            }
        }

        if test_result["test_status"] == "fail":
            test_result["failure_reason"] = random.choice([
                "Timeout exceeded",
                "Invalid response format",
                "Connection failed",
                "Authentication error"
            ])
        elif test_result["test_status"] == "warning":
            test_result["warning"] = "Performance below optimal thresholds"

        test_results.append(test_result)

    # Overall test summary
    passed = len([r for r in test_results if r["test_status"] == "pass"])
    total_time = sum(r["execution_time"] for r in test_results)

    test_summary = {
        "total_scenarios": len(test_scenarios),
        "passed_tests": passed,
        "failed_tests": len([r for r in test_results if r["test_status"] == "fail"]),
        "success_rate": round(passed / len(test_scenarios), 2),
        "total_execution_time": round(total_time, 1),
        "overall_status": "passed" if passed == len(test_scenarios) else "partial" if passed > 0 else "failed"
    }

    return {
        "test_id": operation_id,
        "device_id": device_id,
        "test_results": test_results,
        "test_summary": test_summary,
        "tested_at": datetime.now().isoformat()
    }

@mcp.tool()
def generate_device_data(device_id: str, data_config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate synthetic device data """
    operation_id = log_action("GENERATE_DATA", {
        "device_id": device_id,
        "data_points": data_config.get("count", 100)
    })

    data_count = min(data_config.get("count", 100), 1000)  # Limit to 1000 points
    data_type = data_config.get("type", "sensor_reading")

    data_hash = hash(f"{device_id}_{str(data_config)}")
    random.seed(data_hash)

    # Generate data points
    data_points = []
    base_time = datetime.now()

    for i in range(data_count):
        timestamp = base_time + timedelta(seconds=i * random.randint(1, 60))

        data_point = {
            "timestamp": timestamp.isoformat(),
            "sequence_id": i + 1
        }

        if data_type == "sensor_reading":
            data_point.update({
                "temperature": round(random.uniform(18, 35), 1),
                "humidity": round(random.uniform(30, 80), 1),
                "pressure": round(random.uniform(980, 1020), 1)
            })
        elif data_type == "network_metrics":
            data_point.update({
                "latency_ms": round(random.uniform(10, 200), 1),
                "packet_loss": round(random.uniform(0, 0.05), 3),
                "bandwidth_mbps": round(random.uniform(1, 100), 1)
            })
        else:  # generic
            data_point.update({
                "value": round(random.uniform(0, 100), 2),
                "quality": round(random.uniform(0.8, 1.0), 2),
                "status": random.choice(["normal", "warning", "error"])
            })

        data_points.append(data_point)

    # Data statistics
    data_stats = {
        "total_points": len(data_points),
        "time_span": f"{data_count * 30} seconds",  # Approximate
        "data_type": data_type,
        "generation_rate": f"{round(len(data_points) / 60, 1)} points/minute",
        "data_quality": round(random.uniform(0.85, 0.98), 2)
    }

    return {
        "generation_id": operation_id,
        "device_id": device_id,
        "data_points": data_points[:50],  # Limit output to first 50 points
        "data_statistics": data_stats,
        "generated_at": datetime.now().isoformat()
    }

@mcp.tool()
def monitor_device_health(device_ids: List[str], monitoring_period: int = 300) -> Dict[str, Any]:
    """Monitor health of multiple devices """
    operation_id = log_action("MONITOR_HEALTH", {
        "device_count": len(device_ids),
        "period_seconds": monitoring_period
    })

    health_hash = hash(f"{'_'.join(device_ids)}_{monitoring_period}")
    random.seed(health_hash)

    # Generate health monitoring
    device_health = []

    for device_id in device_ids[:20]:  # Limit to 20 devices
        health_status = {
            "device_id": device_id,
            "overall_health": round(random.uniform(0.6, 0.98), 2),
            "uptime_percentage": round(random.uniform(85, 99.9), 1),
            "response_time_avg": round(random.uniform(50, 300), 1),
            "error_count": random.randint(0, 5),
            "last_heartbeat": (datetime.now() - timedelta(seconds=random.randint(1, 60))).isoformat(),
            "health_alerts": []
        }

        # Add alerts for unhealthy devices
        if health_status["overall_health"] < 0.8:
            health_status["health_alerts"] = [
                random.choice([
                    "High response time detected",
                    "Intermittent connectivity issues",
                    "Battery level critical",
                    "Memory usage high"
                ])
            ]

        device_health.append(health_status)

    # Overall fleet health
    avg_health = round(sum(d["overall_health"] for d in device_health) / len(device_health), 2)
    healthy_devices = len([d for d in device_health if d["overall_health"] > 0.8])

    monitoring_summary = {
        "monitoring_period": monitoring_period,
        "devices_monitored": len(device_health),
        "healthy_devices": healthy_devices,
        "unhealthy_devices": len(device_health) - healthy_devices,
        "fleet_health_average": avg_health,
        "total_alerts": sum(len(d["health_alerts"]) for d in device_health)
    }

    return {
        "monitoring_id": operation_id,
        "device_health": device_health,
        "monitoring_summary": monitoring_summary,
        "recommendations": [
            "Investigate devices with health < 80%",
            "Update firmware on problematic devices",
            "Check network connectivity"
        ][:random.randint(1, 3)],
        "monitored_at": datetime.now().isoformat()
    }

@mcp.tool()
def get_device_logs() -> Dict[str, Any]:
    """Get device platform activity logs"""
    return {
        "total_operations": len(DEVICE_LOG),
        "recent_operations": DEVICE_LOG[-10:] if DEVICE_LOG else [],
        "log_status": "active"
    }

if __name__ == "__main__":
    mcp.run()
