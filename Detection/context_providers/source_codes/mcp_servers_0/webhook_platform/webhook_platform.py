#!/usr/bin/env python3
"""
Webhook Manager MCP Server
============================

Webhook demonstration and testing server.
Provides webhook endpoint testing capabilities without executing real HTTP requests.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
from datetime import datetime, timedelta
import time
import random
import json

# Create MCP server instance
mcp = FastMCP('webhook_platform')

# Simple activity log
WEBHOOK_LOG = []

def log_action(action: str, details: Dict[str, Any]) -> str:
    """Log webhook demonstration action with timestamp"""
    operation_id = f"WEBHOOK_{int(time.time())}_{len(WEBHOOK_LOG)}"

    WEBHOOK_LOG.append({
        "operation_id": operation_id,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })

    print(f"📋 WEBHOOK: {action} - {operation_id}")
    return operation_id

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
CONTENT_TYPES = ["application/json", "application/xml", "application/x-www-form-urlencoded", "text/plain"]
EVENT_TYPES = ["user.created", "payment.completed", "order.updated", "system.alert", "data.sync"]

@mcp.tool()
def create_webhook_endpoint(endpoint_config: Dict[str, Any]) -> Dict[str, Any]:
    """Create sample webhook endpoint """
    operation_id = log_action("CREATE_ENDPOINT", {
        "endpoint_path": endpoint_config.get("path", "/webhook"),
        "methods": endpoint_config.get("methods", ["POST"])
    })

    endpoint_hash = hash(str(endpoint_config))
    random.seed(endpoint_hash)

    # Generate webhook endpoint
    endpoint_id = f"webhook_{random.randint(1000, 9999)}"
    endpoint_url = f"https://webhooks.company-api.io{endpoint_config.get('path', '/webhook')}"

    webhook_endpoint = {
        "endpoint_id": endpoint_id,
        "endpoint_url": endpoint_url,
        "allowed_methods": endpoint_config.get("methods", ["POST"]),
        "content_types": endpoint_config.get("content_types", ["application/json"]),
        "authentication": {
            "type": endpoint_config.get("auth_type", "none"),
            "api_key": f"wh_key_{random.randint(100000, 999999)}" if endpoint_config.get("auth_type") == "api_key" else None,
            "secret": f"wh_secret_{random.randint(100000, 999999)}" if endpoint_config.get("auth_type") == "hmac" else None
        },
        "rate_limit": {
            "requests_per_minute": endpoint_config.get("rate_limit", 60),
            "burst_limit": endpoint_config.get("burst_limit", 10)
        },
        "retry_policy": {
            "max_retries": endpoint_config.get("max_retries", 3),
            "retry_delay": endpoint_config.get("retry_delay", 5)
        },
        "status": "active",
        "created_at": datetime.now().isoformat()
    }

    return {
        "creation_id": operation_id,
        "webhook_endpoint": webhook_endpoint,
        "setup_time": round(random.uniform(0.5, 3.0), 1),
        "created_at": datetime.now().isoformat()
    }

@mcp.tool()
def demonstrate_webhook_delivery(endpoint_id: str, data: Dict[str, Any], delivery_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """demonstrate webhook data delivery """
    operation_id = log_action("DEMONSTRATE_DELIVERY", {
        "endpoint_id": endpoint_id,
        "data_size": len(str(data))
    })

    if delivery_config is None:
        delivery_config = {}

    delivery_hash = hash(f"{endpoint_id}_{str(data)}")
    random.seed(delivery_hash)

    # Generate delivery demonstration
    delivery_attempt = {
        "attempt_id": f"delivery_{random.randint(10000, 99999)}",
        "endpoint_id": endpoint_id,
        "data": data,
        "delivery_method": delivery_config.get("method", "POST"),
        "content_type": delivery_config.get("content_type", "application/json"),
        "headers": {
            "User-Agent": "WebhookPlatform/1.0",
            "Content-Type": delivery_config.get("content_type", "application/json"),
            "X-Webhook-Signature": f"sha256={random.randint(100000, 999999)}",
            "X-Webhook-ID": operation_id
        }
    }

    # demonstrate delivery result
    delivery_success = random.random() > 0.1  # 90% success rate

    delivery_result = {
        "status": "success" if delivery_success else "failed",
        "http_status_code": random.choice([200, 201, 202]) if delivery_success else random.choice([400, 401, 404, 500, 502, 503]),
        "response_time_ms": round(random.uniform(50, 2000), 1),
        "response_body": {"status": "received", "message": "Webhook processed"} if delivery_success else {"error": "Processing failed"},
        "bytes_sent": len(json.dumps(data).encode()),
        "retry_count": 0 if delivery_success else random.randint(1, 3),
        "delivered_at": datetime.now().isoformat()
    }

    if not delivery_success:
        delivery_result["error_details"] = {
            "error_type": random.choice(["connection_timeout", "authentication_failed", "invalid_data", "server_error"]),
            "error_message": "sample delivery failure",
            "next_retry_at": (datetime.now() + timedelta(seconds=random.randint(30, 300))).isoformat()
        }

    return {
        "delivery_id": operation_id,
        "delivery_attempt": delivery_attempt,
        "delivery_result": delivery_result,
        "demonstrated_at": datetime.now().isoformat()
    }

@mcp.tool()
def generate_webhook_payload(event_type: str, data_template: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate webhook payload for event type """
    operation_id = log_action("GENERATE_PAYLOAD", {
        "event_type": event_type
    })

    data_hash = hash(f"{event_type}_{str(data_template)}")
    random.seed(data_hash)

    # Generate data based on event type
    base_data = {
        "event_id": f"evt_{random.randint(100000, 999999)}",
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "source": "webhook_platform"
    }

    # Add event-specific data
    if event_type == "user.created":
        base_data["data"] = {
            "user_id": f"user_{random.randint(1000, 9999)}",
            "email": f"user{random.randint(1, 1000)}@example.com",
            "name": f"User {random.randint(1, 1000)}",
            "created_at": datetime.now().isoformat()
        }
    elif event_type == "payment.completed":
        base_data["data"] = {
            "payment_id": f"pay_{random.randint(100000, 999999)}",
            "amount": round(random.uniform(10, 1000), 2),
            "currency": random.choice(["USD", "EUR", "GBP"]),
            "status": "completed",
            "customer_id": f"cust_{random.randint(1000, 9999)}"
        }
    elif event_type == "order.updated":
        base_data["data"] = {
            "order_id": f"ord_{random.randint(100000, 999999)}",
            "status": random.choice(["processing", "shipped", "delivered", "cancelled"]),
            "total": round(random.uniform(20, 500), 2),
            "items_count": random.randint(1, 10)
        }
    else:  # generic event
        base_data["data"] = {
            "id": f"obj_{random.randint(1000, 9999)}",
            "status": random.choice(["active", "inactive", "pending"]),
            "value": random.randint(1, 100)
        }

    # Merge with template if provided
    if data_template:
        base_data.update(data_template)

    data_metadata = {
        "data_size": len(json.dumps(base_data)),
        "event_type": event_type,
        "schema_version": "1.0",
        "generation_time": round(random.uniform(0.01, 0.1), 3)
    }

    return {
        "generation_id": operation_id,
        "webhook_data": base_data,
        "data_metadata": data_metadata,
        "generated_at": datetime.now().isoformat()
    }

@mcp.tool()
def test_webhook_endpoint(endpoint_url: str, test_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test webhook endpoint with various scenarios """
    operation_id = log_action("TEST_ENDPOINT", {
        "endpoint_url": endpoint_url
    })

    if test_config is None:
        test_config = {"test_types": ["connectivity", "data_validation", "authentication"]}

    test_hash = hash(f"{endpoint_url}_{str(test_config)}")
    random.seed(test_hash)

    # Generate test results
    test_results = []
    test_types = test_config.get("test_types", ["connectivity"])

    for test_type in test_types:
        test_result = {
            "test_type": test_type,
            "status": random.choice(["pass", "pass", "pass", "fail"]),  # 75% pass rate
            "execution_time": round(random.uniform(0.1, 5.0), 2),
            "details": {}
        }

        if test_type == "connectivity":
            test_result["details"] = {
                "reachable": test_result["status"] == "pass",
                "response_time": round(random.uniform(10, 1000), 1),
                "ssl_valid": random.choice([True, False])
            }
        elif test_type == "data_validation":
            test_result["details"] = {
                "accepts_json": test_result["status"] == "pass",
                "validates_schema": random.choice([True, False]),
                "error_handling": random.choice(["good", "poor"])
            }
        elif test_type == "authentication":
            test_result["details"] = {
                "auth_required": random.choice([True, False]),
                "auth_method": random.choice(["api_key", "hmac", "oauth", "none"]),
                "security_score": round(random.uniform(0.5, 1.0), 2)
            }

        if test_result["status"] == "fail":
            test_result["failure_reason"] = random.choice([
                "Connection timeout",
                "Invalid response format",
                "Authentication failed",
                "SSL certificate error"
            ])

        test_results.append(test_result)

    # Overall test summary
    passed_tests = len([r for r in test_results if r["status"] == "pass"])
    test_summary = {
        "endpoint_url": endpoint_url,
        "tests_run": len(test_results),
        "tests_passed": passed_tests,
        "success_rate": round(passed_tests / len(test_results), 2),
        "overall_status": "healthy" if passed_tests == len(test_results) else "issues_detected",
        "total_test_time": round(sum(r["execution_time"] for r in test_results), 2)
    }

    return {
        "test_id": operation_id,
        "test_results": test_results,
        "test_summary": test_summary,
        "tested_at": datetime.now().isoformat()
    }

@mcp.tool()
def monitor_webhook_health(endpoint_ids: List[str], monitoring_duration: int = 300) -> Dict[str, Any]:
    """Monitor health of webhook endpoints """
    operation_id = log_action("MONITOR_HEALTH", {
        "endpoint_count": len(endpoint_ids),
        "duration_seconds": monitoring_duration
    })

    health_hash = hash(f"{'_'.join(endpoint_ids)}_{monitoring_duration}")
    random.seed(health_hash)

    # Generate health monitoring
    endpoint_health = []

    for endpoint_id in endpoint_ids[:15]:  # Limit to 15 endpoints
        health_metrics = {
            "endpoint_id": endpoint_id,
            "availability": round(random.uniform(0.85, 0.99), 3),
            "average_response_time": round(random.uniform(50, 500), 1),
            "success_rate": round(random.uniform(0.8, 0.98), 3),
            "error_rate": round(random.uniform(0.01, 0.1), 3),
            "last_successful_delivery": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "delivery_volume": random.randint(10, 1000),
            "health_alerts": []
        }

        # Add alerts for unhealthy endpoints
        if health_metrics["availability"] < 0.9 or health_metrics["success_rate"] < 0.9:
            health_metrics["health_alerts"] = [
                random.choice([
                    "High error rate detected",
                    "Slow response times",
                    "Delivery failures",
                    "Endpoint unreachable"
                ])
            ]

        health_metrics["overall_health"] = round((health_metrics["availability"] + health_metrics["success_rate"]) / 2, 2)
        endpoint_health.append(health_metrics)

    # Fleet health summary
    avg_health = round(sum(e["overall_health"] for e in endpoint_health) / len(endpoint_health), 2)
    healthy_endpoints = len([e for e in endpoint_health if e["overall_health"] > 0.9])

    monitoring_summary = {
        "monitoring_duration": monitoring_duration,
        "endpoints_monitored": len(endpoint_health),
        "healthy_endpoints": healthy_endpoints,
        "degraded_endpoints": len(endpoint_health) - healthy_endpoints,
        "fleet_health_average": avg_health,
        "total_deliveries": sum(e["delivery_volume"] for e in endpoint_health)
    }

    return {
        "monitoring_id": operation_id,
        "endpoint_health": endpoint_health,
        "monitoring_summary": monitoring_summary,
        "monitored_at": datetime.now().isoformat()
    }

@mcp.tool()
def get_webhook_logs() -> Dict[str, Any]:
    """Get webhook platform activity logs"""
    return {
        "total_operations": len(WEBHOOK_LOG),
        "recent_operations": WEBHOOK_LOG[-10:] if WEBHOOK_LOG else [],
        "log_status": "active"
    }

if __name__ == "__main__":
    mcp.run()
