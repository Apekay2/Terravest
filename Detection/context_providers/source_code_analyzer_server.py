#!/usr/bin/env python3
"""
ADR Source Code Context Provider

Provides MCP server source code for reasoning-based threat analysis.
No pre-analysis or cheating metadata - just clean source code and basic info.
"""
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
mcp = FastMCP('source_code_analyzer_server')

# Load source code registry
def load_source_registry() -> Dict[str, Any]:
    """Load source code registry from YAML file"""
    registry_file = Path(__file__).parent / "data" / "source_codes_registry.yaml"

    try:
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                data = yaml.safe_load(f)
                logger.info(f"Loaded source registry from {registry_file}")
                return data
        else:
            logger.warning(f"Registry file not found: {registry_file}")
            return {"mcp_servers": []}
    except Exception as e:
        logger.error(f"Failed to load source registry: {e}")
        return {"mcp_servers": []}

source_registry = load_source_registry()

@mcp.tool()
def get_source_code(server_names: List[str]) -> Dict[str, Any]:
    """Get the source code of MCP servers for analysis"""
    source_codes = []

    for server_name in server_names:
        # Find server in registry
        server_info = None
        for server in source_registry.get("mcp_servers", []):
            if server.get("name") == server_name or server.get("name") == server_name.replace('-', '_'):
                server_info = server
                break

        if not server_info:
            source_codes.append({
                "server_name": server_name,
                "status": "not_found"
            })
            continue

        # Read source code
        server_path = server_info.get("path", "")
        full_path = Path(__file__).parent / server_path

        try:
            if full_path.exists():
                with open(full_path, 'r') as f:
                    source_code = f.read()

                # Provide clean metadata without cheating indicators
                source_codes.append({
                    "server_name": server_name,
                    "status": "found",
                    "metadata": {
                        "category": server_info.get("category"),
                        "description": server_info.get("description"),
                        "capabilities": server_info.get("capabilities", [])
                    },
                    "source_code": source_code
                })
            else:
                source_codes.append({
                    "server_name": server_name,
                    "status": "file_not_found"
                })

        except Exception as e:
            source_codes.append({
                "server_name": server_name,
                "status": "error",
                "error": str(e)
            })

    return {
        "source_codes": source_codes,
        "total_retrieved": len([s for s in source_codes if s.get("status") == "found"])
    }

@mcp.tool()
def list_mcp_servers(category: str = None) -> Dict[str, Any]:
    """List available MCP servers with basic metadata"""
    servers = source_registry.get("mcp_servers", [])
    filtered_servers = []

    for server in servers:
        if category and server.get("category", "").lower() != category.lower():
            continue

        # Provide clean metadata without cheating indicators
        filtered_servers.append({
            "name": server.get("name"),
            "category": server.get("category"),
            "description": server.get("description"),
            "capabilities": server.get("capabilities", [])
        })

    return {
        "servers": filtered_servers,
        "total_count": len(filtered_servers)
    }

@mcp.tool()
def get_server_categories() -> Dict[str, Any]:
    """Get available server categories for analysis"""
    servers = source_registry.get("mcp_servers", [])
    categories = sorted(list(set(s.get("category", "") for s in servers if s.get("category"))))

    return {
        "categories": categories,
        "total_categories": len(categories),
        "total_servers": len(servers)
    }

@mcp.tool()
def analyze_tool_capabilities(server_names: List[str]) -> Dict[str, Any]:
    """Analyze if tool capabilities match their stated business purpose"""
    analyses = []

    for server_name in server_names:
        # Find server in registry
        server_info = None
        for server in source_registry.get("mcp_servers", []):
            if server.get("name") == server_name or server.get("name") == server_name.replace('-', '_'):
                server_info = server
                break

        if not server_info:
            analyses.append({
                "server_name": server_name,
                "status": "not_found"
            })
            continue

        # Provide structured capability data for analysis
        capability_analysis = {
            "server_name": server_name,
            "category": server_info.get("category", ""),
            "description": server_info.get("description", ""),
            "capabilities": server_info.get("capabilities", []),
            "analysis_guidance": "Compare capabilities against description and category to identify scope violations or hidden functionality"
        }

        analyses.append(capability_analysis)

    return {
        "capability_analyses": analyses,
        "servers_analyzed": len(server_names)
    }

@mcp.tool()
def analyze_vulnerabilities(server_names: List[str]) -> Dict[str, Any]:
    """Analyze MCP servers for potential security vulnerabilities"""
    vulnerability_analyses = []

    for server_name in server_names:
        # Find server in registry
        server_info = None
        for server in source_registry.get("mcp_servers", []):
            if server.get("name") == server_name or server.get("name") == server_name.replace('-', '_'):
                server_info = server
                break

        if not server_info:
            vulnerability_analyses.append({
                "server_name": server_name,
                "status": "not_found"
            })
            continue

        # Provide vulnerability analysis framework
        vulnerability_analysis = {
            "server_name": server_name,
            "category": server_info.get("category", ""),
            "capabilities": server_info.get("capabilities", []),
            "analysis_guidance": "Review server capabilities and source code for potential security vulnerabilities, privilege escalation, or data exposure risks"
        }

        vulnerability_analyses.append(vulnerability_analysis)

    return {
        "vulnerability_analyses": vulnerability_analyses,
        "servers_analyzed": len(server_names)
    }

@mcp.tool()
def search_code_patterns(pattern_description: str, server_categories: List[str] = None) -> Dict[str, Any]:
    """Search for specific code patterns across MCP servers"""
    servers = source_registry.get("mcp_servers", [])

    if server_categories:
        filtered_servers = [s for s in servers if s.get("category") in server_categories]
    else:
        filtered_servers = servers

    return {
        "search_pattern": pattern_description,
        "server_categories": server_categories or "all",
        "available_servers": filtered_servers,
        "analysis_guidance": f"Search for the pattern '{pattern_description}' in the source code of the listed servers"
    }

if __name__ == "__main__":
    mcp.run()
