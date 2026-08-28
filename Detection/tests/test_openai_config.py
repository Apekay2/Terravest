"""Tests for openai_config helpers."""

import pytest

from openai_config import calculate_cost


class TestCalculateCost:
    def test_zero_tokens(self):
        assert calculate_cost(2.50, 10.00, 0, 0) == 0.0

    def test_input_only(self):
        # 1M input tokens at $2.50/1M
        assert calculate_cost(2.50, 10.00, 1_000_000, 0) == pytest.approx(2.50)

    def test_output_only(self):
        assert calculate_cost(2.50, 10.00, 0, 1_000_000) == pytest.approx(10.00)

    def test_mixed_tokens(self):
        cost = calculate_cost(3.00, 15.00, 500_000, 200_000)
        expected = (500_000 * 3.00 + 200_000 * 15.00) / 1_000_000
        assert cost == pytest.approx(expected)
