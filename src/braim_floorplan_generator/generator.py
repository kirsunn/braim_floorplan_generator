"""
Основной модуль генерации планировок.

Алгоритм:
1. Расчёт размеров комнат: площади распределяются пропорционально минимальным требованиям
2. Упаковка: используется shelf-алгоритм (комнаты раскладываются слева-направо)
3. Генерация стен: по границам комнат, с дедупликацией общих стен

Важно: все размеры в модели указываются в **метрах** для внутренней логики,
но при экспорте и в документации используются **мм** (например, 1200 мм, а не 1.2 м).

Исключения:
- Генплан/участок/геодезия — в метрах с точностью (15.22 м)
- Размеры в осях — в мм
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import math


@dataclass
class Room:
    """
    Комната в планировке.
    
    Attributes:
        type: Тип комнаты (living, bedroom, kitchen, bathroom, toilet, hallway)
        area: Площадь комнаты в м²
        x: Координата X левого нижнего угла в м
        y: Координата Y левого нижнего угла в м
        width: Ширина комнаты в м
        height: Глубина (высота) комнаты в м
        name: Уникальное имя комнаты (генерируется автоматически)
    
    Note:
        При экспорте и в документации размеры конвертируются в мм:
        - width_mm = width * 1000
        - height_mm = height * 1000
    """
    type: str
    area: float
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    name: str = ""
    
    def __post_init__(self):
        if not self.name:
            self.name = f"{self.type}_{id(self) % 1000}"
    
    @property
    def aspect_ratio(self) -> float:
        """Соотношение сторон комнаты."""
        if self.height == 0:
            return 0.0
        return max(self.width / self.height, self.height / self.width)
    
    @property
    def min_dimension_mm(self) -> float:
        """Наименьшая сторона комнаты в мм."""
        return min(self.width, self.height) * 1000
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "area": self.area,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "name": self.name,
            # Дополнительно в мм для удобства
            "width_mm": self.width * 1000,
            "height_mm": self.height * 1000,
        }


@dataclass
class Profile:
    """
    Профиль квартиры: список комнат с требованиями.
    
    Attributes:
        apartment_area: Общая площадь квартиры в м²
        rooms: Список спецификаций комнат
    
    Пример спецификации комнаты:
    {
        "type": "living",
        "min_area": 14.0,       # м²
        "preferred_area": 18.0,  # м²
        "preferred_aspect_ratio": 1.2
    }
    """
    apartment_area: float
    rooms: List[Dict] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Profile":
        return cls(
            apartment_area=data.get("apartment_area", 50.0),
            rooms=data.get("rooms", []),
        )
    
    @classmethod
    def from_json_file(cls, filepath: str) -> "Profile":
        import json
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))
    
    def get_room_requirements(self) -> List[Dict]:
        return self.rooms


@dataclass
class Layout:
    """
    Готовая планировка квартиры.
    
    Attributes:
        rooms: Список комнат
        apartment_area: Общая площадь квартиры в м²
        width: Ширина квартиры в м
        height: Глубина квартиры в м
    """
    rooms: List[Room] = field(default_factory=list)
    apartment_area: float = 0.0
    width: float = 0.0
    height: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "rooms": [room.to_dict() for room in self.rooms],
            "apartment_area": self.apartment_area,
            "width": self.width,
            "height": self.height,
            # Дополнительно в мм
            "width_mm": self.width * 1000,
            "height_mm": self.height * 1000,
        }


class FloorplanGenerator:
    """
    Генератор планировок на основе профиля.
    
    Attributes:
        profile: Профиль квартиры
        max_aspect_ratio: Максимальное соотношение сторон комнаты (по умолчанию 4.0)
    """
    
    def __init__(self, profile: Profile, max_aspect_ratio: float = 4.0):
        self.profile = profile
        self.max_aspect_ratio = max_aspect_ratio
    
    def generate(self) -> Layout:
        """
        Генерирует планировку квартиры.
        
        Returns:
            Layout с размещёнными комнатами.
        """
        rooms = self._calculate_room_sizes()
        layout = self._pack_rooms(rooms)
        return layout
    
    def _calculate_room_sizes(self) -> List[Room]:
        """
        Рассчитывает размеры комнат на основе профиля.
        
        Алгоритм:
        1. Суммируем минимальные площади всех комнат.
        2. Распределяем доступную площадь пропорционально минимальным требованиям.
        3. Учитываем preferred_area и max_area из профиля.
        4. Рассчитываем ширину и высоту из площади и preferred_aspect_ratio.
        """
        rooms_data = self.profile.get_room_requirements()
        
        # Сумма минимальных площадей
        total_min_area = sum(room.get("min_area", 5.0) for room in rooms_data)
        
        # Коэффициент масштабирования
        if total_min_area > 0:
            scale_factor = self.profile.apartment_area / total_min_area
        else:
            scale_factor = 1.0
        
        rooms = []
        for room_spec in rooms_data:
            room_type = room_spec.get("type", "room")
            min_area = room_spec.get("min_area", 5.0)
            preferred_area = room_spec.get("preferred_area", min_area * 1.2)
            max_area = room_spec.get("max_area", preferred_area * 1.5)
            
            # Расчёт площади: пропорционально минимальной, но не больше max_area
            calculated_area = min_area * scale_factor
            calculated_area = max(calculated_area, min_area)
            calculated_area = min(calculated_area, max_area)
            
            # Расчёт размеров: пытаемся приблизиться к preferred_aspect_ratio
            preferred_ratio = room_spec.get("preferred_aspect_ratio", 1.2)
            area = calculated_area
            
            # width * height = area, width / height = preferred_ratio
            # => width = sqrt(area * preferred_ratio), height = width / preferred_ratio
            width = math.sqrt(area * preferred_ratio)
            height = width / preferred_ratio
            
            # Проверка на max_aspect_ratio
            if width / height > self.max_aspect_ratio:
                height = math.sqrt(area / self.max_aspect_ratio)
                width = height * self.max_aspect_ratio
            elif height / width > self.max_aspect_ratio:
                width = math.sqrt(area / self.max_aspect_ratio)
                height = width * self.max_aspect_ratio
            
            room = Room(
                type=room_type,
                area=area,
                width=width,
                height=height,
            )
            rooms.append(room)
        
        return rooms
    
    def _pack_rooms(self, rooms: List[Room]) -> Layout:
        """
        Упаковывает комнаты в планировку с помощью shelf-алгоритма.
        
        Алгоритм:
        1. Сортируем комнаты по убыванию высоты.
        2. Раскладываем слева-направо в строки (shelf).
        3. При выходе за границу — перенос на следующую строку.
        """
        if not rooms:
            return Layout()
        
        # Сортировка по убыванию высоты
        sorted_rooms = sorted(rooms, key=lambda r: r.height, reverse=True)
        
        # Параметры упаковки
        apartment_width = sum(room.width for room in sorted_rooms)
        apartment_height = max(room.height for room in sorted_rooms)
        
        # Shelf-алгоритм
        x, y = 0.0, 0.0
        row_height = 0.0
        max_width = 0.0
        
        packed_rooms = []
        for room in sorted_rooms:
            # Если комната не помещается в текущую строку — перенос
            if x + room.width > apartment_width and packed_rooms:
                x = 0.0
                y += row_height
                row_height = 0.0
            
            # Размещение комнаты
            room.x = x
            room.y = y
            packed_rooms.append(room)
            
            # Обновление параметров строки
            x += room.width
            row_height = max(row_height, room.height)
            max_width = max(max_width, x)
        
        # Итоговые размеры квартиры
        final_width = max_width
        final_height = y + row_height
        
        return Layout(
            rooms=packed_rooms,
            apartment_area=self.profile.apartment_area,
            width=final_width,
            height=final_height,
        )
