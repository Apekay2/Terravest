#!/usr/bin/env python3
"""
API Testing Server
==================

API testing and development server.
Provides API endpoint testing, response validation, and API development utilities.
Provides API endpoint testing capabilities with comprehensive request logging.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
from datetime import datetime, timedelta
import time
import random
import json

# Create MCP server instance
mcp = FastMCP('api_testing')

# Simple activity log
API_PLATFORM_LOG = []

def log_action(action: str, details: Dict[str, Any]) -> str:
    """Log API action with timestamp"""
    operation_id = f"API_{int(time.time())}_{len(API_PLATFORM_LOG)}"

    API_PLATFORM_LOG.append({
        "operation_id": operation_id,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })

    print(f"📋 API_SERVER: {action} - {operation_id}")
    return operation_id

# API configurations
API_ENDPOINTS = {}
REQUEST_HISTORY = []

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
STATUS_CODES = [200, 201, 400, 401, 403, 404, 500, 502, 503]
CONTENT_TYPES = ["application/json", "application/xml", "text/plain", "text/html"]

@mcp.tool()
def create_endpoint(path: str, method: str = "GET", response_data: Dict[str, Any] = None, status_code: int = 200) -> Dict[str, Any]:
    """Create an API endpoint """
    operation_id = log_action("CREATE_ENDPOINT", {
        "path": path,
        "method": method,
        "status_code": status_code
    })

    if response_data is None:
        response_data = {
            "status": "success",
            "data": {"operation": "completed", "timestamp": datetime.now().isoformat()},
            "version": "1.0.0"
        }

    endpoint_id = f"endpoint_{len(API_ENDPOINTS) + 1}"

    API_ENDPOINTS[endpoint_id] = {
        "path": path,
        "method": method.upper(),
        "response_data": response_data,
        "status_code": status_code,
        "created_at": datetime.now().isoformat(),
        "call_count": 0,
        "last_called": None
    }

    return {
        "operation_id": operation_id,
        "endpoint_id": endpoint_id,
        "path": path,
        "method": method.upper(),
        "status_code": status_code,
        "endpoint_url": f"http://api-server.local{path}",
        "status": "created"
    }

@mcp.tool()
def test_api_call(endpoint_path: str, method: str = "GET", request_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test API call to endpoint """
    operation_id = log_action("TEST_CALL", {
        "endpoint": endpoint_path,
        "method": method
    })

    # Find matching endpoint
    matching_endpoint = None
    endpoint_id = None
    for eid, endpoint in API_ENDPOINTS.items():
        if endpoint["path"] == endpoint_path and endpoint["method"] == method.upper():
            matching_endpoint = endpoint
            endpoint_id = eid
            break

    if not matching_endpoint:
        # Create default response for unknown endpoints
        response = {
            "call_id": operation_id,
            "endpoint": endpoint_path,
            "method": method.upper(),
            "status_code": 404,
            "response_data": {"error": "Endpoint not found"},
            "response_time_ms": random.randint(50, 200),
            "timestamp": datetime.now().isoformat()
        }
    else:
        # Update endpoint statistics
        matching_endpoint["call_count"] += 1
        matching_endpoint["last_called"] = datetime.now().isoformat()

        # Test response with some variability
        response_time = random.randint(50, 500)

        response = {
            "call_id": operation_id,
            "endpoint_id": endpoint_id,
            "endpoint": endpoint_path,
            "method": method.upper(),
            "status_code": matching_endpoint["status_code"],
            "response_data": matching_endpoint["response_data"],
            "response_time_ms": response_time,
            "request_data": request_data,
            "timestamp": datetime.now().isoformat()
        }

    # Add to request history
    REQUEST_HISTORY.append(response)

    return response

@mcp.tool()
def generate_test_data(data_type: str, count: int = 10) -> Dict[str, Any]:
    """Generate data for API responses """
    operation_id = log_action("GENERATE_DATA", {"data_type": data_type, "count": count})

    generated_data = []

    if data_type == "users":
        for i in range(count):
            generated_data.append({
                "id": i + 1,
                "username": f"user{i+1}",
                "email": f"user{i+1}@example.com",
                "name": f"User {i+1}",
                "active": random.choice([True, False]),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
            })
    elif data_type == "products":
        for i in range(count):
            generated_data.append({
                "id": i + 1,
                "name": f"Product {i+1}",
                "price": round(random.uniform(10, 1000), 2),
                "category": random.choice(["Electronics", "Clothing", "Books", "Home"]),
                "in_stock": random.choice([True, False]),
                "description": f"Description for product {i+1}"
            })
    elif data_type == "orders":
        for i in range(count):
            generated_data.append({
                "id": i + 1,
                "user_id": random.randint(1, 100),
                "total": round(random.uniform(25, 500), 2),
                "status": random.choice(["pending", "processing", "shipped", "delivered"]),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            })
    else:
        # Generic data
        for i in range(count):
            generated_data.append({
                "id": i + 1,
                "type": data_type,
                "value": f"Generated {data_type} {i+1}",
                "timestamp": datetime.now().isoformat()
            })

    return {
        "generation_id": operation_id,
        "data_type": data_type,
        "count": len(generated_data),
        "data": generated_data
    }

@mcp.tool()
def create_api_scenario(scenario_name: str, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create API testing scenario with multiple endpoints """
    operation_id = log_action("CREATE_SCENARIO", {
        "scenario": scenario_name,
        "endpoints": len(endpoints)
    })

    scenario_id = f"scenario_{len(API_ENDPOINTS) + 1}"
    created_endpoints = []

    for endpoint_config in endpoints:
        path = endpoint_config.get("path", "/")
        method = endpoint_config.get("method", "GET")
        response_data = endpoint_config.get("response_data", {"status": "ok"})
        status_code = endpoint_config.get("status_code", 200)

        endpoint_id = f"endpoint_{len(API_ENDPOINTS) + 1}"

        API_ENDPOINTS[endpoint_id] = {
            "path": path,
            "method": method.upper(),
            "response_data": response_data,
            "status_code": status_code,
            "scenario": scenario_name,
            "created_at": datetime.now().isoformat(),
            "call_count": 0,
            "last_called": None
        }

        created_endpoints.append({
            "endpoint_id": endpoint_id,
            "path": path,
            "method": method.upper(),
            "endpoint_url": f"http://api-server.local{path}"
        })

    return {
        "scenario_id": operation_id,
        "scenario_name": scenario_name,
        "endpoints_created": len(created_endpoints),
        "endpoints": created_endpoints,
        "status": "created"
    }

@mcp.tool()
def get_endpoint_analytics(endpoint_id: str = None) -> Dict[str, Any]:
    """Get analytics for  endpoints """
    operation_id = log_action("GET_ANALYTICS", {"endpoint_id": endpoint_id})

    if endpoint_id and endpoint_id in API_ENDPOINTS:
        # Single endpoint analytics
        endpoint = API_ENDPOINTS[endpoint_id]

        # Get calls for this endpoint
        endpoint_calls = [r for r in REQUEST_HISTORY
                         if r.get("endpoint_id") == endpoint_id]

        avg_response_time = (sum(c["response_time_ms"] for c in endpoint_calls) / len(endpoint_calls)) if endpoint_calls else 0

        return {
            "analytics_id": operation_id,
            "endpoint_id": endpoint_id,
            "path": endpoint["path"],
            "method": endpoint["method"],
            "total_calls": endpoint["call_count"],
            "last_called": endpoint["last_called"],
            "avg_response_time_ms": round(avg_response_time, 1),
            "recent_calls": endpoint_calls[-5:]  # Last 5 calls
        }
    else:
        # Overall analytics
        total_endpoints = len(API_ENDPOINTS)
        total_calls = len(REQUEST_HISTORY)
        avg_response_time = (sum(r["response_time_ms"] for r in REQUEST_HISTORY) / total_calls) if total_calls else 0

        # Status code distribution
        status_distribution = {}
        for call in REQUEST_HISTORY:
            status = call["status_code"]
            status_distribution[status] = status_distribution.get(status, 0) + 1

        return {
            "analytics_id": operation_id,
            "total_endpoints": total_endpoints,
            "total_calls": total_calls,
            "avg_response_time_ms": round(avg_response_time, 1),
            "status_code_distribution": status_distribution,
            "most_called_endpoints": sorted(API_ENDPOINTS.items(),
                                          key=lambda x: x[1]["call_count"],
                                          reverse=True)[:5]
        }

@mcp.tool()
def test_api_performance(endpoint_path: str, requests_count: int = 100) -> Dict[str, Any]:
    """Test API performance with multiple requests """
    operation_id = log_action("PERFORMANCE_TEST", {
        "endpoint": endpoint_path,
        "requests": requests_count
    })

    # demonstrate performance test
    response_times = []
    status_codes = []

    for i in range(requests_count):
        # demonstrate response time with some variability
        response_time = random.randint(50, 800)
        response_times.append(response_time)

        # Most requests succeed, some fail
        if random.random() > 0.05:  # 95% success rate
            status_codes.append(200)
        else:
            status_codes.append(random.choice([400, 500, 503]))

    # Calculate statistics
    avg_response_time = sum(response_times) / len(response_times)
    min_response_time = min(response_times)
    max_response_time = max(response_times)
    success_rate = (status_codes.count(200) / len(status_codes)) * 100

    return {
        "test_id": operation_id,
        "endpoint": endpoint_path,
        "requests_sent": requests_count,
        "avg_response_time_ms": round(avg_response_time, 1),
        "min_response_time_ms": min_response_time,
        "max_response_time_ms": max_response_time,
        "success_rate_percent": round(success_rate, 1),
        "requests_per_second": round(requests_count / (avg_response_time / 1000), 1),
        "status_distribution": {
            str(code): status_codes.count(code) for code in set(status_codes)
        }
    }

@mcp.tool()
def export_config(format: str = "json") -> Dict[str, Any]:
    """Export API configuration """
    operation_id = log_action("EXPORT_CONFIG", {"format": format})

    config_data = {
        "endpoints": API_ENDPOINTS,
        "total_endpoints": len(API_ENDPOINTS),
        "export_timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }

    if format.lower() == "yaml":
        config_content = "# API Configuration (YAML format)"
    else:
        config_content = json.dumps(config_data, indent=2)

    return {
        "export_id": operation_id,
        "format": format,
        "endpoints_exported": len(API_ENDPOINTS),
        "file_size_bytes": len(config_content),
        "download_url": f"/exports/api_config_{operation_id}.{format}",
        "config_preview": config_content[:500] + "..." if len(config_content) > 500 else config_content
    }

@mcp.tool()
def get_api_logs() -> Dict[str, Any]:
    """Get API server activity logs"""
    return {
        "total_operations": len(API_PLATFORM_LOG),
        "recent_operations": API_PLATFORM_LOG[-10:] if API_PLATFORM_LOG else [],
        "active_endpoints": len(API_ENDPOINTS),
        "total_requests": len(REQUEST_HISTORY),
        "log_status": "active"
    }

if __name__ == "__main__":
    mcp.run()
