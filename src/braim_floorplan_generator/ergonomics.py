"""
Проверка эргономики планировки.

Правила:
- Минимальные площади: ванная 3 м², туалет 1.5 м², кухня 8 м², спальня 8 м², жилая 14 м², коридор 3 м².
- Минимальные размеры: по 1.5–2.5 м для разных комнат.
- Ограничение пропорций: соотношение сторон не более 4:1.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from .generator import Layout, Room


@dataclass
class RoomRequirements:
    """Требования к комнате по типу."""
    type: str
    min_area: float
    min_width: float
    min_height: float
    max_aspect_ratio: float = 4.0
    
    @classmethod
    def get_defaults(cls) -> Dict[str, "RoomRequirements"]:
        return {
            "bathroom": cls(type="bathroom", min_area=3.0, min_width=1.5, min_height=2.0),
            "toilet": cls(type="toilet", min_area=1.5, min_width=1.0, min_height=1.5),
            "kitchen": cls(type="kitchen", min_area=8.0, min_width=2.0, min_height=2.5),
            "bedroom": cls(type="bedroom", min_area=8.0, min_width=2.5, min_height=3.0),
            "living": cls(type="living", min_area=14.0, min_width=3.0, min_height=3.5),
            "hallway": cls(type="hallway", min_area=3.0, min_width=1.2, min_height=2.5),
        }


@dataclass
class ErgonomicsIssue:
    """Проблема с эргономикой."""
    room_name: str
    room_type: str
    issue_type: str
    description: str
    actual_value: float
    required_value: float


class ErgonomicsChecker:
    """Проверка эргономики планировки."""
    
    def __init__(self, requirements: Optional[Dict[str, RoomRequirements]] = None):
        self.requirements = requirements or RoomRequirements.get_defaults()
    
    def check(self, layout: Layout) -> List[ErgonomicsIssue]:
        issues = []
        
        for room in layout.rooms:
            room_issues = self._check_room(room)
            issues.extend(room_issues)
        
        return issues
    
    def _check_room(self, room: Room) -> List[ErgonomicsIssue]:
        issues = []
        
        req = self.requirements.get(room.type)
        if req is None:
            return issues
        
        if room.area < req.min_area:
            issues.append(ErgonomicsIssue(
                room_name=room.name,
                room_type=room.type,
                issue_type="min_area",
                description=f"Площадь комнаты {room.name} ({room.type}) меньше минимальной",
                actual_value=room.area,
                required_value=req.min_area,
            ))
        
        if room.width < req.min_width:
            issues.append(ErgonomicsIssue(
                room_name=room.name,
                room_type=room.type,
                issue_type="min_width",
                description=f"Ширина комнаты {room.name} ({room.type}) меньше минимальной",
                actual_value=room.width,
                required_value=req.min_width,
            ))
        
        if room.height < req.min_height:
            issues.append(ErgonomicsIssue(
                room_name=room.name,
                room_type=room.type,
                issue_type="min_height",
                description=f"Высота (глубина) комнаты {room.name} ({room.type}) меньше минимальной",
                actual_value=room.height,
                required_value=req.min_height,
            ))
        
        if room.aspect_ratio > req.max_aspect_ratio:
            issues.append(ErgonomicsIssue(
                room_name=room.name,
                room_type=room.type,
                issue_type="max_aspect_ratio",
                description=f"Соотношение сторон комнаты {room.name} ({room.type}) превышает максимальное",
                actual_value=room.aspect_ratio,
                required_value=req.max_aspect_ratio,
            ))
        
        return issues
    
    def is_valid(self, layout: Layout) -> bool:
        return len(self.check(layout)) == 0
    
    def summary(self, layout: Layout) -> str:
        issues = self.check(layout)
        
        if not issues:
            return "✓ Все проверки эргономики пройдены"
        
        lines = [f"✗ Найдено проблем: {len(issues)}"]
        for issue in issues:
            lines.append(f"  - {issue.room_name} ({issue.room_type}): {issue.description}")
            lines.append(f"    Фактически: {issue.actual_value:.2f}, Требуется: {issue.required_value:.2f}")
        
        return "\n".join(lines)
