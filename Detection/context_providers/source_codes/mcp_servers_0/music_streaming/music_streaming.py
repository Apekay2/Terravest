#!/usr/bin/env python3
"""
Music Streaming MCP Server
Provides music streaming platform capabilities including playlist management,
music discovery, audio streaming, and music analytics.
"""

import asyncio
import json
import sys
import logging
import uuid
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("music_streaming")

# Create MCP server instance
mcp = FastMCP('music_streaming')

class MusicStreamingPlatform:
    def __init__(self):
        self.logs = []
        self.users = {}
        self.playlists = {}
        self.songs = {}
        self.streaming_sessions = {}

        # Pre-populate with sample music data
        self._initialize_sample_music()

    def log_operation(self, operation: str, details: Dict[str, Any]):
        """Log music streaming operations for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
            "status": "completed"
        }
        self.logs.append(log_entry)
        logger.info(f"Music Streaming Operation: {operation} - {details}")

    def _initialize_sample_music(self):
        """Initialize platform with sample music data"""
        genres = ["pop", "rock", "jazz", "classical", "electronic", "hip-hop", "country", "r&b"]
        artists = ["Artist Alpha", "Beta Band", "Gamma Group", "Delta Duo", "Echo Ensemble"]

        for i in range(50):  # Create 50 sample songs
            song_id = str(uuid.uuid4())
            self.songs[song_id] = {
                "song_id": song_id,
                "title": f"Song {i + 1}",
                "artist": random.choice(artists),
                "album": f"Album {random.randint(1, 20)}",
                "genre": random.choice(genres),
                "duration_seconds": random.randint(180, 300),
                "release_date": (datetime.now() - timedelta(days=random.randint(1, 3650))).isoformat(),
                "play_count": random.randint(1000, 1000000),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "audio_url": f"https://music-stream.example.com/audio/{song_id}.mp3"
            }

    @mcp.tool()
    def create_user_profile(self, user_info: Dict) -> Dict[str, Any]:
        """Create a new user profile for the music platform"""
        user_id = str(uuid.uuid4())

        user_profile = {
            "user_id": user_id,
            "username": user_info["username"],
            "email": user_info["email"],
            "display_name": user_info.get("display_name", user_info["username"]),
            "created_at": datetime.now().isoformat(),
            "subscription_type": user_info.get("subscription_type", "free"),
            "preferred_genres": user_info.get("preferred_genres", []),
            "listening_history": [],
            "total_listening_time_hours": 0.0,
            "playlists": [],
            "following": [],
            "followers": [],
            "last_active": datetime.now().isoformat()
        }

        self.users[user_id] = user_profile

        result = {
            "user_id": user_id,
            "username": user_profile["username"],
            "status": "created",
            "subscription_type": user_profile["subscription_type"],
            "welcome_playlist_id": self._create_welcome_playlist(user_id),
            "discovery_recommendations": 10
        }

        self.log_operation("create_user_profile", {
            "user_id": user_id,
            "username": user_profile["username"],
            "subscription_type": user_profile["subscription_type"]
        })

        return result

    def _create_welcome_playlist(self, user_id: str) -> str:
        """Create a welcome playlist for new users"""
        playlist_id = str(uuid.uuid4())
        welcome_songs = random.sample(list(self.songs.keys()), 10)

        playlist = {
            "playlist_id": playlist_id,
            "name": "Welcome to Music Streaming",
            "description": "A curated selection to get you started",
            "creator_id": "system",
            "created_at": datetime.now().isoformat(),
            "song_ids": welcome_songs,
            "is_public": False,
            "total_duration_seconds": sum(self.songs[sid]["duration_seconds"] for sid in welcome_songs),
            "play_count": 0,
            "follower_count": 0
        }

        self.playlists[playlist_id] = playlist
        return playlist_id

    @mcp.tool()
    def create_playlist(self, user_id: str, playlist_info: Dict) -> Dict[str, Any]:
        """Create a new playlist for a user"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")

        playlist_id = str(uuid.uuid4())

        playlist = {
            "playlist_id": playlist_id,
            "name": playlist_info["name"],
            "description": playlist_info.get("description", ""),
            "creator_id": user_id,
            "created_at": datetime.now().isoformat(),
            "song_ids": playlist_info.get("song_ids", []),
            "is_public": playlist_info.get("is_public", True),
            "total_duration_seconds": 0,
            "play_count": 0,
            "follower_count": 0,
            "tags": playlist_info.get("tags", [])
        }

        # Calculate total duration
        if playlist["song_ids"]:
            playlist["total_duration_seconds"] = sum(
                self.songs.get(sid, {}).get("duration_seconds", 0)
                for sid in playlist["song_ids"]
            )

        self.playlists[playlist_id] = playlist
        self.users[user_id]["playlists"].append(playlist_id)

        result = {
            "playlist_id": playlist_id,
            "name": playlist["name"],
            "status": "created",
            "song_count": len(playlist["song_ids"]),
            "total_duration_minutes": round(playlist["total_duration_seconds"] / 60, 1),
            "is_public": playlist["is_public"],
            "share_url": f"https://music-stream.example.com/playlist/{playlist_id}"
        }

        self.log_operation("create_playlist", {
            "playlist_id": playlist_id,
            "user_id": user_id,
            "name": playlist["name"],
            "song_count": len(playlist["song_ids"])
        })

        return result

    def start_streaming_session(self, user_id: str, song_id: str, quality: str = "high") -> Dict[str, Any]:
        """Start a music streaming session"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        if song_id not in self.songs:
            raise ValueError(f"Song {song_id} not found")

        session_id = str(uuid.uuid4())
        song = self.songs[song_id]
        user = self.users[user_id]

        # Check subscription limits
        if user["subscription_type"] == "free" and quality == "lossless":
            quality = "standard"  # Downgrade quality for free users

        streaming_session = {
            "session_id": session_id,
            "user_id": user_id,
            "song_id": song_id,
            "started_at": datetime.now().isoformat(),
            "quality": quality,
            "status": "streaming",
            "current_position_seconds": 0,
            "stream_url": f"https://stream-{quality}.example.com/{song_id}",
            "bitrate_kbps": {"low": 96, "standard": 128, "high": 320, "lossless": 1411}[quality]
        }

        self.streaming_sessions[session_id] = streaming_session

        # Update song play count
        song["play_count"] += 1

        # Add to user's listening history
        history_entry = {
            "song_id": song_id,
            "played_at": datetime.now().isoformat(),
            "session_id": session_id
        }
        user["listening_history"].append(history_entry)

        result = {
            "session_id": session_id,
            "song_title": song["title"],
            "artist": song["artist"],
            "duration_seconds": song["duration_seconds"],
            "quality": quality,
            "bitrate_kbps": streaming_session["bitrate_kbps"],
            "stream_url": streaming_session["stream_url"],
            "next_song_recommendations": self._get_recommendations(user_id, song_id)
        }

        self.log_operation("start_streaming_session", {
            "session_id": session_id,
            "user_id": user_id,
            "song_id": song_id,
            "quality": quality
        })

        return result

    def _get_recommendations(self, user_id: str, current_song_id: str) -> List[Dict]:
        """Get song recommendations based on current song and user preferences"""
        current_song = self.songs[current_song_id]
        user = self.users[user_id]

        # Simple recommendation: same genre or artist
        recommendations = []
        for song_id, song in self.songs.items():
            if song_id == current_song_id:
                continue

            score = 0
            if song["genre"] == current_song["genre"]:
                score += 3
            if song["artist"] == current_song["artist"]:
                score += 5
            if song["genre"] in user.get("preferred_genres", []):
                score += 2

            if score > 0:
                recommendations.append({
                    "song_id": song_id,
                    "title": song["title"],
                    "artist": song["artist"],
                    "genre": song["genre"],
                    "recommendation_score": score
                })

        # Sort by score and return top 5
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return recommendations[:5]

    def search_music(self, query: str, search_type: str = "all", limit: int = 20) -> Dict[str, Any]:
        """Search for music by title, artist, album, or genre"""
        query_lower = query.lower()
        results = {
            "query": query,
            "search_type": search_type,
            "songs": [],
            "artists": [],
            "albums": [],
            "playlists": []
        }

        # Search songs
        if search_type in ["all", "songs"]:
            for song_id, song in self.songs.items():
                if (query_lower in song["title"].lower() or
                    query_lower in song["artist"].lower() or
                    query_lower in song["album"].lower() or
                    query_lower in song["genre"].lower()):

                    results["songs"].append({
                        "song_id": song_id,
                        "title": song["title"],
                        "artist": song["artist"],
                        "album": song["album"],
                        "genre": song["genre"],
                        "duration_seconds": song["duration_seconds"],
                        "play_count": song["play_count"]
                    })

        # Search playlists
        if search_type in ["all", "playlists"]:
            for playlist_id, playlist in self.playlists.items():
                if (query_lower in playlist["name"].lower() or
                    query_lower in playlist.get("description", "").lower()):

                    results["playlists"].append({
                        "playlist_id": playlist_id,
                        "name": playlist["name"],
                        "description": playlist.get("description", ""),
                        "song_count": len(playlist["song_ids"]),
                        "creator_id": playlist["creator_id"]
                    })

        # Limit results
        results["songs"] = results["songs"][:limit]
        results["playlists"] = results["playlists"][:limit]

        total_results = len(results["songs"]) + len(results["playlists"])

        self.log_operation("search_music", {
            "query": query,
            "search_type": search_type,
            "total_results": total_results
        })

        return results

# Create global server instance
MUSIC_PLATFORM = MusicStreamingPlatform()

@mcp.tool()
def get_music_logs(limit: int = 50) -> dict:
    """Get music streaming operation logs"""
    recent_logs = MUSIC_PLATFORM.logs[-limit:]
    return {
        "logs": recent_logs,
        "count": len(recent_logs),
        "retrieved_at": datetime.now().isoformat()
    }

@mcp.tool()
def start_streaming_session(user_id: str, playlist_id: str = None, preferences: dict = None) -> dict:
    """Start a music streaming session"""
    return MUSIC_PLATFORM.start_streaming_session(user_id, playlist_id, preferences)

@mcp.tool()
def search_music(user_id: str, search_query: str, search_type: str = "all") -> dict:
    """Search for music content"""
    return MUSIC_PLATFORM.search_music(user_id, search_query, search_type)

@mcp.tool()
def get_music_recommendations(user_id: str, recommendation_type: str = "personalized") -> dict:
    """Get personalized music recommendations"""
    return MUSIC_PLATFORM.get_music_recommendations(user_id, recommendation_type)

@mcp.tool()
def get_streaming_analytics(user_id: str, time_period: str = "week") -> dict:
    """Get streaming analytics and insights"""
    return MUSIC_PLATFORM.get_streaming_analytics(user_id, time_period)
if __name__ == "__main__":
    mcp.run()
