"""Tests for CLI validation in main_detector."""

import subprocess
import sys
from pathlib import Path

import pytest

DETECTION_ROOT = Path(__file__).resolve().parent.parent


class TestMainDetectorCLI:
    def test_rejects_zero_concurrent(self):
        result = subprocess.run(
            [sys.executable, "main_detector.py", "--detector", "adr", "--concurrent", "0"],
            cwd=DETECTION_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "max_concurrent must be >= 1" in (result.stderr + result.stdout)

    def test_rejects_missing_results_dir(self):
        result = subprocess.run(
            [
                sys.executable,
                "main_detector.py",
                "--results-dir",
                "benchmark/does_not_exist_00000000",
            ],
            cwd=DETECTION_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "Results directory not found" in (result.stderr + result.stdout)

    def test_default_detector_is_ads(self):
        result = subprocess.run(
            [sys.executable, "main_detector.py", "--help"],
            cwd=DETECTION_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "default: adr" in (result.stderr + result.stdout).lower()

    def test_help_mentions_keyless_smoke_test_detector(self):
        result = subprocess.run(
            [sys.executable, "main_detector.py", "--help"],
            cwd=DETECTION_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        help_text = (result.stderr + result.stdout).lower()
        assert "llamafirewall" in help_text
        assert "keyless" in help_text or "smoke" in help_text

    def test_rejects_adr_bench_on_agentdojo_layout(self, tmp_path: Path):
        bench = tmp_path / "agentdojo_layout"
        bench.mkdir()
        (bench / "ground_truth.json").write_text("{}")
        (bench / "task_001").mkdir()

        result = subprocess.run(
            [
                sys.executable,
                "main_detector.py",
                "--benchmark",
                "adr_bench",
                "--detector",
                "llamafirewall",
                "--results-dir",
                str(bench),
            ],
            cwd=DETECTION_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "does not use per-run ground_truth.json" in (result.stderr + result.stdout)

    def test_rejects_agentdojo_without_ground_truth(self, tmp_path: Path):
        bench = tmp_path / "pinned_run"
        bench.mkdir()
        (bench / "task_001").mkdir()

        result = subprocess.run(
            [
                sys.executable,
                "main_detector.py",
                "--benchmark",
                "agentdojo",
                "--detector",
                "llamafirewall",
                "--results-dir",
                str(bench),
            ],
            cwd=DETECTION_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "requires ground_truth.json" in (result.stderr + result.stdout)
