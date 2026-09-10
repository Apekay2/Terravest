from mcp.server.fastmcp import FastMCP
from function.permission_reporter import generate_access_report

mcp = FastMCP('permission_reporter')

@mcp.tool()
def _generate_access_report(audit_data: dict) -> str:
    """
    Generate comprehensive access and permission reports from audit data.

    Args:
        audit_data: Dictionary containing audit results to process

    Returns:
        String containing formatted access report with findings and recommendations
    """
    return generate_access_report(audit_data)

if __name__ == "__main__":
    mcp.run()
