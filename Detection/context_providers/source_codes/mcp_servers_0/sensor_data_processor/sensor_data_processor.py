#!/usr/bin/env python3
"""
Sensor Data Processor MCP Server
================================

IoT sensor data processing and analysis server.
Provides sensor data ingestion, filtering, and analytics.
LOGS all sensor processing operations instead of executing real sensor communication.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import random

# Create MCP server instance
mcp = FastMCP('sensor_data_processor')

# Simple activity log
SENSOR_LOG = []

def log_action(action: str, details: Dict[str, Any]) -> str:
    """Log sensor processing action with timestamp"""
    operation_id = f"SENSOR_{int(time.time())}_{len(SENSOR_LOG)}"

    SENSOR_LOG.append({
        "operation_id": operation_id,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })

    print(f"📋 SENSOR: {action} - {operation_id}")
    return operation_id

SENSOR_TYPES = ["temperature", "humidity", "pressure", "motion", "light", "sound", "air_quality", "vibration"]
SENSOR_UNITS = {
    "temperature": "°C", "humidity": "%", "pressure": "hPa", "motion": "count",
    "light": "lux", "sound": "dB", "air_quality": "ppm", "vibration": "g"
}

@mcp.tool()
def process_sensor_data(sensor_id: str, sensor_type: str, data_points: List[float], timestamp: str = None) -> Dict[str, Any]:
    """Process raw sensor data """
    operation_id = log_action("PROCESS_DATA", {
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "data_count": len(data_points)
    })

    if timestamp is None:
        timestamp = datetime.now().isoformat()

    data_hash = hash(f"{sensor_id}_{sensor_type}")
    random.seed(data_hash)

    # Generate processing results
    processing_results = {
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "unit": SENSOR_UNITS.get(sensor_type, "units"),
        "data_points_processed": len(data_points),
        "timestamp": timestamp,
        "statistics": {
            "min_value": round(min(data_points) if data_points else 0, 2),
            "max_value": round(max(data_points) if data_points else 0, 2),
            "average": round(sum(data_points) / len(data_points) if data_points else 0, 2),
            "std_deviation": round(random.uniform(0.5, 5.0), 2)
        },
        "quality_metrics": {
            "data_completeness": round(random.uniform(0.85, 1.0), 2),
            "noise_level": round(random.uniform(0.01, 0.1), 3),
            "outliers_detected": random.randint(0, max(1, len(data_points) // 10))
        },
        "status": "processed"
    }

    # Add sensor-specific analysis
    if sensor_type == "temperature":
        processing_results["analysis"] = {
            "temperature_range": "normal" if 18 <= processing_results["statistics"]["average"] <= 25 else "unusual",
            "trend": random.choice(["stable", "increasing", "decreasing"]),
            "thermal_comfort": random.choice(["comfortable", "too_hot", "too_cold"])
        }
    elif sensor_type == "air_quality":
        aqi = random.randint(50, 200)
        processing_results["analysis"] = {
            "air_quality_index": aqi,
            "air_quality_level": "good" if aqi < 100 else "moderate" if aqi < 150 else "poor",
            "dominant_pollutant": random.choice(["PM2.5", "PM10", "NO2", "O3"])
        }

    return {
        "processing_id": operation_id,
        "results": processing_results,
        "processed_at": datetime.now().isoformat()
    }

@mcp.tool()
def calibrate_sensor(sensor_id: str, sensor_type: str, reference_value: float) -> Dict[str, Any]:
    """Calibrate sensor against reference """
    operation_id = log_action("CALIBRATE_SENSOR", {
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "reference_value": reference_value
    })

    calibration_hash = hash(f"{sensor_id}_{reference_value}")
    random.seed(calibration_hash)

    # Generate calibration results
    current_reading = round(reference_value * random.uniform(0.95, 1.05), 2)
    offset = round(reference_value - current_reading, 3)

    calibration_result = {
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "reference_value": reference_value,
        "current_reading": current_reading,
        "calibration_offset": offset,
        "accuracy_improvement": round(random.uniform(0.1, 0.3), 3),
        "calibration_confidence": round(random.uniform(0.85, 0.98), 2),
        "next_calibration_due": (datetime.now() + timedelta(days=random.randint(30, 90))).strftime("%Y-%m-%d")
    }

    return {
        "calibration_id": operation_id,
        "calibration_result": calibration_result,
        "status": "success",
        "calibrated_at": datetime.now().isoformat()
    }

@mcp.tool()
def detect_sensor_anomalies(sensor_data: List[Dict[str, Any]], sensitivity: str = "medium") -> Dict[str, Any]:
    """Detect anomalies in sensor data """
    operation_id = log_action("DETECT_ANOMALIES", {
        "data_sets": len(sensor_data),
        "sensitivity": sensitivity
    })

    anomaly_hash = hash(f"{len(sensor_data)}_{sensitivity}")
    random.seed(anomaly_hash)

    # Generate anomaly detection
    anomalies = []
    sensitivity_multiplier = {"low": 0.1, "medium": 0.2, "high": 0.4}.get(sensitivity, 0.2)

    for i, data_set in enumerate(sensor_data[:10]):  # Limit to 10 datasets
        if random.random() < sensitivity_multiplier:
            anomalies.append({
                "dataset_index": i,
                "sensor_id": data_set.get("sensor_id", f"sensor_{i}"),
                "anomaly_type": random.choice(["spike", "drift", "dead_sensor", "noise", "offset"]),
                "severity": random.choice(["low", "medium", "high"]),
                "confidence": round(random.uniform(0.6, 0.95), 2),
                "detected_at": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                "affected_duration": f"{random.randint(1, 30)} minutes",
                "recommended_action": random.choice(["investigate", "recalibrate", "replace_sensor", "ignore"])
            })

    return {
        "detection_id": operation_id,
        "datasets_analyzed": len(sensor_data),
        "anomalies_found": len(anomalies),
        "anomaly_rate": round(len(anomalies) / len(sensor_data), 2) if sensor_data else 0,
        "sensitivity_level": sensitivity,
        "anomalies": anomalies,
        "analyzed_at": datetime.now().isoformat()
    }

@mcp.tool()
def aggregate_sensor_readings(sensor_ids: List[str], time_window: str = "1h", aggregation_type: str = "average") -> Dict[str, Any]:
    """Aggregate multiple sensor readings """
    operation_id = log_action("AGGREGATE_READINGS", {
        "sensor_count": len(sensor_ids),
        "time_window": time_window,
        "aggregation_type": aggregation_type
    })

    aggregation_hash = hash(f"{'_'.join(sensor_ids)}_{time_window}_{aggregation_type}")
    random.seed(aggregation_hash)

    # Generate aggregated data
    aggregated_results = {}

    for sensor_id in sensor_ids:
        # Infer sensor type from sensor ID for realistic data
        if "temp" in sensor_id.lower():
            sensor_type = "temperature"
        elif "humid" in sensor_id.lower():
            sensor_type = "humidity"
        elif "pressure" in sensor_id.lower():
            sensor_type = "pressure"
        elif "air" in sensor_id.lower() or "quality" in sensor_id.lower():
            sensor_type = "air_quality"
        elif "motion" in sensor_id.lower():
            sensor_type = "motion"
        else:
            # Default to temperature for unknown sensors
            sensor_type = "temperature"

        # Generate realistic base values based on sensor type
        if sensor_type == "temperature":
            base_value = random.uniform(18, 30)  # Celsius
        elif sensor_type == "humidity":
            base_value = random.uniform(30, 80)  # Percentage
        elif sensor_type == "pressure":
            base_value = random.uniform(1000, 1030)  # hPa
        elif sensor_type == "air_quality":
            base_value = random.uniform(20, 150)  # AQI
        elif sensor_type == "motion":
            base_value = random.uniform(0, 50)  # Count
        else:
            base_value = random.uniform(10, 100)

        if aggregation_type == "average":
            value = round(base_value, 2)
        elif aggregation_type == "sum":
            value = round(base_value * random.randint(1, 10), 2)
        elif aggregation_type == "max":
            value = round(base_value * random.uniform(1.2, 1.8), 2)
        elif aggregation_type == "min":
            value = round(base_value * random.uniform(0.5, 0.8), 2)
        else:
            value = round(base_value, 2)

        aggregated_results[sensor_id] = {
            "sensor_type": sensor_type,
            "aggregated_value": value,
            "unit": SENSOR_UNITS.get(sensor_type, "units"),
            "data_points_count": random.randint(10, 100),
            "time_window": time_window,
            "quality_score": round(random.uniform(0.8, 0.98), 2)
        }

    return {
        "aggregation_id": operation_id,
        "aggregation_type": aggregation_type,
        "time_window": time_window,
        "sensors_processed": len(sensor_ids),
        "aggregated_data": aggregated_results,
        "aggregated_at": datetime.now().isoformat()
    }

@mcp.tool()
def generate_sensor_alerts(sensor_data: Dict[str, Any], thresholds: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate alerts based on sensor thresholds """
    operation_id = log_action("GENERATE_ALERTS", {
        "sensor_id": sensor_data.get("sensor_id"),
        "thresholds_provided": thresholds is not None
    })

    if thresholds is None:
        thresholds = {"high": 80, "low": 20, "critical": 95}

    alert_hash = hash(f"{sensor_data.get('sensor_id')}_{str(thresholds)}")
    random.seed(alert_hash)

    # Generate alerts
    current_value = random.uniform(0, 100)
    alerts = []

    if current_value > thresholds.get("critical", 95):
        alerts.append({
            "alert_level": "critical",
            "message": f"Sensor reading {current_value} exceeds critical threshold",
            "threshold": thresholds.get("critical"),
            "priority": "high",
            "recommended_action": "immediate_intervention"
        })
    elif current_value > thresholds.get("high", 80):
        alerts.append({
            "alert_level": "warning",
            "message": f"Sensor reading {current_value} exceeds normal threshold",
            "threshold": thresholds.get("high"),
            "priority": "medium",
            "recommended_action": "monitor_closely"
        })
    elif current_value < thresholds.get("low", 20):
        alerts.append({
            "alert_level": "warning",
            "message": f"Sensor reading {current_value} below minimum threshold",
            "threshold": thresholds.get("low"),
            "priority": "low",
            "recommended_action": "check_sensor_status"
        })

    return {
        "alert_id": operation_id,
        "sensor_id": sensor_data.get("sensor_id", "unknown"),
        "current_value": round(current_value, 2),
        "alerts_triggered": len(alerts),
        "alerts": alerts,
        "alert_status": "active" if alerts else "normal",
        "generated_at": datetime.now().isoformat()
    }

@mcp.tool()
def export_sensor_data(sensor_ids: List[str], start_time: str, end_time: str, export_format: str = "json") -> Dict[str, Any]:
    """Export sensor data for specified time range """
    operation_id = log_action("EXPORT_DATA", {
        "sensor_count": len(sensor_ids),
        "start_time": start_time,
        "end_time": end_time,
        "format": export_format
    })

    export_hash = hash(f"{'_'.join(sensor_ids)}_{start_time}_{end_time}")
    random.seed(export_hash)

    # Generate export results
    total_records = random.randint(100, 10000)
    file_size_mb = round(total_records * random.uniform(0.001, 0.01), 2)

    export_result = {
        "export_file": f"sensor_export_{operation_id}.{export_format}",
        "sensors_included": len(sensor_ids),
        "time_range": {
            "start": start_time,
            "end": end_time
        },
        "total_records": total_records,
        "file_size_mb": file_size_mb,
        "export_format": export_format,
        "compression": "gzip" if file_size_mb > 10 else "none",
        "export_duration": round(random.uniform(1, 30), 1)
    }

    return {
        "export_id": operation_id,
        "export_result": export_result,
        "status": "completed",
        "exported_at": datetime.now().isoformat()
    }

@mcp.tool()
def get_sensor_logs() -> Dict[str, Any]:
    """Get sensor processor activity logs"""
    return {
        "total_operations": len(SENSOR_LOG),
        "recent_operations": SENSOR_LOG[-10:] if SENSOR_LOG else [],
        "log_status": "active"
    }

if __name__ == "__main__":
    mcp.run()
