import time
from typing import Any, Dict, List, Optional
from datetime import datetime

class WordPress:
    def __init__(self):
        self.posts = []
        self.pages = []
        self.users = []
        self.comments = []
        self.operation_logs = []
        # Default site info - can be customized per request
        self.base_site_info = {
            "name": "WordPress Demo Site",
            "description": "WordPress demonstration platform",
            "version": "6.4.2",
            "timezone": "UTC"
        }

        # Initialize with default content
        self._initialize_default_content()

    def _initialize_default_content(self):
        """Initialize with default content"""
        # Initial posts
        self.posts = [
            {
                "id": 1,
                "title": "Getting Started with Our Platform",
                "content": "Welcome to our content management system. This platform provides powerful tools for managing your digital content and engaging with your audience effectively.",
                "status": "published",
                "author": 1,
                "date": "2024-01-01T10:00:00",
                "slug": "getting-started",
                "categories": [1]
            },
            {
                "id": 2,
                "title": "Best Practices for Content Creation",
                "content": "Creating engaging content requires understanding your audience and delivering value through every post. Here are proven strategies for building compelling content.",
                "status": "published",
                "author": 1,
                "date": "2024-01-15T14:30:00",
                "slug": "content-best-practices",
                "categories": [1, 2]
            }
        ]

        # Initial pages
        self.pages = [
            {
                "id": 10,
                "title": "About Us",
                "content": "We are dedicated to providing innovative solutions that help organizations achieve their digital transformation goals. Our platform combines ease of use with powerful capabilities.",
                "status": "published",
                "author": 1,
                "date": "2024-01-01T10:00:00",
                "slug": "about-us"
            }
        ]

        # System users
        self.users = [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@company-platform.com",
                "display_name": "Administrator",
                "roles": ["administrator"]
            }
        ]

    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """Log operation for audit trail"""
        log_entry = {
            "operation": operation,
            "details": details,
            "timestamp": time.time()
        }
        self.operation_logs.append(log_entry)

    def get_site_info(self, site_url: str = None) -> Dict[str, Any]:
        """Get WordPress site information"""
        self._log_operation("get_site_info", {"site_url": site_url})

        # Generate site info based on requested URL or use default
        if site_url:
            # Extract domain for site name
            import re
            domain_match = re.search(r'https?://([^/]+)', site_url)
            domain = domain_match.group(1) if domain_match else "demo-site"

            # Create contextual site info
            site_info = self.base_site_info.copy()
            site_info["url"] = site_url

            if "demo" in domain or "api" in domain:
                site_info["name"] = "WordPress API Demo Site"
                site_info["description"] = "A WordPress demo site for API testing"
            elif "company" in domain:
                site_info["name"] = "Corporate WordPress Site"
                site_info["description"] = "Enterprise content management platform"
            else:
                site_info["name"] = f"WordPress Site - {domain}"
                site_info["description"] = "WordPress content management system"
        else:
            # Use default site info
            site_info = self.base_site_info.copy()
            site_info["url"] = "https://demo.wp-api.org"
            site_info["name"] = "WordPress API Demo Site"
            site_info["description"] = "A WordPress demo site for API testing"

        return {
            "status": "success",
            "message": "Successfully retrieved site information",
            "site_info": site_info
        }

    def list_posts(self, per_page: int = 10, page: int = 1, status: str = "published") -> Dict[str, Any]:
        """List WordPress posts"""
        self._log_operation("list_posts", {
            "per_page": per_page,
            "page": page,
            "status": status
        })

        # Filter posts by status
        filtered_posts = [p for p in self.posts if p["status"] == status]

        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_posts = filtered_posts[start_idx:end_idx]

        return {
            "status": "success",
            "message": f"Successfully retrieved {len(paginated_posts)} posts",
            "posts": paginated_posts,
            "total_posts": len(filtered_posts),
            "page": page,
            "per_page": per_page
        }

    def get_post(self, post_id: int) -> Dict[str, Any]:
        """Get a specific WordPress post"""
        self._log_operation("get_post", {"post_id": post_id})

        post = next((p for p in self.posts if p["id"] == post_id), None)

        if not post:
            return {
                "status": "error",
                "message": f"Post with ID {post_id} not found"
            }

        return {
            "status": "success",
            "message": f"Successfully retrieved post {post_id}",
            "post": post
        }

    def create_post(self, title: str, content: str, status: str = "draft", author: int = 1) -> Dict[str, Any]:
        """Create a new WordPress post"""
        new_id = max([p["id"] for p in self.posts], default=0) + 1

        new_post = {
            "id": new_id,
            "title": title,
            "content": content,
            "status": status,
            "author": author,
            "date": datetime.now().isoformat(),
            "slug": title.lower().replace(" ", "-").replace("'", ""),
            "categories": [1]
        }

        self.posts.append(new_post)

        self._log_operation("create_post", {
            "post_id": new_id,
            "title": title,
            "status": status
        })

        return {
            "status": "success",
            "message": f"Successfully created post with ID {new_id}",
            "post": new_post
        }

    def update_post(self, post_id: int, title: Optional[str] = None, content: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing WordPress post"""
        post = next((p for p in self.posts if p["id"] == post_id), None)

        if not post:
            return {
                "status": "error",
                "message": f"Post with ID {post_id} not found"
            }

        # Update fields if provided
        if title is not None:
            post["title"] = title
        if content is not None:
            post["content"] = content
        if status is not None:
            post["status"] = status

        self._log_operation("update_post", {
            "post_id": post_id,
            "updated_fields": {
                "title": title,
                "content": bool(content),
                "status": status
            }
        })

        return {
            "status": "success",
            "message": f"Successfully updated post {post_id}",
            "post": post
        }

    def delete_post(self, post_id: int) -> Dict[str, Any]:
        """Delete a WordPress post"""
        post_index = next((i for i, p in enumerate(self.posts) if p["id"] == post_id), None)

        if post_index is None:
            return {
                "status": "error",
                "message": f"Post with ID {post_id} not found"
            }

        deleted_post = self.posts.pop(post_index)

        self._log_operation("delete_post", {"post_id": post_id})

        return {
            "status": "success",
            "message": f"Successfully deleted post {post_id}",
            "deleted_post": deleted_post
        }

    def list_pages(self) -> Dict[str, Any]:
        """List WordPress pages"""
        self._log_operation("list_pages", {})

        return {
            "status": "success",
            "message": f"Successfully retrieved {len(self.pages)} pages",
            "pages": self.pages
        }

    def list_users(self) -> Dict[str, Any]:
        """List WordPress users"""
        self._log_operation("list_users", {})

        return {
            "status": "success",
            "message": f"Successfully retrieved {len(self.users)} users",
            "users": self.users
        }

    def create_comment(self, post_id: int, content: str, author_name: str, author_email: str) -> Dict[str, Any]:
        """Create a comment on a post"""
        # Check if post exists
        post = next((p for p in self.posts if p["id"] == post_id), None)
        if not post:
            return {
                "status": "error",
                "message": f"Post with ID {post_id} not found"
            }

        new_comment_id = len(self.comments) + 1
        new_comment = {
            "id": new_comment_id,
            "post_id": post_id,
            "content": content,
            "author_name": author_name,
            "author_email": author_email,
            "date": datetime.now().isoformat(),
            "status": "approved"
        }

        self.comments.append(new_comment)

        self._log_operation("create_comment", {
            "comment_id": new_comment_id,
            "post_id": post_id,
            "author": author_name
        })

        return {
            "status": "success",
            "message": f"Successfully created comment {new_comment_id}",
            "comment": new_comment
        }

    def search_content(self, search_term: str) -> Dict[str, Any]:
        """Search WordPress content"""
        self._log_operation("search_content", {"search_term": search_term})

        # Search in posts and pages
        matching_posts = [
            p for p in self.posts
            if search_term.lower() in p["title"].lower() or search_term.lower() in p["content"].lower()
        ]

        matching_pages = [
            p for p in self.pages
            if search_term.lower() in p["title"].lower() or search_term.lower() in p["content"].lower()
        ]

        return {
            "status": "success",
            "message": f"Found {len(matching_posts)} posts and {len(matching_pages)} pages",
            "search_term": search_term,
            "posts": matching_posts,
            "pages": matching_pages,
            "total_results": len(matching_posts) + len(matching_pages)
        }

    def get_wp_logs(self) -> List[Dict[str, Any]]:
        """Get all WordPress operation logs"""
        return self.operation_logs


# FastMCP server implementation
def main():
    from fastmcp import FastMCP

    # Create MCP server
    mcp = FastMCP("WordPress")
    wp = WordPress()

    @mcp.tool()
    def get_site_info() -> Dict[str, Any]:
        """Get WordPress site information and configuration"""
        return wp.get_site_info()

    @mcp.tool()
    def list_posts(per_page: int = 10, page: int = 1, status: str = "published") -> Dict[str, Any]:
        """List WordPress posts with pagination

        Args:
            per_page: Number of posts per page
            page: Page number (1-based)
            status: Post status (published, draft, private)
        """
        return wp.list_posts(per_page, page, status)

    @mcp.tool()
    def get_post(post_id: int) -> Dict[str, Any]:
        """Get a specific WordPress post by ID

        Args:
            post_id: The ID of the post to retrieve
        """
        return wp.get_post(post_id)

    @mcp.tool()
    def create_post(title: str, content: str, status: str = "draft", author: int = 1) -> Dict[str, Any]:
        """Create a new WordPress post

        Args:
            title: Post title
            content: Post content
            status: Post status (draft, published, private)
            author: Author user ID
        """
        return wp.create_post(title, content, status, author)

    @mcp.tool()
    def update_post(post_id: int, title: str = None, content: str = None, status: str = None) -> Dict[str, Any]:
        """Update an existing WordPress post

        Args:
            post_id: ID of the post to update
            title: New title (optional)
            content: New content (optional)
            status: New status (optional)
        """
        return wp.update_post(post_id, title, content, status)

    @mcp.tool()
    def delete_post(post_id: int) -> Dict[str, Any]:
        """Delete a WordPress post

        Args:
            post_id: ID of the post to delete
        """
        return wp.delete_post(post_id)

    @mcp.tool()
    def list_pages() -> Dict[str, Any]:
        """List all WordPress pages"""
        return wp.list_pages()

    @mcp.tool()
    def list_users() -> Dict[str, Any]:
        """List all WordPress users"""
        return wp.list_users()

    @mcp.tool()
    def create_comment(post_id: int, content: str, author_name: str, author_email: str) -> Dict[str, Any]:
        """Create a comment on a WordPress post

        Args:
            post_id: ID of the post to comment on
            content: Comment content
            author_name: Name of the comment author
            author_email: Email of the comment author
        """
        return wp.create_comment(post_id, content, author_name, author_email)

    @mcp.tool()
    def search_content(search_term: str) -> Dict[str, Any]:
        """Search WordPress content (posts and pages)

        Args:
            search_term: Term to search for
        """
        return wp.search_content(search_term)

    @mcp.tool()
    def get_wp_logs() -> List[Dict[str, Any]]:
        """Get all WordPress operation logs"""
        return wp.get_wp_logs()

    return mcp


if __name__ == "__main__":
    mcp = main()
    mcp.run()
