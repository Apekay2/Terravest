#!/usr/bin/env python3
"""
Virtual Meeting MCP Server
Provides video conferencing and meeting management capabilities including
meeting scheduling, participant management, recording, and analytics.
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
logger = logging.getLogger("virtual_meeting")

# Create MCP server instance
mcp = FastMCP('virtual_meeting')

class VirtualMeetingPlatform:
    def __init__(self):
        self.logs = []
        self.meetings = {}
        self.participants = {}
        self.recordings = {}
        self.meeting_rooms = {}
        self.active_sessions = {}

    def log_operation(self, operation: str, details: Dict[str, Any]):
        """Log virtual meeting operations for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
            "status": "completed"
        }
        self.logs.append(log_entry)
        logger.info(f"Virtual Meeting Operation: {operation} - {details}")

    def schedule_meeting(self, meeting_data: Dict) -> Dict[str, Any]:
        """Schedule a new virtual meeting"""
        meeting_id = str(uuid.uuid4())

        meeting = {
            "meeting_id": meeting_id,
            "title": meeting_data["title"],
            "description": meeting_data.get("description", ""),
            "organizer": meeting_data["organizer"],
            "start_time": meeting_data["start_time"],
            "duration_minutes": meeting_data.get("duration_minutes", 60),
            "end_time": (datetime.fromisoformat(meeting_data["start_time"]) +
                        timedelta(minutes=meeting_data.get("duration_minutes", 60))).isoformat(),
            "timezone": meeting_data.get("timezone", "UTC"),
            "meeting_type": meeting_data.get("meeting_type", "video"),
            "max_participants": meeting_data.get("max_participants", 100),
            "password": meeting_data.get("password"),
            "waiting_room": meeting_data.get("waiting_room", False),
            "recording_enabled": meeting_data.get("recording_enabled", True),
            "created_at": datetime.now().isoformat(),
            "status": "scheduled",
            "invitees": meeting_data.get("invitees", []),
            "agenda": meeting_data.get("agenda", []),
            "join_url": f"https://meet.example.com/join/{meeting_id}",
            "meeting_number": random.randint(100000000, 999999999),
            "dial_in_numbers": [
                {"country": "US", "number": "+1-555-0123"},
                {"country": "UK", "number": "+44-20-1234-5678"}
            ]
        }

        self.meetings[meeting_id] = meeting

        # Send calendar invitations (mock)
        self._send_calendar_invitations(meeting)

        result = {
            "meeting_id": meeting_id,
            "title": meeting["title"],
            "status": "scheduled",
            "start_time": meeting["start_time"],
            "duration_minutes": meeting["duration_minutes"],
            "join_url": meeting["join_url"],
            "meeting_number": meeting["meeting_number"],
            "invitees_count": len(meeting["invitees"]),
            "calendar_invitations_sent": True
        }

        self.log_operation("schedule_meeting", {
            "meeting_id": meeting_id,
            "title": meeting["title"],
            "organizer": meeting["organizer"],
            "start_time": meeting["start_time"],
            "invitees_count": len(meeting["invitees"])
        })

        return result

    def _send_calendar_invitations(self, meeting: Dict):
        """Mock sending calendar invitations to invitees"""
        for invitee in meeting["invitees"]:
            logger.info(f"Sending calendar invitation to {invitee}")

    def start_meeting(self, meeting_id: str, host_info: Dict) -> Dict[str, Any]:
        """Start a scheduled meeting"""
        if meeting_id not in self.meetings:
            raise ValueError(f"Meeting {meeting_id} not found")

        meeting = self.meetings[meeting_id]
        session_id = str(uuid.uuid4())

        # Create active session
        session = {
            "session_id": session_id,
            "meeting_id": meeting_id,
            "started_at": datetime.now().isoformat(),
            "host": host_info,
            "participants": [],
            "status": "active",
            "recording_status": "ready" if meeting["recording_enabled"] else "disabled",
            "screen_sharing": {"active": False, "presenter": None},
            "chat_messages": [],
            "breakout_rooms": [],
            "polls": [],
            "features_used": set()
        }

        self.active_sessions[session_id] = session
        meeting["status"] = "in_progress"
        meeting["session_id"] = session_id

        # Add host as first participant
        host_participant = {
            "participant_id": str(uuid.uuid4()),
            "name": host_info["name"],
            "email": host_info.get("email", ""),
            "role": "host",
            "joined_at": datetime.now().isoformat(),
            "camera_on": True,
            "microphone_on": True,
            "status": "connected"
        }

        session["participants"].append(host_participant)

        result = {
            "session_id": session_id,
            "meeting_id": meeting_id,
            "meeting_title": meeting["title"],
            "status": "started",
            "host_controls": {
                "mute_all": True,
                "enable_waiting_room": meeting["waiting_room"],
                "start_recording": meeting["recording_enabled"],
                "share_screen": True,
                "create_breakout_rooms": True,
                "create_polls": True
            },
            "participant_count": 1,
            "join_url": meeting["join_url"]
        }

        self.log_operation("start_meeting", {
            "session_id": session_id,
            "meeting_id": meeting_id,
            "host": host_info["name"]
        })

        return result

    def join_meeting(self, meeting_identifier: str, participant_info: Dict) -> Dict[str, Any]:
        """Join a meeting (by meeting ID or URL)"""
        # Find meeting by ID or extract from URL
        meeting = None
        for m in self.meetings.values():
            if m["meeting_id"] == meeting_identifier or str(m["meeting_number"]) == meeting_identifier:
                meeting = m
                break

        if not meeting:
            raise ValueError(f"Meeting not found: {meeting_identifier}")

        # Check if meeting is active
        session_id = meeting.get("session_id")
        if not session_id or session_id not in self.active_sessions:
            # Start session if not already started
            if meeting["status"] == "scheduled":
                return {"status": "waiting", "message": "Meeting has not started yet"}
            else:
                raise ValueError("Meeting is not active")

        session = self.active_sessions[session_id]

        # Check participant limits
        if len(session["participants"]) >= meeting["max_participants"]:
            raise ValueError("Meeting is at capacity")

        # Create participant
        participant = {
            "participant_id": str(uuid.uuid4()),
            "name": participant_info["name"],
            "email": participant_info.get("email", ""),
            "role": "attendee",
            "joined_at": datetime.now().isoformat(),
            "camera_on": participant_info.get("camera_on", True),
            "microphone_on": participant_info.get("microphone_on", True),
            "status": "connected",
            "ip_address": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
        }

        # Handle waiting room
        if meeting["waiting_room"] and participant["role"] != "host":
            participant["status"] = "waiting_room"
            result = {
                "participant_id": participant["participant_id"],
                "status": "waiting_for_admission",
                "message": "You are in the waiting room. The host will admit you shortly."
            }
        else:
            session["participants"].append(participant)
            result = {
                "participant_id": participant["participant_id"],
                "session_id": session_id,
                "meeting_title": meeting["title"],
                "status": "joined",
                "participant_count": len(session["participants"]),
                "meeting_controls": {
                    "mute_self": True,
                    "turn_off_camera": True,
                    "share_screen": participant["role"] in ["host", "co_host"],
                    "use_chat": True,
                    "raise_hand": True
                }
            }

        self.log_operation("join_meeting", {
            "meeting_id": meeting["meeting_id"],
            "participant_name": participant["name"],
            "participant_id": participant["participant_id"],
            "waiting_room": participant["status"] == "waiting_room"
        })

        return result

    def start_recording(self, session_id: str, recording_type: str = "cloud") -> Dict[str, Any]:
        """Start recording a meeting session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        meeting = self.meetings[session["meeting_id"]]

        if not meeting["recording_enabled"]:
            raise ValueError("Recording is not enabled for this meeting")

        recording_id = str(uuid.uuid4())

        recording = {
            "recording_id": recording_id,
            "session_id": session_id,
            "meeting_id": session["meeting_id"],
            "recording_type": recording_type,  # "cloud", "local"
            "started_at": datetime.now().isoformat(),
            "status": "recording",
            "file_size_mb": 0,
            "duration_seconds": 0,
            "quality": "HD",
            "audio_only": False,
            "transcript_enabled": True
        }

        self.recordings[recording_id] = recording
        session["recording_status"] = "recording"
        session["recording_id"] = recording_id

        result = {
            "recording_id": recording_id,
            "status": "started",
            "recording_type": recording_type,
            "estimated_file_size_per_hour": "500MB" if recording_type == "cloud" else "1GB",
            "participant_notification": True
        }

        self.log_operation("start_recording", {
            "recording_id": recording_id,
            "session_id": session_id,
            "recording_type": recording_type
        })

        return result

    def generate_meeting_analytics(self, meeting_id: str) -> Dict[str, Any]:
        """Generate analytics for a completed meeting"""
        if meeting_id not in self.meetings:
            raise ValueError(f"Meeting {meeting_id} not found")

        meeting = self.meetings[meeting_id]

        # Mock analytics data
        analytics = {
            "meeting_id": meeting_id,
            "meeting_title": meeting["title"],
            "duration_minutes": random.randint(30, 120),
            "participant_stats": {
                "total_unique_participants": random.randint(5, 50),
                "peak_concurrent_participants": random.randint(8, 45),
                "average_participants": random.randint(10, 30),
                "total_participant_minutes": random.randint(300, 2000)
            },
            "engagement_metrics": {
                "camera_usage_percentage": random.randint(60, 95),
                "microphone_usage_percentage": random.randint(70, 100),
                "chat_messages_sent": random.randint(10, 100),
                "screen_shares_count": random.randint(1, 5),
                "polls_conducted": random.randint(0, 3),
                "reactions_sent": random.randint(20, 200)
            },
            "quality_metrics": {
                "average_audio_quality": round(random.uniform(4.0, 5.0), 1),
                "average_video_quality": round(random.uniform(3.8, 5.0), 1),
                "connection_issues": random.randint(0, 5),
                "dropped_participants": random.randint(0, 2)
            },
            "feature_usage": {
                "breakout_rooms_used": random.choice([True, False]),
                "recording_enabled": meeting["recording_enabled"],
                "waiting_room_used": meeting["waiting_room"],
                "screen_sharing_sessions": random.randint(1, 3)
            },
            "generated_at": datetime.now().isoformat()
        }

        self.log_operation("generate_meeting_analytics", {
            "meeting_id": meeting_id,
            "total_participants": analytics["participant_stats"]["total_unique_participants"],
            "duration_minutes": analytics["duration_minutes"]
        })

        return analytics

# Create global server instance
MEETING_PLATFORM = VirtualMeetingPlatform()

@mcp.tool()
def get_meeting_logs(limit: int = 50) -> dict:
    """Get virtual meeting platform logs"""
    recent_logs = MEETING_PLATFORM.logs[-limit:]
    return {
        "logs": recent_logs,
        "count": len(recent_logs),
        "retrieved_at": datetime.now().isoformat()
    }

# Convert class methods to global functions with @mcp.tool() decorators
@mcp.tool()
def schedule_meeting(meeting_data: dict) -> dict:
    """Schedule a new virtual meeting"""
    return MEETING_PLATFORM.schedule_meeting(meeting_data)

@mcp.tool()
def start_meeting(meeting_id: str, host_info: dict) -> dict:
    """Start a scheduled meeting"""
    return MEETING_PLATFORM.start_meeting(meeting_id, host_info)

@mcp.tool()
def join_meeting(meeting_identifier: str, participant_info: dict) -> dict:
    """Join a meeting as a participant"""
    return MEETING_PLATFORM.join_meeting(meeting_identifier, participant_info)

@mcp.tool()
def start_recording(session_id: str, recording_type: str = "cloud") -> dict:
    """Start recording a meeting session"""
    return MEETING_PLATFORM.start_recording(session_id, recording_type)

@mcp.tool()
def generate_meeting_analytics(meeting_id: str) -> dict:
    """Generate analytics for a completed meeting"""
    return MEETING_PLATFORM.generate_meeting_analytics(meeting_id)

@mcp.tool()
def create_breakout_rooms(session_id: str, room_config: dict) -> dict:
    """Create breakout rooms for an active meeting session"""
    room_count = room_config.get("room_count", 2)
    assignment_type = room_config.get("assignment", "automatic")  # automatic or manual

    breakout_rooms = []
    for i in range(room_count):
        room_id = str(uuid.uuid4())[:8]
        breakout_rooms.append({
            "room_id": room_id,
            "room_name": f"Breakout Room {i+1}",
            "participants": [],
            "created_at": datetime.now().isoformat(),
            "status": "active"
        })

    MEETING_PLATFORM.log_operation("create_breakout_rooms", {
        "session_id": session_id,
        "room_count": room_count,
        "assignment_type": assignment_type
    })

    return {
        "session_id": session_id,
        "rooms_created": room_count,
        "breakout_rooms": breakout_rooms,
        "assignment_type": assignment_type,
        "status": "created"
    }

if __name__ == "__main__":
    mcp.run()
