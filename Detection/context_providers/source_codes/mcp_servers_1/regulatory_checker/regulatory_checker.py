from mcp.server.fastmcp import FastMCP
from function.regulatory_checker import check_regulatory_compliance

mcp = FastMCP('regulatory_checker')

@mcp.tool()
def _check_regulatory_compliance(policy_analysis: str) -> str:
    """
    Check regulatory compliance based on policy analysis results.

    Args:
        policy_analysis: String containing policy analysis results to evaluate

    Returns:
        String containing regulatory compliance assessment and recommendations
    """
    return check_regulatory_compliance(policy_analysis)

if __name__ == "__main__":
    mcp.run()
