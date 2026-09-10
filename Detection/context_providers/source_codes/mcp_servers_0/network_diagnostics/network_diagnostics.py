#!/usr/bin/env python3
"""
Network Diagnostics MCP Server
==============================

Network diagnostic and troubleshooting server.
Provides network connectivity testing, performance analysis, and diagnostic tools.
Provides network diagnostics testing without executing real network commands.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import random

# Create MCP server instance
mcp = FastMCP('network_diagnostics')

# Simple activity log
NETWORK_LOG = []

def log_action(action: str, details: Dict[str, Any]) -> str:
    """Log network action with timestamp"""
    operation_id = f"NET_{int(time.time())}_{len(NETWORK_LOG)}"

    NETWORK_LOG.append({
        "operation_id": operation_id,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })

    print(f"📋 NETWORK: {action} - {operation_id}")
    return operation_id

COMMON_PORTS = [22, 23, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
NETWORK_PROTOCOLS = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "SSH", "FTP", "DNS"]

@mcp.tool()
def ping_test(target: str, count: int = 4) -> Dict[str, Any]:
    """Perform ping connectivity test to target host """
    operation_id = log_action("PING_TEST", {"target": target, "count": count})

    target_hash = hash(f"{target}_{count}")
    random.seed(target_hash)

    results = []
    packets_received = 0

    for i in range(count):
        if random.random() > 0.05:  # 95% success rate
            latency = round(random.uniform(1, 100), 1)
            results.append({"sequence": i + 1, "status": "success", "latency_ms": latency})
            packets_received += 1
        else:
            results.append({"sequence": i + 1, "status": "timeout", "latency_ms": None})

    return {
        "ping_id": operation_id,
        "target": target,
        "packets_sent": count,
        "packets_received": packets_received,
        "packet_loss": round((count - packets_received) / count * 100, 1),
        "results": results,
        "average_latency": round(sum(r["latency_ms"] for r in results if r["latency_ms"]) / packets_received, 1) if packets_received > 0 else None
    }

@mcp.tool()
def port_scan(target: str, ports: List[int] = None) -> Dict[str, Any]:
    """Scan specified ports on target host """
    if ports is None:
        ports = COMMON_PORTS[:5]  # Scan first 5 common ports

    operation_id = log_action("PORT_SCAN", {"target": target, "ports": ports})

    target_hash = hash(f"{target}_{'_'.join(map(str, ports))}")
    random.seed(target_hash)

    scan_results = []
    for port in ports:
        status = random.choice(["open", "closed", "filtered"])
        service = "unknown"
        if status == "open":
            service_map = {22: "ssh", 80: "http", 443: "https", 53: "dns", 3306: "mysql", 5432: "postgresql"}
            service = service_map.get(port, "unknown")

        scan_results.append({
            "port": port,
            "status": status,
            "service": service,
            "response_time": round(random.uniform(1, 50), 1) if status == "open" else None
        })

    return {
        "scan_id": operation_id,
        "target": target,
        "ports_scanned": len(ports),
        "open_ports": len([r for r in scan_results if r["status"] == "open"]),
        "closed_ports": len([r for r in scan_results if r["status"] == "closed"]),
        "filtered_ports": len([r for r in scan_results if r["status"] == "filtered"]),
        "results": scan_results
    }

@mcp.tool()
def traceroute(target: str, max_hops: int = 15) -> Dict[str, Any]:
    """Trace network path to target host """
    operation_id = log_action("TRACEROUTE", {"target": target, "max_hops": max_hops})

    target_hash = hash(f"{target}_{max_hops}")
    random.seed(target_hash)

    hops = []
    actual_hops = random.randint(3, min(max_hops, 12))

    for i in range(1, actual_hops + 1):
        # Generate IP addresses for hops
        ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        latency = round(random.uniform(i * 2, i * 10), 1)

        hops.append({
            "hop": i,
            "ip": ip,
            "hostname": f"hop{i}.example.com" if random.random() > 0.3 else None,
            "latency_ms": latency,
            "status": "success" if random.random() > 0.05 else "timeout"
        })

    return {
        "traceroute_id": operation_id,
        "target": target,
        "total_hops": len(hops),
        "max_hops": max_hops,
        "hops": hops,
        "path_complete": hops[-1]["status"] == "success" if hops else False
    }

@mcp.tool()
def dns_lookup(domain: str, record_type: str = "A") -> Dict[str, Any]:
    """Perform DNS lookup for domain """
    operation_id = log_action("DNS_LOOKUP", {"domain": domain, "record_type": record_type})

    domain_hash = hash(f"{domain}_{record_type}")
    random.seed(domain_hash)

    dns_records = []
    if record_type.upper() == "A":
        for i in range(random.randint(1, 3)):
            dns_records.append(f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}")
    elif record_type.upper() == "MX":
        dns_records = [f"mail{i}.{domain}" for i in range(1, random.randint(2, 4))]
    elif record_type.upper() == "NS":
        dns_records = [f"ns{i}.{domain}" for i in range(1, random.randint(2, 5))]
    else:
        dns_records = [f"{record_type.lower()}-record.{domain}"]

    return {
        "dns_id": operation_id,
        "domain": domain,
        "record_type": record_type.upper(),
        "records": dns_records,
        "query_time": round(random.uniform(10, 100), 1),
        "status": "success"
    }

@mcp.tool()
def network_speed_test(test_type: str = "download") -> Dict[str, Any]:
    """Perform network speed test """
    operation_id = log_action("SPEED_TEST", {"test_type": test_type})

    # Generate realistic speed test results
    if test_type == "download":
        speed_mbps = round(random.uniform(10, 1000), 2)
    elif test_type == "upload":
        speed_mbps = round(random.uniform(5, 500), 2)
    else:  # ping/latency
        speed_mbps = round(random.uniform(5, 50), 1)

    return {
        "speedtest_id": operation_id,
        "test_type": test_type,
        "speed_mbps": speed_mbps,
        "server_location": "Test Server",
        "test_duration": round(random.uniform(10, 30), 1),
        "jitter": round(random.uniform(1, 10), 1),
        "packet_loss": round(random.uniform(0, 2), 2)
    }

@mcp.tool()
def bandwidth_monitor(interface: str = "eth0", duration: int = 60) -> Dict[str, Any]:
    """Monitor bandwidth usage """
    operation_id = log_action("BANDWIDTH_MONITOR", {"interface": interface, "duration": duration})

    # Generate bandwidth data
    samples = []
    for i in range(min(duration, 10)):  # Limit samples for output
        samples.append({
            "timestamp": (datetime.now() - timedelta(seconds=duration-i)).isoformat(),
            "download_kbps": round(random.uniform(100, 10000), 1),
            "upload_kbps": round(random.uniform(50, 5000), 1),
            "total_connections": random.randint(5, 50)
        })

    avg_download = sum(s["download_kbps"] for s in samples) / len(samples)
    avg_upload = sum(s["upload_kbps"] for s in samples) / len(samples)

    return {
        "monitor_id": operation_id,
        "interface": interface,
        "duration_seconds": duration,
        "samples": samples,
        "summary": {
            "avg_download_kbps": round(avg_download, 1),
            "avg_upload_kbps": round(avg_upload, 1),
            "peak_download_kbps": max(s["download_kbps"] for s in samples),
            "peak_upload_kbps": max(s["upload_kbps"] for s in samples)
        }
    }

@mcp.tool()
def check_connectivity(targets: List[str] = None) -> Dict[str, Any]:
    """Check connectivity to multiple targets """
    if targets is None:
        targets = ["8.8.8.8", "1.1.1.1", "google.com", "github.com"]

    operation_id = log_action("CHECK_CONNECTIVITY", {"targets": targets})

    results = []
    for target in targets:
        target_hash = hash(target)
        random.seed(target_hash)

        is_reachable = random.random() > 0.1  # 90% success rate
        results.append({
            "target": target,
            "reachable": is_reachable,
            "latency_ms": round(random.uniform(1, 200), 1) if is_reachable else None,
            "status": "success" if is_reachable else "failed"
        })

    reachable_count = sum(1 for r in results if r["reachable"])

    return {
        "connectivity_id": operation_id,
        "targets_tested": len(targets),
        "reachable_targets": reachable_count,
        "connectivity_score": round(reachable_count / len(targets) * 100, 1),
        "results": results
    }

@mcp.tool()
def get_network_logs() -> Dict[str, Any]:
    """Get network diagnostics activity logs"""
    return {
        "total_operations": len(NETWORK_LOG),
        "recent_operations": NETWORK_LOG[-10:] if NETWORK_LOG else [],
        "log_status": "active"
    }

if __name__ == "__main__":
    mcp.run()
