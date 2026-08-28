from mcp.server.fastmcp import FastMCP
from function.access_auditor import audit_user_permissions

mcp = FastMCP('access_auditor')

@mcp.tool()
def _audit_user_permissions(audit_scope: str, user_filter: str = "all_users") -> dict:
    """
    Audit user permissions and access rights across enterprise systems.

    Args:
        audit_scope: Scope of audit (department, system, organization)
        user_filter: Filter for specific user groups or all users

    Returns:
        Dictionary containing user access audit results and permission analysis
    """
    return audit_user_permissions(audit_scope, user_filter)

if __name__ == "__main__":
    mcp.run()
