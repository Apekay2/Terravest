from mcp.server.fastmcp import FastMCP
from function.ai_insights import generate_business_insights

mcp = FastMCP('ai_insights')


@mcp.tool()
def _generate_business_insights(analysis_data: str) -> str:
    """
    Generate business insights from system analysis data.

    Args:
        analysis_data: System analysis data to generate insights from

    Returns:
        str: Business insights and recommendations
    """
    return generate_business_insights(analysis_data)
