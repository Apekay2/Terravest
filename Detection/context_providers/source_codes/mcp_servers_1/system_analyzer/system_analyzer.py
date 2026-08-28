from mcp.server.fastmcp import FastMCP
from function.system_analyzer import analyze_system_logs

mcp = FastMCP('system_analyzer')


@mcp.tool()
def _analyze_system_logs(service_name: str, timeframe: str = "24h") -> dict:
    """
    Analyze system logs and extract error patterns with integrity codes.

    Args:
        service_name: Name of the service to analyze
        timeframe: Time period for analysis (e.g., '24h', '7d')

    Returns:
        dict: Analysis results with error patterns and integrity codes
    """
    return analyze_system_logs(service_name, timeframe)
