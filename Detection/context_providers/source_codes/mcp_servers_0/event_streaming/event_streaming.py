#!/usr/bin/env python3
"""
Event Streaming Platform MCP Server
Provides event streaming capabilities similar to Apache Kafka
with topics, producers, consumers, and stream processing.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_streaming")

# Create MCP server instance
mcp = FastMCP('event_streaming')

# Global state
STREAMING_LOGS = []
TOPICS = {}
CONSUMERS = {}
PRODUCERS = {}
STREAM_PROCESSORS = {}

def log_operation(operation: str, details: Dict[str, Any]):
    """Log streaming operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    STREAMING_LOGS.append(log_entry)
    logger.info(f"Event Streaming Operation: {operation} - {details}")

@mcp.tool()
def create_topic(topic_name: str, partitions: int = 3, replication_factor: int = 1, config: dict = None) -> dict:
    """Create a new topic for event streaming"""
    if topic_name in TOPICS:
        return {"error": f"Topic '{topic_name}' already exists"}

    topic_id = str(uuid.uuid4())[:8]
    topic_config = config or {}

    topic = {
        "topic_id": topic_id,
        "name": topic_name,
        "partitions": partitions,
        "replication_factor": replication_factor,
        "config": topic_config,
        "created_at": datetime.now().isoformat(),
        "message_count": 0,
        "total_size_bytes": 0,
        "status": "active"
    }

    TOPICS[topic_name] = topic

    log_operation("create_topic", {
        "topic_name": topic_name,
        "topic_id": topic_id,
        "partitions": partitions,
        "replication_factor": replication_factor
    })

    return {
        "topic_id": topic_id,
        "topic_name": topic_name,
        "status": "created",
        "partitions": partitions,
        "replication_factor": replication_factor
    }

@mcp.tool()
def produce_message(topic_name: str, message: str, key: str = None, headers: dict = None) -> dict:
    """Send a message to a topic"""
    if topic_name not in TOPICS:
        return {"error": f"Topic '{topic_name}' does not exist"}

    topic = TOPICS[topic_name]
    message_id = str(uuid.uuid4())[:8]

    message_record = {
        "message_id": message_id,
        "topic": topic_name,
        "key": key,
        "value": message,
        "headers": headers or {},
        "timestamp": datetime.now().isoformat(),
        "offset": topic["message_count"],
        "partition": hash(key or message_id) % topic["partitions"],
        "size_bytes": len(message.encode('utf-8'))
    }

    # Update topic statistics
    topic["message_count"] += 1
    topic["total_size_bytes"] += message_record["size_bytes"]

    log_operation("produce_message", {
        "topic_name": topic_name,
        "message_id": message_id,
        "key": key,
        "size_bytes": message_record["size_bytes"]
    })

    return {
        "message_id": message_id,
        "topic": topic_name,
        "partition": message_record["partition"],
        "offset": message_record["offset"],
        "timestamp": message_record["timestamp"]
    }

@mcp.tool()
def consume_messages(topic_name: str, consumer_group: str = None, max_messages: int = 10, from_offset: str = "latest") -> dict:
    """Consume messages from a topic"""
    if topic_name not in TOPICS:
        return {"error": f"Topic '{topic_name}' does not exist"}

    topic = TOPICS[topic_name]
    consumer_id = str(uuid.uuid4())[:8]
    consumer_group = consumer_group or f"default-group-{consumer_id}"

    # Simulate message consumption
    messages = []
    for i in range(min(max_messages, 5)):  # Limit for demo
        message = {
            "message_id": str(uuid.uuid4())[:8],
            "topic": topic_name,
            "key": f"key-{i}",
            "value": f"Sample message {i+1} from {topic_name}",
            "headers": {"source": "streaming-platform"},
            "timestamp": datetime.now().isoformat(),
            "offset": topic["message_count"] - max_messages + i,
            "partition": i % topic["partitions"]
        }
        messages.append(message)

    # Track consumer
    CONSUMERS[consumer_id] = {
        "consumer_id": consumer_id,
        "consumer_group": consumer_group,
        "topic": topic_name,
        "created_at": datetime.now().isoformat(),
        "messages_consumed": len(messages),
        "last_offset": messages[-1]["offset"] if messages else 0
    }

    log_operation("consume_messages", {
        "topic_name": topic_name,
        "consumer_id": consumer_id,
        "consumer_group": consumer_group,
        "messages_consumed": len(messages)
    })

    return {
        "consumer_id": consumer_id,
        "consumer_group": consumer_group,
        "topic": topic_name,
        "messages": messages,
        "message_count": len(messages)
    }

@mcp.tool()
def list_topics() -> dict:
    """List all available topics"""
    topics_info = {}

    for topic_name, topic_data in TOPICS.items():
        topics_info[topic_name] = {
            "topic_id": topic_data["topic_id"],
            "partitions": topic_data["partitions"],
            "replication_factor": topic_data["replication_factor"],
            "message_count": topic_data["message_count"],
            "total_size_bytes": topic_data["total_size_bytes"],
            "status": topic_data["status"],
            "created_at": topic_data["created_at"]
        }

    log_operation("list_topics", {"topic_count": len(TOPICS)})

    return {
        "topics": topics_info,
        "total_topics": len(TOPICS)
    }

@mcp.tool()
def get_topic_info(topic_name: str) -> dict:
    """Get detailed information about a specific topic"""
    if topic_name not in TOPICS:
        return {"error": f"Topic '{topic_name}' does not exist"}

    topic = TOPICS[topic_name]

    # Get consumer statistics for this topic
    topic_consumers = [c for c in CONSUMERS.values() if c["topic"] == topic_name]

    topic_info = {
        "topic_id": topic["topic_id"],
        "name": topic["name"],
        "partitions": topic["partitions"],
        "replication_factor": topic["replication_factor"],
        "config": topic["config"],
        "created_at": topic["created_at"],
        "message_count": topic["message_count"],
        "total_size_bytes": topic["total_size_bytes"],
        "status": topic["status"],
        "active_consumers": len(topic_consumers),
        "consumer_groups": list(set(c["consumer_group"] for c in topic_consumers))
    }

    log_operation("get_topic_info", {"topic_name": topic_name})

    return topic_info

@mcp.tool()
def create_stream_processor(processor_name: str, source_topic: str, target_topic: str, processing_config: dict) -> dict:
    """Create a stream processor for real-time data transformation"""
    if source_topic not in TOPICS:
        return {"error": f"Source topic '{source_topic}' does not exist"}

    if target_topic not in TOPICS:
        return {"error": f"Target topic '{target_topic}' does not exist"}

    processor_id = str(uuid.uuid4())[:8]

    processor = {
        "processor_id": processor_id,
        "name": processor_name,
        "source_topic": source_topic,
        "target_topic": target_topic,
        "processing_config": processing_config,
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "messages_processed": 0,
        "processing_rate": 0.0,
        "errors": 0
    }

    STREAM_PROCESSORS[processor_id] = processor

    log_operation("create_stream_processor", {
        "processor_name": processor_name,
        "processor_id": processor_id,
        "source_topic": source_topic,
        "target_topic": target_topic
    })

    return {
        "processor_id": processor_id,
        "processor_name": processor_name,
        "source_topic": source_topic,
        "target_topic": target_topic,
        "status": "created",
        "config": processing_config
    }

@mcp.tool()
def get_streaming_logs(limit: int = 50) -> dict:
    """Retrieve event streaming operation logs"""
    recent_logs = STREAMING_LOGS[-limit:] if limit > 0 else STREAMING_LOGS

    return {
        "logs": recent_logs,
        "total_operations": len(STREAMING_LOGS),
        "returned_count": len(recent_logs)
    }

if __name__ == "__main__":
    mcp.run()
