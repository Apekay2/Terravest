"""
Base parser interface for ADR Sensor.

All parsers should inherit from BaseParser and implement the parse_all() method.
This enables easy extension with new AI agent log formats.
"""

from abc import ABC, abstractmethod
from typing import List

from ..schemas.agent_event_schema import AgentEvent


class BaseParser(ABC):
    """Abstract base class for all ADR parsers.

    To add support for a new AI agent, create a new parser class that inherits
    from BaseParser and implements the parse_all() method.

    Example:
        class MyAgentParser(BaseParser):
            def parse_all(self) -> List[AgentEvent]:
                # Parse logs from your agent and return AgentEvent objects
                ...
    """

    @abstractmethod
    def parse_all(self) -> List[AgentEvent]:
        """Parse all available logs and return a list of AgentEvent objects.

        Returns:
            List of AgentEvent objects representing parsed telemetry data.
        """
        ...
