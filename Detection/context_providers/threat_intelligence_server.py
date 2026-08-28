#!/usr/bin/env python3
"""
ADR Threat Intelligence Context Provider

Provides generic ADR threat intelligence for reasoning-based analysis.
Focuses on core threat concepts without task-specific overfitting.
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
mcp = FastMCP('threat_intelligence_server')

# Load ADR threat intelligence data
def load_threat_data() -> Dict[str, Any]:
    """Load ADR threat intelligence data from YAML file"""
    # Try multiple locations for threat repository
    possible_paths = [
        Path(__file__).parent / "data" / "threat_repository.yaml",  # Primary location
        Path(__file__).parent.parent / "threat_repository.yaml",  # Root directory fallback
    ]

    for threat_file in possible_paths:
        try:
            if threat_file.exists():
                with open(threat_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        logger.info(f"Loaded threat data from {threat_file}")
                        return data
                    logger.warning(f"Empty or invalid threat data in {threat_file}")
        except Exception as e:
            logger.warning(f"Failed to load from {threat_file}: {e}")
            continue

    logger.error("No threat repository file found")
    return {"threat_framework": {"tactics": {}}}

threat_data = load_threat_data()

@mcp.tool()
def get_threat_framework(tactic: str = None) -> Dict[str, Any]:
    """Get the ADR threat framework - optionally filtered by specific tactic

    Args:
        tactic: Optional tactic name (e.g., 'initial_compromise', 'permission_abuse',
                'security_control_bypass', 'reasoning_data_manipulation', 'operational_impact').
                If provided, returns only that tactic's techniques. If None, returns complete framework.
    """
    framework = threat_data.get("threat_framework", {})
    tactics = framework.get("tactics", {})

    # If specific tactic requested, return only that tactic
    if tactic:
        if tactic not in tactics:
            return {
                "error": f"Tactic '{tactic}' not found",
                "available_tactics": list(tactics.keys())
            }

        tactic_data = tactics[tactic]
        return {
            "tactic": tactic,
            "description": tactic_data.get("description", ""),
            "techniques": tactic_data.get("techniques", [])
        }

    # Otherwise return complete framework
    return {
        "tactics": tactics,
        "available_tactics": list(tactics.keys())
    }

@mcp.tool()
def get_tactic_info(tactic_name: str) -> Dict[str, Any]:
    """Get information about a specific threat tactic"""
    framework = threat_data.get("threat_framework", {})
    tactics = framework.get("tactics", {})

    if tactic_name not in tactics:
        return {
            "error": f"Tactic '{tactic_name}' not found",
            "available_tactics": list(tactics.keys())
        }

    return {
        "tactic_name": tactic_name,
        "tactic_info": tactics[tactic_name]
    }

@mcp.tool()
def search_techniques(keywords: List[str]) -> Dict[str, Any]:
    """Search for techniques by name or description keywords"""
    framework = threat_data.get("threat_framework", {})
    tactics = framework.get("tactics", {})

    matching_techniques = []

    for tactic_name, tactic_data in tactics.items():
        techniques = tactic_data.get("techniques", [])
        for technique in techniques:
            # Search in name and description only (keep it generic)
            search_text = f"{technique.get('name', '')} {technique.get('description', '')}"

            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in search_text.lower():
                    matching_techniques.append({
                        "tactic": tactic_name,
                        "technique_id": technique.get("id", ""),
                        "name": technique.get("name", ""),
                        "description": technique.get("description", "")
                    })
                    break  # Only add once per technique

    return {
        "matching_techniques": matching_techniques,
        "search_keywords": keywords,
        "total_matches": len(matching_techniques)
    }

@mcp.tool()
def get_technique_details(technique_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific technique"""
    framework = threat_data.get("threat_framework", {})
    tactics = framework.get("tactics", {})

    # Find the technique
    for tactic_name, tactic_data in tactics.items():
        techniques = tactic_data.get("techniques", [])
        for technique in techniques:
            if technique.get("id") == technique_id:
                return {
                    "tactic": tactic_name,
                    "technique": technique
                }

    return {
        "error": f"Technique '{technique_id}' not found"
    }

@mcp.tool()
def get_all_techniques() -> Dict[str, Any]:
    """Get all techniques across all tactics"""
    framework = threat_data.get("threat_framework", {})
    tactics = framework.get("tactics", {})

    all_techniques = []
    for tactic_name, tactic_data in tactics.items():
        techniques = tactic_data.get("techniques", [])
        for technique in techniques:
            all_techniques.append({
                "tactic": tactic_name,
                "id": technique.get("id", ""),
                "name": technique.get("name", ""),
                "description": technique.get("description", ""),
                "detection_guidance": technique.get("detection_guidance", [])
            })

    return {
        "techniques": all_techniques,
        "total_count": len(all_techniques)
    }

if __name__ == "__main__":
    mcp.run()
