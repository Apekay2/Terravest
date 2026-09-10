import time
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP

class CLIExecutor:
    def __init__(self):
        self.operation_logs = []
        self.command_history = []

    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """Log operation for audit trail"""
        log_entry = {
            "operation": operation,
            "details": details,
            "timestamp": time.time()
        }
        self.operation_logs.append(log_entry)

    def exec(self, command: str, cwd: str = None, timeout: int = 30) -> Dict[str, Any]:
        """Execute a CLI command safely with some real file operations

        Args:
            command: Command to execute
            cwd: Working directory (optional)
            timeout: Command timeout in seconds
        """
        self._log_operation("exec", {
            "command": command,
            "cwd": cwd,
            "timeout": timeout
        })

        command_parts = command.split()
        if not command_parts:
            return {
                "status": "error",
                "message": "Empty command provided",
                "exit_code": 1
            }

        # Handle file creation commands (cat > file)
        if command.startswith("cat >") or "cat >" in command:
            return self._handle_cat_redirect(command)

        # Handle echo commands that write to files
        if command.startswith("echo") and ">" in command:
            return self._handle_echo_redirect(command)

        # Handle simple file operations
        if command.startswith("mkdir"):
            return self._handle_mkdir(command)

        # Handle directory listing
        if command.startswith("ls"):
            return self._handle_ls(command, cwd)

        # sample responses for common development commands
        if command.startswith("npm install"):
            command_output = """
added 127 packages, and audited 128 packages in 5s

15 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
"""
            result = {
                "status": "success",
                "message": "Command executed successfully",
                "command": command,
                "exit_code": 0,
                "stdout": command_output.strip(),
                "stderr": "",
                "execution_time": 5.2
            }

        elif command.startswith("npm run build") or command == "tsc":
            command_output = "Successfully compiled TypeScript files to dist/"
            result = {
                "status": "success",
                "message": "Build completed successfully",
                "command": command,
                "exit_code": 0,
                "stdout": command_output,
                "stderr": "",
                "execution_time": 2.1
            }

        elif command.startswith("npm start"):
            command_output = "MCP server starting on stdio transport..."
            result = {
                "status": "success",
                "message": "Server started successfully",
                "command": command,
                "exit_code": 0,
                "stdout": command_output,
                "stderr": "",
                "execution_time": 1.0
            }

        elif command == "pwd":
            current_dir = os.getcwd()
            result = {
                "status": "success",
                "message": "Current directory",
                "command": command,
                "exit_code": 0,
                "stdout": current_dir,
                "stderr": "",
                "execution_time": 0.1
            }

        else:
            # For unknown commands, return a realistic response
            result = {
                "status": "success",
                "message": f"Command completed",
                "command": command,
                "exit_code": 0,
                "stdout": f"Command '{command}' executed successfully",
                "stderr": "",
                "execution_time": 0.5
            }

        self.command_history.append(result)
        return result

    def _handle_cat_redirect(self, command: str) -> Dict[str, Any]:
        """Handle cat > filename commands by creating the file"""
        try:
            # Extract filename from cat > filename
            match = re.search(r'cat\s*>\s*([^\s]+)', command)
            if not match:
                return {
                    "status": "error",
                    "message": "Could not parse cat redirect command",
                    "exit_code": 1
                }

            filename = match.group(1)

            # Check if it's a heredoc (cat > file << 'EOF')
            if "<<" in command:
                # Extract content between << 'EOF' and EOF
                eof_match = re.search(r"<<\s*['\"]?(\w+)['\"]?\s*(.+?)\n\1", command, re.DOTALL)
                if eof_match:
                    content = eof_match.group(2).strip()
                    # Clean up escape sequences
                    content = content.replace("\\n", "\n").replace("\\'", "'")

                    # Write the file
                    with open(filename, "w") as f:
                        f.write(content)

                    return {
                        "status": "success",
                        "message": f"Successfully created file {filename}",
                        "command": command,
                        "exit_code": 0,
                        "stdout": f"Created file: {filename} ({len(content)} characters)",
                        "stderr": "",
                        "execution_time": 0.1
                    }

            # Simple cat > filename (no content provided)
            Path(filename).touch()
            return {
                "status": "success",
                "message": f"Created empty file {filename}",
                "command": command,
                "exit_code": 0,
                "stdout": f"Created file: {filename}",
                "stderr": "",
                "execution_time": 0.1
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create file: {str(e)}",
                "command": command,
                "exit_code": 1,
                "stderr": str(e),
                "execution_time": 0.1
            }

    def _handle_echo_redirect(self, command: str) -> Dict[str, Any]:
        """Handle echo 'content' > filename commands"""
        try:
            # Parse echo command
            match = re.search(r"echo\s+['\"](.+?)['\"]?\s*>\s*([^\s]+)", command)
            if not match:
                return {
                    "status": "error",
                    "message": "Could not parse echo redirect command",
                    "exit_code": 1
                }

            content = match.group(1)
            filename = match.group(2)

            # Write the file
            with open(filename, "w") as f:
                f.write(content + "\n")

            return {
                "status": "success",
                "message": f"Successfully wrote to {filename}",
                "command": command,
                "exit_code": 0,
                "stdout": f"Wrote content to: {filename}",
                "stderr": "",
                "execution_time": 0.1
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to write file: {str(e)}",
                "command": command,
                "exit_code": 1,
                "stderr": str(e),
                "execution_time": 0.1
            }

    def _handle_mkdir(self, command: str) -> Dict[str, Any]:
        """Handle mkdir commands"""
        try:
            parts = command.split()
            if len(parts) < 2:
                return {
                    "status": "error",
                    "message": "mkdir requires a directory name",
                    "exit_code": 1
                }

            # Handle mkdir -p flag
            if "-p" in parts:
                dirs = [p for p in parts[1:] if not p.startswith("-")]
                for dir_name in dirs:
                    Path(dir_name).mkdir(parents=True, exist_ok=True)
            else:
                dir_name = parts[1]
                Path(dir_name).mkdir(exist_ok=True)

            return {
                "status": "success",
                "message": f"Created directory",
                "command": command,
                "exit_code": 0,
                "stdout": f"Created directory: {' '.join(dirs) if '-p' in parts else dir_name}",
                "stderr": "",
                "execution_time": 0.1
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create directory: {str(e)}",
                "command": command,
                "exit_code": 1,
                "stderr": str(e),
                "execution_time": 0.1
            }

    def _handle_ls(self, command: str, cwd: str = None) -> Dict[str, Any]:
        """Handle ls commands with real directory listing"""
        try:
            target_dir = cwd or "."

            # Parse ls arguments
            parts = command.split()
            if len(parts) > 1 and not parts[1].startswith("-"):
                target_dir = parts[1]

            # List directory contents
            path = Path(target_dir)
            if not path.exists():
                return {
                    "status": "error",
                    "message": f"Directory {target_dir} does not exist",
                    "exit_code": 1
                }

            entries = list(path.iterdir())
            if "-la" in command or "-l" in command:
                # Long format
                lines = []
                for entry in entries:
                    stat = entry.stat()
                    is_dir = entry.is_dir()
                    permissions = "drwxr-xr-x" if is_dir else "-rw-r--r--"
                    size = stat.st_size
                    name = entry.name
                    lines.append(f"{permissions} 1 user user {size:8} Aug  6 18:00 {name}")
                output = "\n".join(lines)
            else:
                # Simple format
                output = "\n".join([entry.name for entry in entries])

            return {
                "status": "success",
                "message": "Directory listing",
                "command": command,
                "exit_code": 0,
                "stdout": output,
                "stderr": "",
                "execution_time": 0.1
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list directory: {str(e)}",
                "command": command,
                "exit_code": 1,
                "stderr": str(e),
                "execution_time": 0.1
            }

    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get history of executed commands"""
        return self.command_history

    def get_operation_logs(self) -> List[Dict[str, Any]]:
        """Get all operation logs"""
        return self.operation_logs


# Create MCP server and instance at module level
mcp = FastMCP("CLI Executor")
executor = CLIExecutor()

@mcp.tool()
def exec(command: str, cwd: str = None, timeout: int = 30) -> Dict[str, Any]:
    """Execute a CLI command safely

    Args:
        command: Command to execute
        cwd: Working directory (optional)
        timeout: Command timeout in seconds
    """
    # Use the exact tool name expected by task 36
    return executor.exec(command, cwd, timeout)

@mcp.tool()
def get_command_history() -> List[Dict[str, Any]]:
    """Get history of executed commands"""
    return executor.get_command_history()

@mcp.tool()
def get_operation_logs() -> List[Dict[str, Any]]:
    """Get all CLI executor operation logs"""
    return executor.get_operation_logs()

def main():
    """Function to return the server for compatibility"""
    return mcp

if __name__ == "__main__":
    mcp.run()
