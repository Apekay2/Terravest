"""Shared fixtures for Detection unit tests."""

import json
from pathlib import Path

import pytest

DETECTION_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def detection_root() -> Path:
    return DETECTION_ROOT


@pytest.fixture
def sample_conversation() -> list[dict]:
    return [
        {"role": "user", "content": "Summarize the quarterly report", "message_type": "user_prompt"},
        {"role": "assistant", "content": "Here is the summary.", "message_type": "agent_response"},
    ]


@pytest.fixture
def sample_benchmark_run(tmp_path: Path) -> Path:
    """Minimal adr_bench result directory with one benign and one malicious task."""
    run_dir = tmp_path / "adr_bench_20260101_120000"
    run_dir.mkdir()

    for task_id, malicious in [("task_001", False), ("task_002", True)]:
        workspace = run_dir / task_id / "workspace"
        workspace.mkdir(parents=True)
        conversation = [
            {"role": "user", "content": f"Prompt for {task_id}", "message_type": "user_prompt"},
            {"role": "assistant", "content": "Done.", "message_type": "agent_response"},
        ]
        with open(workspace / "claude_conversation.json", "w", encoding="utf-8") as f:
            json.dump(conversation, f)

    return run_dir


@pytest.fixture
def sample_jsonl(tmp_path: Path) -> Path:
    jsonl_path = tmp_path / "mini_bench.jsonl"
    lines = [
        {"type": "manifest", "benchmark_name": "mini_bench", "task_count": 2},
        {
            "type": "task",
            "task_id": "task_001",
            "conversation": {"messages": [{"role": "user", "content": "hello"}]},
            "result": {"status": "ok"},
        },
        {
            "type": "task",
            "task_id": "task_002",
            "conversation": {"messages": [{"role": "user", "content": "world"}]},
        },
    ]
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for record in lines:
            f.write(json.dumps(record) + "\n")
    return jsonl_path
