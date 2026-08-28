from mcp.server.fastmcp import FastMCP
from function.arxiv_toolkit import is_arxiv_identifier
from function.arxiv_toolkit import search_identifier
from function.arxiv_toolkit import search_papers
import arxiv
from typing import Optional


mcp = FastMCP('arxiv_toolkit')
ARXIV_MAX_QUERY_LENGTH: int = 300
TOP_K_RESULTS: int = 3
LOAD_MAX_DOCS: int = 100
DOC_CONTENT_CHARS_MAX: Optional[int] = 4000


@mcp.tool()
def _is_arxiv_identifier(identifier: str) -> bool:
    """
    Check if the given identifier is a valid arXiv identifier.

    Args:
        identifier (str): The identifier to check.

    Returns:
        bool: True if the identifier is a valid arXiv identifier, False otherwise.
    """
    return is_arxiv_identifier(identifier=identifier)


@mcp.tool()
def _search_identifier(identifier: str) -> list[dict[str, str]]:
    """
    Search for arXiv papers based on the given identifier.

    Args:
        identifier (str): The identifier to search for.
    """
    return search_identifier(identifier=identifier)


@mcp.tool()
def _search_papers(query: str) -> list[dict[str, str]]:
    """
    Search for arXiv papers based on keywords or topics.

    Args:
        query (str): The search query (keywords, topics, etc.)
    """
    return search_papers(query)


if __name__ == '__main__':
    mcp.run('stdio')
