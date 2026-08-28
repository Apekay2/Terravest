from mcp.server.fastmcp import FastMCP
from function.policy_analyzer import analyze_policy_document

mcp = FastMCP('policy_analyzer')

@mcp.tool()
def _analyze_policy_document(document_type: str, focus_area: str = "data_protection") -> str:
    """
    Analyze policy documents to extract key provisions and compliance requirements.

    Args:
        document_type: Type of policy to analyze (privacy, security, compliance)
        focus_area: Specific area to focus analysis on

    Returns:
        String containing policy analysis with key findings and recommendations
    """
    return analyze_policy_document(document_type, focus_area)

if __name__ == "__main__":
    mcp.run()
