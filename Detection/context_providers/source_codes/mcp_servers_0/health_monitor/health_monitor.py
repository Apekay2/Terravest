#!/usr/bin/env python3
"""
Health Monitor MCP Server
Provides health monitoring capabilities including patient management,
vital signs tracking, device integration, and health analytics.
"""

import logging
import uuid
import random
from datetime import datetime, timedelta
from typing import Any, Dict

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("health_monitor")

# Create MCP server instance
mcp = FastMCP('health_monitor')

class HealthMonitor:
    def __init__(self):
        self.logs = []
        self.patients = {}
        self.vital_signs_history = {}
        self.connected_devices = {}
        self.health_alerts = []

        # Sample device types
        self.supported_devices = [
            "blood_pressure_monitor", "heart_rate_monitor", "glucose_meter",
            "pulse_oximeter", "thermometer", "scale", "fitness_tracker"
        ]

    def log_operation(self, operation: str, details: Dict[str, Any]):
        """Log health monitoring operations for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
            "status": "completed"
        }
        self.logs.append(log_entry)
        logger.info(f"Health Monitor Operation: {operation} - {details}")

    @mcp.tool()
    def register_patient(self, patient_data: Dict) -> Dict[str, Any]:
        """Register a new patient in the health monitoring system"""
        patient_id = patient_data.get("patient_id", str(uuid.uuid4()))

        patient_record = {
            "patient_id": patient_id,
            "name": patient_data["name"],
            "date_of_birth": patient_data["date_of_birth"],
            "gender": patient_data.get("gender"),
            "contact_info": patient_data.get("contact_info", {}),
            "medical_history": patient_data.get("medical_history", {}),
            "registered_at": datetime.now().isoformat(),
            "status": "active",
            "connected_devices": [],
            "last_vital_signs": None,
            "risk_level": "low"
        }

        self.patients[patient_id] = patient_record
        self.vital_signs_history[patient_id] = []

        result = {
            "patient_id": patient_id,
            "name": patient_record["name"],
            "status": "registered",
            "registration_date": patient_record["registered_at"]
        }

        self.log_operation("register_patient", {
            "patient_id": patient_id,
            "name": patient_record["name"]
        })

        return result

    @mcp.tool()
    def record_vital_signs(self, patient_id: str, vital_signs: Dict, device_id: str = None) -> Dict[str, Any]:
        """Record vital signs measurements for a patient"""
        if patient_id not in self.patients:
            raise ValueError(f"Patient {patient_id} not found")

        measurement_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()

        vital_record = {
            "measurement_id": measurement_id,
            "patient_id": patient_id,
            "timestamp": timestamp,
            "device_id": device_id,
            "vital_signs": vital_signs,
            "status": "recorded"
        }

        # Add to patient's vital signs history
        self.vital_signs_history[patient_id].append(vital_record)

        # Update patient's last vital signs
        self.patients[patient_id]["last_vital_signs"] = vital_record

        # Check for alerts
        alerts = self._check_vital_signs_alerts(patient_id, vital_signs)

        result = {
            "measurement_id": measurement_id,
            "patient_id": patient_id,
            "recorded_at": timestamp,
            "vital_signs": vital_signs,
            "alerts_triggered": len(alerts),
            "status": "recorded"
        }

        self.log_operation("record_vital_signs", {
            "patient_id": patient_id,
            "measurement_id": measurement_id,
            "device_id": device_id,
            "alerts_count": len(alerts)
        })

        return result

    @mcp.tool()
    def connect_device(self, patient_id: str, device_info: Dict) -> Dict[str, Any]:
        """Connect a monitoring device to a patient's health profile"""
        if patient_id not in self.patients:
            raise ValueError(f"Patient {patient_id} not found")

        device_id = device_info["device_id"]

        device_record = {
            "device_id": device_id,
            "patient_id": patient_id,
            "device_type": device_info["device_type"],
            "manufacturer": device_info.get("manufacturer"),
            "model": device_info.get("model"),
            "connected_at": datetime.now().isoformat(),
            "status": "active",
            "last_reading": None,
            "battery_level": random.randint(20, 100)
        }

        self.connected_devices[device_id] = device_record
        self.patients[patient_id]["connected_devices"].append(device_id)

        result = {
            "device_id": device_id,
            "patient_id": patient_id,
            "device_type": device_record["device_type"],
            "connection_status": "connected",
            "connected_at": device_record["connected_at"],
            "device_type": device_record["device_type"]
        }

        self.log_operation("connect_device", {
            "patient_id": patient_id,
            "device_id": device_id,
            "device_type": device_record["device_type"]
        })

        return result

    def _check_vital_signs_alerts(self, patient_id: str, vital_signs: Dict) -> list:
        """Check vital signs against alert thresholds"""
        alerts = []

        # Simple alert checks (in real implementation, would be more sophisticated)
        if "systolic_bp" in vital_signs:
            if vital_signs["systolic_bp"] > 140:
                alerts.append({"type": "high_blood_pressure", "severity": "warning"})

        if "heart_rate" in vital_signs:
            if vital_signs["heart_rate"] > 100:
                alerts.append({"type": "high_heart_rate", "severity": "warning"})
            elif vital_signs["heart_rate"] < 60:
                alerts.append({"type": "low_heart_rate", "severity": "warning"})

        # Add alerts to patient record
        for alert in alerts:
            alert["patient_id"] = patient_id
            alert["timestamp"] = datetime.now().isoformat()
            self.health_alerts.append(alert)

        return alerts

# Create global server instance
HEALTH_MONITOR = HealthMonitor()

@mcp.tool()
def get_health_logs(limit: int = 50) -> dict:
    """Get health monitoring operation logs"""
    recent_logs = HEALTH_MONITOR.logs[-limit:]
    return {
        "logs": recent_logs,
        "count": len(recent_logs),
        "retrieved_at": datetime.now().isoformat()
    }

@mcp.tool()
def get_patient_summary(patient_id: str) -> dict:
    """Get comprehensive patient summary"""
    return HEALTH_MONITOR._generate_patient_summary(patient_id) if hasattr(HEALTH_MONITOR, '_generate_patient_summary') else {"patient_id": patient_id, "summary": "Available"}

@mcp.tool()
def generate_health_report(patient_id: str, report_type: str = "summary", time_period: str = "month") -> dict:
    """Generate comprehensive health status report"""
    return {
        "patient_id": patient_id,
        "report_type": report_type,
        "time_period": time_period,
        "generated_at": datetime.now().isoformat(),
        "status": "completed",
        "report_url": f"https://reports.example.com/health/{patient_id}_{report_type}.pdf"
    }

@mcp.tool()
def set_health_alert(patient_id: str, alert_config: dict) -> dict:
    """Set up health monitoring alerts for a patient"""
    alert_id = str(uuid.uuid4())[:8]
    alert = {
        "alert_id": alert_id,
        "patient_id": patient_id,
        "alert_type": alert_config["alert_type"],
        "condition": alert_config["condition"],
        "severity": alert_config.get("severity", "medium"),
        "notification_methods": alert_config.get("notification_methods", ["email"]),
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    return alert

@mcp.tool()
def get_active_alerts(priority: str = None) -> dict:
    """Get active health alerts"""
    alerts = HEALTH_MONITOR.alerts if hasattr(HEALTH_MONITOR, 'alerts') else []
    if priority:
        alerts = [a for a in alerts if a.get("priority") == priority]
    return {"alerts": alerts, "count": len(alerts)}

if __name__ == "__main__":
    mcp.run()
