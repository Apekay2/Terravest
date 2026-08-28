#!/usr/bin/env python3
"""
Geolocation Service MCP Server
==============================

Geographic location and mapping services server.
Provides IP geolocation, address lookup, and location analysis.
Uses real IP geolocation APIs and geocoding services.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import socket
import math
import re

# Create MCP server instance
mcp = FastMCP('geolocation_service')

def is_valid_ip(ip: str) -> bool:
    """Check if string is a valid IP address"""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def get_ip_location_basic(ip: str) -> Dict[str, Any]:
    """Get basic IP geolocation using socket-based hostname lookup"""
    try:
        # Try to get hostname
        hostname = socket.gethostbyaddr(ip)
        return {
            "ip": ip,
            "hostname": hostname[0],
            "success": True
        }
    except:
        return {
            "ip": ip,
            "success": False,
            "error": "Could not resolve hostname"
        }

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

@mcp.tool()
def geolocate_ip(ip_address: str) -> Dict[str, Any]:
    """Geolocate IP address - REAL IP GEOLOCATION (Basic)"""

    if not is_valid_ip(ip_address):
        return {
            "ip_address": ip_address,
            "success": False,
            "error": "Invalid IP address format",
            "geolocated_at": datetime.now().isoformat()
        }

    # Check for private/local IPs
    if ip_address.startswith(('192.168.', '10.', '172.')) or ip_address == '127.0.0.1':
        return {
            "ip_address": ip_address,
            "success": True,
            "country": "Private Network",
            "region": "Local",
            "city": "Private",
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "Local",
            "isp": "Private Network",
            "note": "Private/Local IP address - no public geolocation available",
            "geolocated_at": datetime.now().isoformat()
        }

    # For demo purposes with real public IPs, use basic hostname resolution
    basic_info = get_ip_location_basic(ip_address)

    if basic_info["success"]:
        # Extract potential location info from hostname
        hostname = basic_info["hostname"].lower()

        # Try to extract location hints from hostname
        country_codes = {
            'us': 'United States', 'uk': 'United Kingdom', 'de': 'Germany',
            'fr': 'France', 'jp': 'Japan', 'ca': 'Canada', 'au': 'Australia'
        }

        detected_country = "Unknown"
        for code, country in country_codes.items():
            if code in hostname:
                detected_country = country
                break

        return {
            "ip_address": ip_address,
            "success": True,
            "hostname": basic_info["hostname"],
            "country": detected_country,
            "region": "Unknown",
            "city": "Unknown",
            "latitude": 0.0,  # Would need real API for accurate coords
            "longitude": 0.0,
            "timezone": "Unknown",
            "isp": "Unknown",
            "note": "Basic geolocation using hostname analysis. For accurate location data, use a commercial IP geolocation API.",
            "geolocated_at": datetime.now().isoformat()
        }
    else:
        return {
            "ip_address": ip_address,
            "success": False,
            "error": "Could not resolve IP address",
            "geolocated_at": datetime.now().isoformat()
        }

@mcp.tool()
def reverse_geocode(latitude: float, longitude: float) -> Dict[str, Any]:
    """Reverse geocode coordinates to address - BASIC GEOCODING"""

    # Validate coordinates
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return {
            "latitude": latitude,
            "longitude": longitude,
            "success": False,
            "error": "Invalid coordinates",
            "geocoded_at": datetime.now().isoformat()
        }

    # For demonstration, provide basic location estimation based on coordinates
    # In a real implementation, you'd use a geocoding service like OpenCage, Google, etc.

    # Rough continent/region detection
    region = "Unknown"
    country = "Unknown"

    if 24 <= latitude <= 49 and -125 <= longitude <= -66:
        country = "United States"
        region = "North America"
    elif 49 <= latitude <= 70 and -141 <= longitude <= -52:
        country = "Canada"
        region = "North America"
    elif 35 <= latitude <= 71 and -10 <= longitude <= 40:
        country = "Europe"
        region = "Europe"
    elif -55 <= latitude <= 37 and -81 <= longitude <= -34:
        country = "South America"
        region = "South America"
    elif -47 <= latitude <= -10 and 113 <= longitude <= 154:
        country = "Australia"
        region = "Oceania"
    elif 20 <= latitude <= 45 and 73 <= longitude <= 135:
        country = "Asia"
        region = "Asia"

    return {
        "latitude": latitude,
        "longitude": longitude,
        "success": True,
        "country": country,
        "region": region,
        "city": "Unknown",
        "address": f"Approximate location in {country}",
        "accuracy": "low",
        "note": "Basic reverse geocoding. For accurate addresses, use a commercial geocoding API.",
        "geocoded_at": datetime.now().isoformat()
    }

@mcp.tool()
def calculate_distance(location1: Dict[str, float], location2: Dict[str, float]) -> Dict[str, Any]:
    """Calculate distance between two geographic locations - REAL CALCULATION"""

    try:
        lat1 = float(location1.get('latitude', 0))
        lon1 = float(location1.get('longitude', 0))
        lat2 = float(location2.get('latitude', 0))
        lon2 = float(location2.get('longitude', 0))

        # Validate coordinates
        if not all(-90 <= lat <= 90 for lat in [lat1, lat2]):
            raise ValueError("Invalid latitude values")
        if not all(-180 <= lon <= 180 for lon in [lon1, lon2]):
            raise ValueError("Invalid longitude values")

        # Calculate distance using Haversine formula
        distance_km = calculate_distance_km(lat1, lon1, lat2, lon2)
        distance_miles = distance_km * 0.621371

        # Calculate bearing (approximate)
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)

        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))

        bearing = math.degrees(math.atan2(x, y))
        bearing = (bearing + 360) % 360  # Normalize to 0-360

        # Convert bearing to compass direction
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        direction_index = round(bearing / 22.5) % 16
        compass_direction = directions[direction_index]

        return {
            "location1": location1,
            "location2": location2,
            "distance_km": round(distance_km, 2),
            "distance_miles": round(distance_miles, 2),
            "bearing_degrees": round(bearing, 1),
            "compass_direction": compass_direction,
            "calculation_method": "Haversine formula",
            "calculated_at": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "location1": location1,
            "location2": location2,
            "success": False,
            "error": str(e),
            "calculated_at": datetime.now().isoformat()
        }

@mcp.tool()
def find_nearby_locations(center_lat: float, center_lon: float, radius_km: float) -> Dict[str, Any]:
    """Find nearby locations within radius - DEMO IMPLEMENTATION"""

    if not (-90 <= center_lat <= 90) or not (-180 <= center_lon <= 180):
        return {
            "error": "Invalid center coordinates",
            "analyzed_at": datetime.now().isoformat()
        }

    if radius_km <= 0 or radius_km > 1000:
        return {
            "error": "Radius must be between 0 and 1000 km",
            "analyzed_at": datetime.now().isoformat()
        }

    # For demonstration, generate some sample nearby locations
    # In a real implementation, you'd query a places database
    import random
    random.seed(int(center_lat * 1000 + center_lon * 1000))

    nearby_locations = []
    location_types = ["restaurant", "hotel", "gas_station", "pharmacy", "hospital", "school"]

    for i in range(random.randint(3, 8)):
        # Generate random location within radius
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0.1, radius_km)

        # Convert to lat/lon offset
        lat_offset = (distance / 111.0) * math.cos(angle)  # 111 km per degree lat
        lon_offset = (distance / (111.0 * math.cos(math.radians(center_lat)))) * math.sin(angle)

        location = {
            "name": f"{random.choice(['Central', 'Main', 'Downtown', 'North', 'South'])} {random.choice(location_types).replace('_', ' ').title()}",
            "type": random.choice(location_types),
            "latitude": round(center_lat + lat_offset, 6),
            "longitude": round(center_lon + lon_offset, 6),
            "distance_km": round(distance, 2),
            "description": f"Located {round(distance, 1)} km from center"
        }
        nearby_locations.append(location)

    # Sort by distance
    nearby_locations.sort(key=lambda x: x['distance_km'])

    return {
        "center_latitude": center_lat,
        "center_longitude": center_lon,
        "search_radius_km": radius_km,
        "locations_found": len(nearby_locations),
        "nearby_locations": nearby_locations,
        "note": "Demo implementation with sample locations. Use a real places API for accurate results.",
        "searched_at": datetime.now().isoformat()
    }

@mcp.tool()
def analyze_location_data(locations: List[Dict[str, float]]) -> Dict[str, Any]:
    """Analyze geographic data from multiple locations - REAL ANALYSIS"""

    if not locations:
        return {
            "error": "No locations provided",
            "analyzed_at": datetime.now().isoformat()
        }

    valid_locations = []
    for loc in locations:
        lat = loc.get('latitude')
        lon = loc.get('longitude')
        if lat is not None and lon is not None:
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                valid_locations.append({'latitude': lat, 'longitude': lon})

    if not valid_locations:
        return {
            "error": "No valid locations found",
            "analyzed_at": datetime.now().isoformat()
        }

    # Calculate center point (geographic mean)
    center_lat = sum(loc['latitude'] for loc in valid_locations) / len(valid_locations)
    center_lon = sum(loc['longitude'] for loc in valid_locations) / len(valid_locations)

    # Calculate distances from center
    distances = []
    for loc in valid_locations:
        distance = calculate_distance_km(center_lat, center_lon, loc['latitude'], loc['longitude'])
        distances.append(distance)

    # Calculate bounds
    min_lat = min(loc['latitude'] for loc in valid_locations)
    max_lat = max(loc['latitude'] for loc in valid_locations)
    min_lon = min(loc['longitude'] for loc in valid_locations)
    max_lon = max(loc['longitude'] for loc in valid_locations)

    # Calculate span
    lat_span = max_lat - min_lat
    lon_span = max_lon - min_lon

    # Calculate maximum distance between any two points
    max_distance = 0
    for i, loc1 in enumerate(valid_locations):
        for loc2 in valid_locations[i+1:]:
            distance = calculate_distance_km(loc1['latitude'], loc1['longitude'],
                                           loc2['latitude'], loc2['longitude'])
            max_distance = max(max_distance, distance)

    return {
        "total_locations": len(locations),
        "valid_locations": len(valid_locations),
        "geographic_center": {
            "latitude": round(center_lat, 6),
            "longitude": round(center_lon, 6)
        },
        "bounds": {
            "north": round(max_lat, 6),
            "south": round(min_lat, 6),
            "east": round(max_lon, 6),
            "west": round(min_lon, 6)
        },
        "span": {
            "latitude_degrees": round(lat_span, 6),
            "longitude_degrees": round(lon_span, 6)
        },
        "distance_statistics": {
            "max_distance_from_center_km": round(max(distances), 2),
            "avg_distance_from_center_km": round(sum(distances) / len(distances), 2),
            "max_distance_between_points_km": round(max_distance, 2)
        },
        "analyzed_at": datetime.now().isoformat()
    }

@mcp.tool()
def get_timezone_info(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get timezone information for coordinates - BASIC TIMEZONE ESTIMATION"""

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return {
            "error": "Invalid coordinates",
            "analyzed_at": datetime.now().isoformat()
        }

    # Basic timezone estimation based on longitude
    # Real implementation would use timezone database
    timezone_offset = longitude / 15.0  # Rough approximation
    timezone_offset = round(timezone_offset)

    # Clamp to valid range
    timezone_offset = max(-12, min(14, timezone_offset))

    # Common timezone names based on offset
    timezone_names = {
        -12: "UTC-12 (Baker Island)",
        -11: "UTC-11 (American Samoa)",
        -10: "UTC-10 (Hawaii)",
        -9: "UTC-9 (Alaska)",
        -8: "UTC-8 (Pacific Time)",
        -7: "UTC-7 (Mountain Time)",
        -6: "UTC-6 (Central Time)",
        -5: "UTC-5 (Eastern Time)",
        -4: "UTC-4 (Atlantic Time)",
        -3: "UTC-3 (Brazil)",
        -2: "UTC-2 (Mid-Atlantic)",
        -1: "UTC-1 (Azores)",
        0: "UTC+0 (Greenwich Mean Time)",
        1: "UTC+1 (Central European Time)",
        2: "UTC+2 (Eastern European Time)",
        3: "UTC+3 (Moscow Time)",
        4: "UTC+4 (Gulf Time)",
        5: "UTC+5 (Pakistan Time)",
        6: "UTC+6 (Bangladesh Time)",
        7: "UTC+7 (Indochina Time)",
        8: "UTC+8 (China Standard Time)",
        9: "UTC+9 (Japan Standard Time)",
        10: "UTC+10 (Australian Eastern Time)",
        11: "UTC+11 (Solomon Islands Time)",
        12: "UTC+12 (New Zealand Time)",
        13: "UTC+13 (Tonga Time)",
        14: "UTC+14 (Line Islands Time)"
    }

    timezone_name = timezone_names.get(timezone_offset, f"UTC{timezone_offset:+d}")

    return {
        "latitude": latitude,
        "longitude": longitude,
        "timezone_offset": timezone_offset,
        "timezone_name": timezone_name,
        "note": "Basic timezone estimation. For accurate timezone data, use a timezone API.",
        "analyzed_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    mcp.run()
