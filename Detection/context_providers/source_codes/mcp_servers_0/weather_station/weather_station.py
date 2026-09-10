#!/usr/bin/env python3
"""
Weather Station MCP Server
Provides advanced weather monitoring and forecasting capabilities including
sensor data collection, weather alerts, climate analysis, and agricultural weather services.
"""

import json
import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather_station")

# Create MCP server instance
mcp = FastMCP('weather_station')

# Global state
WEATHER_LOGS = []
LOCATIONS = {}
WEATHER_DATA = {}
ALERTS = []
FORECASTS = {}

def log_operation(operation: str, details: Dict[str, Any]):
    """Log weather station operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    WEATHER_LOGS.append(log_entry)
    logger.info(f"Weather Station Operation: {operation} - {details}")

# Initialize sample locations
def initialize_sample_locations():
    """Initialize sample weather monitoring locations"""
    global LOCATIONS
    LOCATIONS = {
        "NYC001": {
            "name": "New York City - Central Park",
            "latitude": 40.7829,
            "longitude": -73.9654,
            "elevation_m": 40,
            "timezone": "America/New_York",
            "sensors": ["temp", "humidity", "pressure", "wind", "rain"]
        },
        "LA001": {
            "name": "Los Angeles - Downtown",
            "latitude": 34.0522,
            "longitude": -118.2437,
            "elevation_m": 87,
            "timezone": "America/Los_Angeles",
            "sensors": ["temp", "humidity", "pressure", "wind", "solar"]
        },
        "CHI001": {
            "name": "Chicago - O'Hare",
            "latitude": 41.9742,
            "longitude": -87.9073,
            "elevation_m": 201,
            "timezone": "America/Chicago",
            "sensors": ["temp", "humidity", "pressure", "wind", "rain", "snow"]
        }
    }

initialize_sample_locations()

@mcp.tool()
def get_current_weather(location_id: str) -> Dict[str, Any]:
    """Get current weather conditions for a location"""
    if location_id not in LOCATIONS:
        raise ValueError(f"Location {location_id} not found")

    location = LOCATIONS[location_id]

    # Generate realistic weather data
    current_weather = {
        "location_id": location_id,
        "location_name": location["name"],
        "observation_time": datetime.now().isoformat(),
        "temperature_celsius": round(random.uniform(-10, 35), 1),
        "feels_like_celsius": round(random.uniform(-15, 40), 1),
        "humidity_percent": random.randint(30, 95),
        "pressure_hpa": round(random.uniform(980, 1030), 1),
        "wind_speed_kmh": round(random.uniform(0, 50), 1),
        "wind_direction_degrees": random.randint(0, 360),
        "wind_direction_text": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
        "visibility_km": round(random.uniform(5, 50), 1),
        "uv_index": random.randint(0, 11),
        "cloud_cover_percent": random.randint(0, 100),
        "weather_condition": random.choice([
            "sunny", "partly_cloudy", "cloudy", "overcast",
            "light_rain", "heavy_rain", "thunderstorm", "snow", "fog"
        ]),
        "precipitation_mm": round(random.uniform(0, 25), 1),
        "dewpoint_celsius": round(random.uniform(-5, 25), 1),
        "air_quality_index": random.randint(1, 150),
        "sunrise": "06:30:00",
        "sunset": "19:45:00"
    }

    # Store current data
    WEATHER_DATA[f"{location_id}_current"] = current_weather

    log_operation("get_current_weather", {
        "location_id": location_id,
        "location_name": location["name"],
        "temperature": current_weather["temperature_celsius"],
        "condition": current_weather["weather_condition"]
    })

    return current_weather

@mcp.tool()
def generate_forecast(location_id: str, forecast_days: int = 7) -> Dict[str, Any]:
    """Generate weather forecast for a location"""
    if location_id not in LOCATIONS:
        raise ValueError(f"Location {location_id} not found")

    location = LOCATIONS[location_id]
    forecast_id = str(uuid.uuid4())

    # Generate daily forecasts
    daily_forecasts = []
    base_temp = random.uniform(10, 25)

    for day in range(forecast_days):
        forecast_date = datetime.now() + timedelta(days=day)

        # Add some variation to temperature
        temp_variation = random.uniform(-5, 5)
        high_temp = base_temp + temp_variation + random.uniform(5, 10)
        low_temp = base_temp + temp_variation - random.uniform(2, 8)

        daily_forecast = {
            "date": forecast_date.strftime("%Y-%m-%d"),
            "day_of_week": forecast_date.strftime("%A"),
            "high_temperature_celsius": round(high_temp, 1),
            "low_temperature_celsius": round(low_temp, 1),
            "humidity_percent": random.randint(40, 85),
            "wind_speed_kmh": round(random.uniform(5, 30), 1),
            "precipitation_chance_percent": random.randint(0, 80),
            "precipitation_mm": round(random.uniform(0, 15), 1),
            "weather_condition": random.choice([
                "sunny", "partly_cloudy", "cloudy", "light_rain", "thunderstorm"
            ]),
            "uv_index": random.randint(1, 9),
            "sunrise": "06:30:00",
            "sunset": "19:45:00"
        }
        daily_forecasts.append(daily_forecast)

    forecast = {
        "forecast_id": forecast_id,
        "location_id": location_id,
        "location_name": location["name"],
        "generated_at": datetime.now().isoformat(),
        "forecast_days": forecast_days,
        "daily_forecasts": daily_forecasts,
        "forecast_model": "Advanced Weather Model v2.1",
        "accuracy_confidence": round(random.uniform(0.75, 0.95), 2)
    }

    # Store forecast
    FORECASTS[forecast_id] = forecast

    log_operation("generate_forecast", {
        "location_id": location_id,
        "forecast_days": forecast_days,
        "forecast_id": forecast_id
    })

    return forecast

@mcp.tool()
def create_weather_alert(alert_config: Dict) -> Dict[str, Any]:
    """Create a weather alert based on conditions"""
    alert_id = str(uuid.uuid4())
    alert_types = ["severe_weather", "temperature_extreme", "precipitation", "wind", "air_quality"]

    alert = {
        "alert_id": alert_id,
        "alert_type": alert_config.get("type", random.choice(alert_types)),
        "location_id": alert_config.get("location_id", "NYC001"),
        "severity": alert_config.get("severity", random.choice(["low", "medium", "high", "critical"])),
        "title": alert_config.get("title", f"Weather Alert {alert_id[:8]}"),
        "description": alert_config.get("description", "Automated weather alert generated"),
        "threshold_conditions": alert_config.get("conditions", {}),
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
        "is_active": True,
        "notification_channels": alert_config.get("channels", ["email", "sms"])
    }

    ALERTS.append(alert)

    log_operation("create_weather_alert", {
        "alert_id": alert_id,
        "alert_type": alert["alert_type"],
        "severity": alert["severity"],
        "location_id": alert["location_id"]
    })

    return alert

@mcp.tool()
def analyze_climate_trends(location_id: str, analysis_period: str = "year") -> Dict[str, Any]:
    """Analyze climate trends for a location over specified period"""
    if location_id not in LOCATIONS:
        raise ValueError(f"Location {location_id} not found")

    location = LOCATIONS[location_id]
    analysis_id = str(uuid.uuid4())

    # Generate trend analysis data
    trend_analysis = {
        "analysis_id": analysis_id,
        "location_id": location_id,
        "location_name": location["name"],
        "analysis_period": analysis_period,
        "analyzed_at": datetime.now().isoformat(),
        "temperature_trends": {
            "average_change_celsius": round(random.uniform(-2, 3), 2),
            "warming_trend": random.choice([True, False]),
            "seasonal_variation": round(random.uniform(15, 30), 1)
        },
        "precipitation_trends": {
            "annual_change_percent": round(random.uniform(-15, 20), 1),
            "wet_season_intensity": random.choice(["increasing", "stable", "decreasing"]),
            "drought_frequency": random.choice(["rare", "occasional", "frequent"])
        },
        "extreme_events": {
            "heat_wave_frequency": random.randint(0, 5),
            "severe_storm_frequency": random.randint(0, 8),
            "temperature_records_broken": random.randint(0, 3)
        },
        "confidence_score": round(random.uniform(0.7, 0.95), 2)
    }

    log_operation("analyze_climate_trends", {
        "location_id": location_id,
        "analysis_period": analysis_period,
        "analysis_id": analysis_id
    })

    return trend_analysis

@mcp.tool()
def get_agricultural_weather(location_id: str, crop_type: str = "general") -> Dict[str, Any]:
    """Get weather data optimized for agricultural applications"""
    if location_id not in LOCATIONS:
        raise ValueError(f"Location {location_id} not found")

    current_weather = get_current_weather(location_id)

    # Add agricultural-specific data
    agricultural_data = {
        **current_weather,
        "crop_type": crop_type,
        "growing_degree_days": round(random.uniform(0, 25), 1),
        "soil_temperature_celsius": round(random.uniform(5, 30), 1),
        "soil_moisture_percent": random.randint(20, 90),
        "evapotranspiration_mm": round(random.uniform(2, 8), 2),
        "frost_risk": random.choice(["none", "low", "moderate", "high"]),
        "disease_pressure": {
            "fungal": random.choice(["low", "moderate", "high"]),
            "bacterial": random.choice(["low", "moderate", "high"]),
            "viral": random.choice(["low", "moderate"])
        },
        "pest_activity": random.choice(["minimal", "low", "moderate", "high"]),
        "irrigation_recommendation": random.choice(["none", "light", "moderate", "heavy"]),
        "field_work_conditions": random.choice(["poor", "fair", "good", "excellent"])
    }

    log_operation("get_agricultural_weather", {
        "location_id": location_id,
        "crop_type": crop_type
    })

    return agricultural_data

@mcp.tool()
def list_weather_locations() -> Dict[str, Any]:
    """List all available weather monitoring locations"""
    locations_info = {
        lid: {k: v for k, v in info.items() if k != "sensors"}
        for lid, info in LOCATIONS.items()
    }

    log_operation("list_weather_locations", {"total_locations": len(LOCATIONS)})

    return {
        "total_locations": len(LOCATIONS),
        "locations": locations_info
    }

@mcp.tool()
def get_weather_logs(limit: int = 50) -> Dict[str, Any]:
    """Retrieve weather station operation logs"""
    recent_logs = WEATHER_LOGS[-limit:]

    return {
        "total_operations": len(WEATHER_LOGS),
        "recent_operations": recent_logs,
        "log_status": "active"
    }

if __name__ == "__main__":
    mcp.run()
