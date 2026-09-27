"""
Конфигурация функциональной планировки.

JSON-схема:
{
  "name": "2-room apartment",
  "perimeter": {
    "type": "rectangle",
    "width_mm": 12000,
    "height_mm": 8000
  },
  "functional_scheme": "linear",
  "zones": {
    "entrance": {
      "depth_mm": 2000,
      "position": "bottom"
    },
    "wet": {
      "depth_mm": 3000,
      "position": "middle",
      "adjacent_to": ["entrance"]
    },
    "living": {
      "position": "top",
      "quiet": true
    }
  },
  "rooms": [
    {
      "type": "living",
      "min_area": 14.0,
      "preferred_area": 18.0,
      "zone": "living"
    }
  ],
  "constraints": {
    "min_corridor_width_mm": 1200,
    "kitchen_near_bathroom": true,
    "bedroom_quiet_zone": true
  }
}
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json


@dataclass
class PerimeterConfig:
    """Конфигурация периметра."""
    type: str  # "rectangle", "polygon", "l_shape"
    width_mm: float = 0.0
    height_mm: float = 0.0
    points_mm: List[List[float]] = field(default_factory=list)  # Для polygon
    
    @classmethod
    def from_dict(cls, data: Dict) -> "PerimeterConfig":
        return cls(
            type=data.get("type", "rectangle"),
            width_mm=data.get("width_mm", 0.0),
            height_mm=data.get("height_mm", 0.0),
            points_mm=data.get("points_mm", []),
        )


@dataclass
class ZoneConfig:
    """Конфигурация зоны."""
    position: str  # "bottom", "middle", "top", "left", "right"
    depth_mm: float = 0.0
    adjacent_to: List[str] = field(default_factory=list)
    quiet: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ZoneConfig":
        return cls(
            position=data.get("position", "top"),
            depth_mm=data.get("depth_mm", 0.0),
            adjacent_to=data.get("adjacent_to", []),
            quiet=data.get("quiet", False),
        )


@dataclass
class RoomConfig:
    """Конфигурация комнаты."""
    type: str
    min_area: float
    preferred_area: float = 0.0
    zone: str = ""
    min_width_mm: float = 1200
    min_height_mm: float = 1200
    
    @classmethod
    def from_dict(cls, data: Dict) -> "RoomConfig":
        min_area = data.get("min_area", 5.0)
        return cls(
            type=data.get("type", "room"),
            min_area=min_area,
            preferred_area=data.get("preferred_area", min_area * 1.2),
            zone=data.get("zone", ""),
            min_width_mm=data.get("min_width_mm", 1200),
            min_height_mm=data.get("min_height_mm", 1200),
        )


@dataclass
class ConstraintsConfig:
    """Ограничения планировки."""
    min_corridor_width_mm: float = 1200
    kitchen_near_bathroom: bool = True
    bedroom_quiet_zone: bool = True
    max_aspect_ratio: float = 4.0
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ConstraintsConfig":
        return cls(
            min_corridor_width_mm=data.get("min_corridor_width_mm", 1200),
            kitchen_near_bathroom=data.get("kitchen_near_bathroom", True),
            bedroom_quiet_zone=data.get("bedroom_quiet_zone", True),
            max_aspect_ratio=data.get("max_aspect_ratio", 4.0),
        )


@dataclass
class LayoutConfig:
    """
    Полная конфигурация планировки.
    
    Attributes:
        name: Название планировки
        perimeter: Конфигурация периметра
        functional_scheme: Тип схемы ("linear", "central", "ring")
        zones: Конфигурация зон
        rooms: Список комнат
        constraints: Ограничения
    """
    name: str
    perimeter: PerimeterConfig
    functional_scheme: str
    zones: Dict[str, ZoneConfig]
    rooms: List[RoomConfig]
    constraints: ConstraintsConfig
    
    @classmethod
    def from_dict(cls, data: Dict) -> "LayoutConfig":
        # Zones
        zones_data = data.get("zones", {})
        zones = {
            name: ZoneConfig.from_dict(config)
            for name, config in zones_data.items()
        }
        
        # Rooms
        rooms = [RoomConfig.from_dict(r) for r in data.get("rooms", [])]
        
        return cls(
            name=data.get("name", "Untitled"),
            perimeter=PerimeterConfig.from_dict(data.get("perimeter", {})),
            functional_scheme=data.get("functional_scheme", "linear"),
            zones=zones,
            rooms=rooms,
            constraints=ConstraintsConfig.from_dict(data.get("constraints", {})),
        )
    
    @classmethod
    def from_json_file(cls, filepath: str) -> "LayoutConfig":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "perimeter": {
                "type": self.perimeter.type,
                "width_mm": self.perimeter.width_mm,
                "height_mm": self.perimeter.height_mm,
            },
            "functional_scheme": self.functional_scheme,
            "zones": {
                name: {
                    "position": zone.position,
                    "depth_mm": zone.depth_mm,
                }
                for name, zone in self.zones.items()
            },
            "rooms": [
                {
                    "type": room.type,
                    "min_area": room.min_area,
                    "preferred_area": room.preferred_area,
                    "zone": room.zone,
                }
                for room in self.rooms
            ],
            "constraints": {
                "min_corridor_width_mm": self.constraints.min_corridor_width_mm,
                "kitchen_near_bathroom": self.constraints.kitchen_near_bathroom,
                "bedroom_quiet_zone": self.constraints.bedroom_quiet_zone,
            },
        }
    
    def save_json(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
