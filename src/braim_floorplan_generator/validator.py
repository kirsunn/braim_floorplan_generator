"""Legacy validator module for ergonomics checks.

This module is kept for backward compatibility with existing tests.
New validation logic should use the validation engine in src.braim_floorplan_generator.validation.
"""

from dataclasses import dataclass
from typing import List, Literal

from .functional_layout import Layout, Room


@dataclass
class ErgonomicsIssue:
    """Represents an ergonomics issue found during layout validation."""
    room_name: str
    room_type: str
    issue_type: Literal["min_dimension", "aspect_ratio"]
    description: str
    actual_value: float
    required_value: float


class ErgonomicsChecker:
    """Legacy ergonomics checker for simple room layouts.

    Checks:
    - Minimum dimension for each room type.
    - Maximum aspect ratio (default 4.0).
    """

    # Minimum dimensions in meters by room type
    MIN_DIMENSIONS = {
        "living": 3.0,
        "bedroom": 3.0,
        "kitchen": 2.0,
        "bathroom": 1.8,
        "hallway": 1.2,
    }

    # Maximum aspect ratio (length / width)
    MAX_ASPECT_RATIO = 4.0

    def check(self, layout: Layout) -> List[ErgonomicsIssue]:
        """Check a layout for ergonomics issues.

        Args:
            layout: The layout to check.

        Returns:
            A list of ergonomics issues found.
        """
        issues = []

        for room in layout.rooms:
            # Check minimum dimension
            min_dim = self._get_min_dimension(room.type)
            actual_min = min(room.width, room.height)
            if actual_min < min_dim:
                issues.append(ErgonomicsIssue(
                    room_name=room.name,
                    room_type=room.type,
                    issue_type="min_dimension",
                    description=f"Наименьшая сторона комнаты {room.name} ({room.type}) меньше требуемого минимума",
                    actual_value=actual_min,
                    required_value=min_dim,
                ))

            # Check aspect ratio
            aspect_ratio = max(room.width, room.height) / min(room.width, room.height)
            if aspect_ratio > self.MAX_ASPECT_RATIO:
                issues.append(ErgonomicsIssue(
                    room_name=room.name,
                    room_type=room.type,
                    issue_type="aspect_ratio",
                    description=f"Соотношение сторон комнаты {room.name} ({room.type}) превышает максимальное",
                    actual_value=aspect_ratio,
                    required_value=self.MAX_ASPECT_RATIO,
                ))

        return issues

    def _get_min_dimension(self, room_type: str) -> float:
        """Get minimum dimension for a room type."""
        return self.MIN_DIMENSIONS.get(room_type, 2.0)
