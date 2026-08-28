#!/usr/bin/env python3
"""
DNS Resolver MCP Server
=======================

DNS resolution and analysis server.
Provides domain resolution, reverse lookups, and DNS record analysis.
Uses real DNS resolution with socket library and basic DNS queries.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime
import socket
import time

# Create MCP server instance
mcp = FastMCP('dns_resolver')

@mcp.tool()
def resolve_domain(domain: str, record_type: str = "A") -> Dict[str, Any]:
    """Resolve DNS record for domain - REAL DNS RESOLUTION"""

    try:
        if record_type.upper() == "A":
            # Get IPv4 address
            ip_address = socket.gethostbyname(domain)
            return {
                "domain": domain,
                "record_type": "A",
                "resolved_ip": ip_address,
                "success": True,
                "resolved_at": datetime.now().isoformat()
            }

        elif record_type.upper() == "AAAA":
            # Get IPv6 address (if available)
            try:
                result = socket.getaddrinfo(domain, None, socket.AF_INET6)
                ipv6_address = result[0][4][0] if result else None
                return {
                    "domain": domain,
                    "record_type": "AAAA",
                    "resolved_ip": ipv6_address,
                    "success": bool(ipv6_address),
                    "resolved_at": datetime.now().isoformat()
                }
            except socket.gaierror:
                return {
                    "domain": domain,
                    "record_type": "AAAA",
                    "success": False,
                    "error": "No IPv6 address found",
                    "resolved_at": datetime.now().isoformat()
                }

        else:
            # For other record types, we'd need dnspython library
            # For now, return basic info
            return {
                "domain": domain,
                "record_type": record_type,
                "success": False,
                "error": f"Record type {record_type} requires dnspython library",
                "resolved_at": datetime.now().isoformat()
            }

    except socket.gaierror as e:
        return {
            "domain": domain,
            "record_type": record_type,
            "success": False,
            "error": str(e),
            "resolved_at": datetime.now().isoformat()
        }

@mcp.tool()
def reverse_dns_lookup(ip_address: str) -> Dict[str, Any]:
    """Perform reverse DNS lookup - REAL REVERSE LOOKUP"""

    try:
        hostname = socket.gethostbyaddr(ip_address)
        return {
            "ip_address": ip_address,
            "hostname": hostname[0],
            "aliases": hostname[1],
            "success": True,
            "resolved_at": datetime.now().isoformat()
        }

    except socket.herror as e:
        return {
            "ip_address": ip_address,
            "success": False,
            "error": str(e),
            "resolved_at": datetime.now().isoformat()
        }

@mcp.tool()
def analyze_domain_records(domain: str) -> Dict[str, Any]:
    """Analyze multiple DNS records for a domain - REAL ANALYSIS"""

    records = {}

    # Try A record
    try:
        ipv4 = socket.gethostbyname(domain)
        records["A"] = {"ip": ipv4, "success": True}
    except socket.gaierror:
        records["A"] = {"success": False, "error": "No A record found"}

    # Try IPv6
    try:
        result = socket.getaddrinfo(domain, None, socket.AF_INET6)
        ipv6 = result[0][4][0] if result else None
        records["AAAA"] = {"ip": ipv6, "success": bool(ipv6)}
    except socket.gaierror:
        records["AAAA"] = {"success": False, "error": "No AAAA record found"}

    # Try to get additional info (basic hostname validation)
    try:
        # Test if domain resolves both ways
        if records["A"]["success"]:
            reverse_check = socket.gethostbyaddr(records["A"]["ip"])
            records["reverse_dns"] = {
                "hostname": reverse_check[0],
                "matches_domain": domain.lower() in reverse_check[0].lower(),
                "success": True
            }
    except:
        records["reverse_dns"] = {"success": False}

    return {
        "domain": domain,
        "records": records,
        "analysis_completed": True,
        "analyzed_at": datetime.now().isoformat()
    }

@mcp.tool()
def check_domain_availability(domain: str) -> Dict[str, Any]:
    """Check if domain is available for registration - BASIC CHECK"""

    try:
        # Try to resolve the domain
        socket.gethostbyname(domain)
        # If it resolves, it's likely registered
        return {
            "domain": domain,
            "appears_registered": True,
            "has_dns_records": True,
            "checked_at": datetime.now().isoformat(),
            "note": "Domain resolves to IP address, likely registered"
        }

    except socket.gaierror:
        # If it doesn't resolve, might be available (or just no DNS)
        return {
            "domain": domain,
            "appears_registered": False,
            "has_dns_records": False,
            "checked_at": datetime.now().isoformat(),
            "note": "Domain does not resolve - may be available or have no DNS records"
        }

@mcp.tool()
def trace_dns_path(domain: str) -> Dict[str, Any]:
    """Trace DNS resolution path - BASIC PATH INFO"""

    resolution_steps = []

    try:
        # Step 1: Basic resolution
        start_time = time.time()
        ip_address = socket.gethostbyname(domain)
        resolution_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        resolution_steps.append({
            "step": 1,
            "action": "A record lookup",
            "result": ip_address,
            "time_ms": round(resolution_time, 2)
        })

        # Step 2: Reverse lookup
        try:
            start_time = time.time()
            reverse_result = socket.gethostbyaddr(ip_address)
            reverse_time = (time.time() - start_time) * 1000

            resolution_steps.append({
                "step": 2,
                "action": "Reverse DNS lookup",
                "result": reverse_result[0],
                "time_ms": round(reverse_time, 2)
            })
        except:
            resolution_steps.append({
                "step": 2,
                "action": "Reverse DNS lookup",
                "result": "Failed",
                "time_ms": 0
            })

        return {
            "domain": domain,
            "final_ip": ip_address,
            "resolution_steps": resolution_steps,
            "total_steps": len(resolution_steps),
            "success": True,
            "traced_at": datetime.now().isoformat()
        }

    except socket.gaierror as e:
        return {
            "domain": domain,
            "success": False,
            "error": str(e),
            "traced_at": datetime.now().isoformat()
        }

@mcp.tool()
def validate_dns_configuration(domain: str) -> Dict[str, Any]:
    """Validate DNS configuration - BASIC VALIDATION"""

    validation_results = []
    overall_score = 0
    max_score = 4

    # Test 1: A record exists
    try:
        ipv4 = socket.gethostbyname(domain)
        validation_results.append({
            "test": "A Record",
            "status": "PASS",
            "details": f"Resolves to {ipv4}"
        })
        overall_score += 1
    except:
        validation_results.append({
            "test": "A Record",
            "status": "FAIL",
            "details": "No A record found"
        })

    # Test 2: Reverse DNS
    try:
        ipv4 = socket.gethostbyname(domain)
        reverse = socket.gethostbyaddr(ipv4)
        validation_results.append({
            "test": "Reverse DNS",
            "status": "PASS",
            "details": f"PTR record: {reverse[0]}"
        })
        overall_score += 1
    except:
        validation_results.append({
            "test": "Reverse DNS",
            "status": "FAIL",
            "details": "No PTR record or reverse lookup failed"
        })

    # Test 3: IPv6 support
    try:
        result = socket.getaddrinfo(domain, None, socket.AF_INET6)
        if result:
            validation_results.append({
                "test": "IPv6 Support",
                "status": "PASS",
                "details": f"AAAA record found: {result[0][4][0]}"
            })
            overall_score += 1
        else:
            raise Exception("No IPv6")
    except:
        validation_results.append({
            "test": "IPv6 Support",
            "status": "WARN",
            "details": "No AAAA record found"
        })

    # Test 4: Response time
    try:
        start_time = time.time()
        socket.gethostbyname(domain)
        response_time = (time.time() - start_time) * 1000

        if response_time < 100:
            status = "PASS"
            overall_score += 1
        elif response_time < 500:
            status = "WARN"
            overall_score += 0.5
        else:
            status = "FAIL"

        validation_results.append({
            "test": "Response Time",
            "status": status,
            "details": f"{response_time:.2f}ms"
        })
    except:
        validation_results.append({
            "test": "Response Time",
            "status": "FAIL",
            "details": "Unable to measure response time"
        })

    return {
        "domain": domain,
        "validation_results": validation_results,
        "overall_score": f"{overall_score}/{max_score}",
        "grade": "A" if overall_score >= 3.5 else "B" if overall_score >= 2.5 else "C" if overall_score >= 1.5 else "F",
        "validated_at": datetime.now().isoformat()
    }

@mcp.tool()
def bulk_dns_lookup(domains: List[str]) -> Dict[str, Any]:
    """Perform DNS lookup for multiple domains - REAL BULK LOOKUP"""

    results = []
    successful_lookups = 0

    for domain in domains[:20]:  # Limit to 20 domains to prevent abuse
        try:
            ip_address = socket.gethostbyname(domain)
            results.append({
                "domain": domain,
                "ip_address": ip_address,
                "success": True
            })
            successful_lookups += 1

        except socket.gaierror as e:
            results.append({
                "domain": domain,
                "success": False,
                "error": str(e)
            })

        # Small delay to be respectful
        time.sleep(0.1)

    return {
        "total_domains": len(domains),
        "processed_domains": len(results),
        "successful_lookups": successful_lookups,
        "success_rate": f"{(successful_lookups/len(results)*100):.1f}%" if results else "0%",
        "results": results,
        "processed_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    mcp.run()
