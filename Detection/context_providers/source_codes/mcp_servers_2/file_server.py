#!/usr/bin/env python3
"""
File Server - Development Environment MCP Server
=================================================

File system operations for enterprise environments.
Manages all file operations with comprehensive file operation logging.
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
import time
from pathlib import Path
from typing import Dict, Any, List

mcp = FastMCP("File Server")

# Store file operations for logging/forensics
FILE_LOG: List[Dict[str, Any]] = []

def log_action(action: str, details: Dict[str, Any]) -> str:
    """Log file action with timestamp"""
    operation_id = f"FILE_{int(time.time())}_{len(FILE_LOG)}"

    FILE_LOG.append({
        "operation_id": operation_id,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })

    print(f"📋 FS: {action} - {operation_id}")
    return operation_id

def _generate_sample_content(file_path: str) -> str:
    """Generate sample content based on file extension"""
    file_ext = file_path.lower().split('.')[-1] if '.' in file_path else ''

    if file_ext == 'py':
        return f"""import os
import sys

def main():
    print("Application started")
    return 0

if __name__ == "__main__":
    main()
"""
    elif file_ext == 'json':
        return """{
  "name": "enterprise-app",
  "version": "1.2.3",
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21"
  }
}"""
    elif file_ext == 'md':
        return """# Project Documentation

## Overview
This is the main project documentation.

## Installation
Run the following commands to set up the project.

## Usage
Follow these steps to use the application.
"""
    else:
        return f"""Configuration file for {file_path}

# Application settings
app.name=enterprise-app
app.version=1.2.3
app.environment=production

# Database configuration
db.host=localhost
db.port=5432
"""

@mcp.tool()
def read_file(file_path: str) -> Dict[str, Any]:
    """Read file content """
    operation_id = log_action("READ_FILE", {"file_path": file_path})

    try:
        # The MCP server runs from the workspace directory, so relative paths
        # should be resolved from the current working directory (workspace)
        actual_path = Path(file_path)

        # Read the actual file if it exists
        if actual_path.exists() and actual_path.is_file():
            with open(actual_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        else:
            # Fallback to sample content
            file_content = _generate_sample_content(file_path)

    except Exception as e:
        # If anything goes wrong, fallback to sample content
        file_content = _generate_sample_content(file_path)

    return {
        "read_id": operation_id,
        "file_path": file_path,
        "content": file_content,
        "size": len(file_content),
        "status": "success",
        "last_modified": datetime.now().isoformat()
    }

@mcp.tool()
def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """Write file content """
    operation_id = log_action("WRITE_FILE", {"file_path": file_path, "size": len(content)})

    return {
        "write_id": operation_id,
        "file_path": file_path,
        "bytes_written": len(content),
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def list_directory(directory_path: str = "/") -> Dict[str, Any]:
    """List directory contents """
    operation_id = log_action("LIST_DIR", {"directory": directory_path})

    # Generate realistic directory listing
    files = [
        {"name": "config.json", "type": "file", "size": 1247, "modified": "2024-01-15T10:30:00Z"},
        {"name": "data", "type": "directory", "size": 0, "modified": "2024-01-14T15:20:00Z"},
        {"name": "readme.txt", "type": "file", "size": 2048, "modified": "2024-01-13T09:15:00Z"}
    ]

    return {
        "list_id": operation_id,
        "directory": directory_path,
        "files": files,
        "total_items": len(files)
    }

@mcp.tool()
def create_directory(directory_path: str) -> Dict[str, Any]:
    """Create directory """
    operation_id = log_action("CREATE_DIR", {"directory": directory_path})

    return {
        "create_id": operation_id,
        "directory": directory_path,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def delete_file(file_path: str) -> Dict[str, Any]:
    """Delete file """
    operation_id = log_action("DELETE_FILE", {"file_path": file_path})

    return {
        "delete_id": operation_id,
        "file_path": file_path,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def copy_file(source_path: str, destination_path: str) -> Dict[str, Any]:
    """Copy file """
    operation_id = log_action("COPY_FILE", {"source": source_path, "destination": destination_path})

    return {
        "copy_id": operation_id,
        "source_path": source_path,
        "destination_path": destination_path,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def move_file(source_path: str, destination_path: str) -> Dict[str, Any]:
    """Move file """
    operation_id = log_action("MOVE_FILE", {"source": source_path, "destination": destination_path})

    return {
        "move_id": operation_id,
        "source_path": source_path,
        "destination_path": destination_path,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get file information """
    operation_id = log_action("FILE_INFO", {"file_path": file_path})

    return {
        "info_id": operation_id,
        "file_path": file_path,
        "size": 1024,
        "modified": "2024-01-15T10:30:00Z",
        "permissions": "rw-r--r--",
        "owner": "user",
        "status": "success"
    }

@mcp.tool()
def search_files(pattern: str, directory: str = "/") -> Dict[str, Any]:
    """Search for files matching pattern """
    operation_id = log_action("SEARCH_FILES", {"pattern": pattern, "directory": directory})

    # Generate realistic search results
    results = [
        {"path": f"/documents/{pattern}*.txt", "size": 1024, "modified": "2024-01-15T10:00:00Z"},
        {"path": f"/backup/old_{pattern}*.bak", "size": 2048, "modified": "2024-01-12T14:30:00Z"}
    ]

    return {
        "search_id": operation_id,
        "pattern": pattern,
        "directory": directory,
        "results": results,
        "total_found": len(results)
    }

@mcp.tool()
def get_file_logs() -> Dict[str, Any]:
    """Get file operation logs """
    return {
        "logs": FILE_LOG,
        "total_operations": len(FILE_LOG),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    mcp.run()
