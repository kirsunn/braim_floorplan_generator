"""
Проверка эргономики планировки.

Правила:
- Минимальные площади: ванная 3 м², туалет 1.5 м², кухня 8 м², спальня 8 м², жилая 14 м², коридор 3 м².
- Минимальные размеры: для всех комнат наименьшая сторона ≥ 1200 мм (1.2 м).
- Ограничение пропорций: соотношение сторон не более 4:1.

Важно: все размеры в модели указываются в мм (например, 1200, а не 1.2 м).
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from .generator import Layout, Room


@dataclass
class RoomRequirements:
    """Требования к комнате по типу."""
    type: str
    min_area: float  # м²
    min_dimension: float  # мм - наименьшая сторона комнаты
    max_aspect_ratio: float = 4.0
    
    @classmethod
    def get_defaults(cls) -> Dict[str, "RoomRequirements"]:
        """
        Требования по умолчанию.
        
        min_dimension - наименьшая сторона комнаты в мм.
        Для всех типов комнат минимальная ширина прохода/доступа = 1200 мм.
        """
        return {
            "bathroom": cls(type="bathroom", min_area=3.0, min_dimension=1200),
            "toilet": cls(type="toilet", min_area=1.5, min_dimension=1200),
            "kitchen": cls(type="kitchen", min_area=8.0, min_dimension=1200),
            "bedroom": cls(type="bedroom", min_area=8.0, min_dimension=1200),
            "living": cls(type="living", min_area=14.0, min_dimension=1200),
            "hallway": cls(type="hallway", min_area=3.0, min_dimension=1200),
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
        """
        Проверяет комнату на соответствие эргономическим нормам.
        
        Для всех комнат:
        1. Площадь ≥ min_area
        2. Наименьшая сторона ≥ min_dimension (1200 мм для всех типов)
        3. Соотношение сторон ≤ max_aspect_ratio
        """
        issues = []
        
        req = self.requirements.get(room.type)
        if req is None:
            # Для неизвестных типов комнат проверка не выполняется
            return issues
        
        # Проверка площади
        if room.area < req.min_area:
            issues.append(ErgonomicsIssue(
                room_name=room.name,
                room_type=room.type,
                issue_type="min_area",
                description=f"Площадь комнаты {room.name} ({room.type}) меньше минимальной",
                actual_value=room.area,
                required_value=req.min_area,
            ))
        
        # Проверка наименьшей стороны (в мм)
        min_dim = min(room.width, room.height) * 1000  # конвертируем м → мм
        if min_dim < req.min_dimension:
            issues.append(ErgonomicsIssue(
                room_name=room.name,
                room_type=room.type,
                issue_type="min_dimension",
                description=f"Наименьшая сторона комнаты {room.name} ({room.type}) меньше минимальной",
                actual_value=min_dim,
                required_value=req.min_dimension,
            ))
        
        # Проверка пропорций
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
            lines.append(f"    Фактически: {issue.actual_value:.0f} мм, Требуется: {issue.required_value:.0f} мм")
        
        return "\n".join(lines)
