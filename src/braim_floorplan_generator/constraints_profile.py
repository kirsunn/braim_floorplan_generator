"""
Constraints profile for BRAIM floorplan generator.

This module defines the constraint weights and thresholds used by the
multi-objective optimization in the layout generator.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ConstraintsProfile:
    """Constraint weights and thresholds for layout optimization."""
    
    # Weights for objective function
    overlap_weight: float = 10.0
    boundary_weight: float = 8.0
    circulation_weight: float = 5.0
    adjacency_weight: float = 6.0
    daylight_weight: float = 4.0
    area_weight: float = 3.0
    
    # Thresholds
    min_circulation_width: float = 0.8  # meters
    min_daylight_distance: float = 6.0  # meters from window
    max_dead_end_length: float = 3.0  # meters
    
    # Adjacency preferences (room_type -> preferred neighbors)
    adjacency_preferences: Dict[str, list] = field(default_factory=lambda: {
        "kitchen": ["dining", "living"],
        "bedroom": ["bathroom"],
        "bathroom": ["bedroom"],
        "dining": ["kitchen", "living"],
        "living": ["dining", "kitchen", "entrance"],
        "entrance": ["living", "kitchen"],
        "office": ["living"],
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "weights": {
                "overlap": self.overlap_weight,
                "boundary": self.boundary_weight,
                "circulation": self.circulation_weight,
                "adjacency": self.adjacency_weight,
                "daylight": self.daylight_weight,
                "area": self.area_weight,
            },
            "thresholds": {
                "min_circulation_width": self.min_circulation_width,
                "min_daylight_distance": self.min_daylight_distance,
                "max_dead_end_length": self.max_dead_end_length,
            },
            "adjacency_preferences": self.adjacency_preferences,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConstraintsProfile":
        """Create profile from dictionary."""
        weights = data.get("weights", {})
        thresholds = data.get("thresholds", {})
        return cls(
            overlap_weight=weights.get("overlap", 10.0),
            boundary_weight=weights.get("boundary", 8.0),
            circulation_weight=weights.get("circulation", 5.0),
            adjacency_weight=weights.get("adjacency", 6.0),
            daylight_weight=weights.get("daylight", 4.0),
            area_weight=weights.get("area", 3.0),
            min_circulation_width=thresholds.get("min_circulation_width", 0.8),
            min_daylight_distance=thresholds.get("min_daylight_distance", 6.0),
            max_dead_end_length=thresholds.get("max_dead_end_length", 3.0),
            adjacency_preferences=data.get("adjacency_preferences", cls().adjacency_preferences),
        )


# Default instance
DEFAULT_PROFILE = ConstraintsProfile()
