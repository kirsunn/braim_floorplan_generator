"""
Основной модуль генерации планировок.

Алгоритм:
1. Расчёт размеров комнат: площади распределяются пропорционально минимальным требованиям
2. Упаковка: используется shelf-алгоритм (комнаты раскладываются слева-направо)
3. Генерация стен: по границам комнат, с дедупликацией общих стен
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import math


@dataclass
class Room:
    """Комната в планировке."""
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
        if self.height == 0:
            return 0.0
        return max(self.width / self.height, self.height / self.width)
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "area": self.area,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "name": self.name,
        }


@dataclass
class Profile:
    """Профиль квартиры: список комнат с требованиями."""
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
    """Готовая планировка квартиры."""
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
        }


class FloorplanGenerator:
    """Генератор планировок на основе профиля."""
    
    def __init__(self, profile: Profile, max_aspect_ratio: float = 4.0):
        self.profile = profile
        self.max_aspect_ratio = max_aspect_ratio
    
    def generate(self) -> Layout:
        rooms = self._calculate_room_sizes()
        layout = self._pack_rooms(rooms)
        return layout
    
    def _calculate_room_sizes(self) -> List[Room]:
        rooms_data = self.profile.get_room_requirements()
        total_min_area = sum(room.get("min_area", 5.0) for room in rooms_data)
        
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
            
            calculated_area = min_area * scale_factor
            calculated_area = max(calculated_area, min_area)
            calculated_area = min(calculated_area, max_area)
            
            preferred_ratio = room_spec.get("preferred_aspect_ratio", 1.2)
            area = calculated_area
            
            width = math.sqrt(area * preferred_ratio)
            height = width / preferred_ratio
            
            if width / height > self.max_aspect_ratio:
                height = math.sqrt(area / self.max_aspect_ratio)
                width = height * self.max_aspect_ratio
            elif height / width > self.max_aspect_ratio:
                width = math.sqrt(area / self.max_aspect_ratio)
                height = width * self.max_aspect_ratio
            
            room = Room(type=room_type, area=area, width=width, height=height)
            rooms.append(room)
        
        return rooms
    
    def _pack_rooms(self, rooms: List[Room]) -> Layout:
        if not rooms:
            return Layout()
        
        sorted_rooms = sorted(rooms, key=lambda r: r.height, reverse=True)
        apartment_width = sum(room.width for room in sorted_rooms)
        apartment_height = max(room.height for room in sorted_rooms)
        
        x, y = 0.0, 0.0
        row_height = 0.0
        max_width = 0.0
        
        packed_rooms = []
        for room in sorted_rooms:
            if x + room.width > apartment_width and packed_rooms:
                x = 0.0
                y += row_height
                row_height = 0.0
            
            room.x = x
            room.y = y
            packed_rooms.append(room)
            
            x += room.width
            row_height = max(row_height, room.height)
            max_width = max(max_width, x)
        
        final_width = max_width
        final_height = y + row_height
        
        return Layout(rooms=packed_rooms, apartment_area=self.profile.apartment_area, width=final_width, height=final_height)
