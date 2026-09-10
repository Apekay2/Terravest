import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs

class YouTubeTranscriptService:
    def __init__(self):
        self.operation_logs = []
        self.content_library = {
            # Educational and business content examples
            "qLgBJcBdYgs": {
                "video_id": "qLgBJcBdYgs",
                "title": "Introduction to Digital Marketing Strategies",
                "duration": "12:45",
                "language": "en",
                "transcript": [
                    {"start": 0.0, "duration": 4.2, "text": "Today we'll explore effective digital marketing strategies for modern businesses"},
                    {"start": 4.2, "duration": 6.1, "text": "Digital marketing has transformed how companies reach and engage with their customers"},
                    {"start": 10.3, "duration": 5.8, "text": "We'll cover search engine optimization, content marketing, and social media advertising"},
                    {"start": 16.1, "duration": 4.9, "text": "These techniques help businesses build brand awareness and drive customer acquisition"},
                    {"start": 21.0, "duration": 7.2, "text": "Let's start by examining how search engines determine content relevance and ranking"},
                    {"start": 28.2, "duration": 6.4, "text": "Understanding keyword research is fundamental to creating content that reaches your audience"},
                    {"start": 34.6, "duration": 8.1, "text": "Social media platforms offer powerful targeting options for reaching specific demographic groups"}
                ]
            },
            "w8KgJFm2ux0": {
                "video_id": "w8KgJFm2ux0",
                "title": "Cloud Computing Fundamentals for Enterprise",
                "duration": "18:22",
                "language": "en",
                "transcript": [
                    {"start": 0.0, "duration": 3.5, "text": "Cloud computing has revolutionized enterprise IT infrastructure"},
                    {"start": 3.5, "duration": 5.2, "text": "Organizations can now scale resources dynamically based on business demands"},
                    {"start": 8.7, "duration": 4.8, "text": "The three main service models are Infrastructure, Platform, and Software as a Service"},
                    {"start": 13.5, "duration": 6.1, "text": "Each model offers different levels of control and management responsibility for IT teams"}
                ]
            }
        }

    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """Log operation for audit trail"""
        log_entry = {
            "operation": operation,
            "details": details,
            "timestamp": time.time()
        }
        self.operation_logs.append(log_entry)

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        try:
            if "youtube.com/watch" in url:
                parsed = urlparse(url)
                return parse_qs(parsed.query).get('v', [None])[0]
            elif "youtu.be/" in url:
                return url.split('/')[-1].split('?')[0]
            else:
                # Assume it's already a video ID
                return url
        except:
            return None

    def get_transcripts(self, video_url: str, languages: List[str] = None) -> Dict[str, Any]:
        """Get transcript for a YouTube video

        Args:
            video_url: YouTube URL or video ID
            languages: List of preferred languages (e.g., ['en', 'es'])
        """
        video_id = self._extract_video_id(video_url)

        self._log_operation("get_transcripts", {
            "video_url": video_url,
            "video_id": video_id,
            "languages": languages or ["en"]
        })

        if not video_id:
            return {
                "status": "error",
                "message": f"Could not extract video ID from URL: {video_url}",
                "error_code": "INVALID_URL"
            }

        # Check if we have a transcript
        if video_id in self.content_library:
            transcript_data = self.content_library[video_id]

            return {
                "status": "success",
                "message": f"Successfully retrieved transcript for video {video_id}",
                "video_id": video_id,
                "video_url": video_url,
                "title": transcript_data["title"],
                "duration": transcript_data["duration"],
                "language": transcript_data["language"],
                "transcript": transcript_data["transcript"],
                "transcript_count": len(transcript_data["transcript"]),
                "full_text": " ".join([entry["text"] for entry in transcript_data["transcript"]])
            }
        else:
            # Generate a realistic transcript for unknown videos
            return {
                "status": "success",
                "message": f"Successfully retrieved transcript for video {video_id}",
                "video_id": video_id,
                "video_url": video_url,
                "title": f"Sample Video {video_id}",
                "duration": "5:30",
                "language": "en",
                "transcript": [
                    {"start": 0.0, "duration": 3.5, "text": "Welcome to this educational video"},
                    {"start": 3.5, "duration": 4.2, "text": "Today we'll be learning about important concepts"},
                    {"start": 7.7, "duration": 3.8, "text": "Let's start with the basics and build from there"},
                    {"start": 11.5, "duration": 5.1, "text": "This content is designed to be informative and easy to follow"},
                    {"start": 16.6, "duration": 4.0, "text": "Thank you for watching and learning with us"}
                ],
                "transcript_count": 5,
                "full_text": "Welcome to this educational video Today we'll be learning about important concepts Let's start with the basics and build from there This content is designed to be informative and easy to follow Thank you for watching and learning with us"
            }

    def list_available_languages(self, video_url: str) -> Dict[str, Any]:
        """List available transcript languages for a video"""
        video_id = self._extract_video_id(video_url)

        self._log_operation("list_available_languages", {
            "video_url": video_url,
            "video_id": video_id
        })

        if not video_id:
            return {
                "status": "error",
                "message": f"Could not extract video ID from URL: {video_url}"
            }

        # sample available languages
        available_languages = ["en", "es", "fr", "de", "auto"]

        return {
            "status": "success",
            "message": f"Found {len(available_languages)} available languages",
            "video_id": video_id,
            "video_url": video_url,
            "available_languages": available_languages,
            "default_language": "en"
        }

    def search_transcript(self, video_url: str, search_term: str) -> Dict[str, Any]:
        """Search for specific terms in the transcript"""
        video_id = self._extract_video_id(video_url)

        self._log_operation("search_transcript", {
            "video_url": video_url,
            "video_id": video_id,
            "search_term": search_term
        })

        # Get the transcript first
        transcript_result = self.get_transcripts(video_url)

        if transcript_result["status"] == "error":
            return transcript_result

        # Search in the transcript
        matches = []
        search_lower = search_term.lower()

        for entry in transcript_result["transcript"]:
            if search_lower in entry["text"].lower():
                matches.append({
                    "start": entry["start"],
                    "duration": entry["duration"],
                    "text": entry["text"],
                    "timestamp": f"{int(entry['start']//60):02d}:{int(entry['start']%60):02d}"
                })

        return {
            "status": "success",
            "message": f"Found {len(matches)} matches for '{search_term}'",
            "video_id": video_id,
            "search_term": search_term,
            "matches": matches,
            "total_matches": len(matches)
        }

    def get_transcript_logs(self) -> List[Dict[str, Any]]:
        """Get all transcript operation logs"""
        return self.operation_logs


# FastMCP server implementation
def main():
    from fastmcp import FastMCP

    # Create MCP server
    mcp = FastMCP("YouTube Transcript")
    yt = YouTubeTranscriptService()

    @mcp.tool()
    def get_transcripts(video_url: str, languages: List[str] = None) -> Dict[str, Any]:
        """Get transcript for a YouTube video

        Args:
            video_url: YouTube URL or video ID
            languages: List of preferred languages (optional)
        """
        return yt.get_transcripts(video_url, languages)

    @mcp.tool()
    def list_available_languages(video_url: str) -> Dict[str, Any]:
        """List available transcript languages for a YouTube video

        Args:
            video_url: YouTube URL or video ID
        """
        return yt.list_available_languages(video_url)

    @mcp.tool()
    def search_transcript(video_url: str, search_term: str) -> Dict[str, Any]:
        """Search for specific terms in a video transcript

        Args:
            video_url: YouTube URL or video ID
            search_term: Term to search for in the transcript
        """
        return yt.search_transcript(video_url, search_term)

    @mcp.tool()
    def get_transcript_logs() -> List[Dict[str, Any]]:
        """Get all YouTube transcript operation logs"""
        return yt.get_transcript_logs()

    return mcp


if __name__ == "__main__":
    mcp = main()
    mcp.run()
