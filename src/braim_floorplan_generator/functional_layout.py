"""
Функциональный слой планировки.

Зонирование:
- Входная зона: hallway, toilet (гостевой санузел)
- Мокрая зона: bathroom, kitchen (инженерные коммуникации)
- Жилая зона: living, bedroom (тихие комнаты)

Логика размещения:
1. Входная зона у границы периметра (ближе к входу)
2. Мокрая зона группируется рядом (общие коммуникации)
3. Жилая зона в глубине квартиры
4. Все зоны соединены через коридор
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math

from .generator import Room, Layout, Profile


class ZoneType(Enum):
    """Тип функциональной зоны."""
    ENTRANCE = "entrance"
    WET = "wet"
    LIVING = "living"


ROOM_TO_ZONE = {
    "hallway": ZoneType.ENTRANCE,
    "toilet": ZoneType.ENTRANCE,
    "bathroom": ZoneType.WET,
    "kitchen": ZoneType.WET,
    "living": ZoneType.LIVING,
    "bedroom": ZoneType.LIVING,
}


@dataclass
class FunctionalZone:
    zone_type: ZoneType
    rooms: List[Room] = field(default_factory=list)
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    
    @property
    def area(self) -> float:
        return sum(room.area for room in self.rooms)


class FunctionalLayoutGenerator:
    """
    Генератор планировок с функциональным зонированием.
    
    Алгоритм плотной упаковки:
    1. Сортируем комнаты по площади (убывание)
    2. Раскладываем в сетку (grid)
    3. Если не помещается — пробуем повернуть
    4. Масштабируем под размер зоны
    """
    
    def __init__(self, profile: Profile, 
                 entrance_depth_mm: float = 2500,
                 wet_zone_depth_mm: float = 3500,
                 corridor_width_mm: float = 1200):
        self.profile = profile
        self.entrance_depth = entrance_depth_mm / 1000
        self.wet_zone_depth = wet_zone_depth_mm / 1000
        self.corridor_width = corridor_width_mm / 1000
        self.zones: List[FunctionalZone] = []
    
    def generate(self, perimeter_width_mm: float, perimeter_height_mm: float) -> Layout:
        width_m = perimeter_width_mm / 1000
        height_m = perimeter_height_mm / 1000
        
        self._group_rooms_by_zone()
        self._calculate_zone_sizes(width_m, height_m)
        self._place_zones(width_m, height_m)
        rooms = self._place_rooms_in_zones_dense()
        
        corridor = self._add_corridor(width_m, height_m)
        if corridor:
            rooms.append(corridor)
        
        return Layout(
            rooms=rooms,
            apartment_area=sum(r.area for r in rooms),
            width=width_m,
            height=height_m,
        )
    
    def _group_rooms_by_zone(self):
        zone_rooms = {
            ZoneType.ENTRANCE: [],
            ZoneType.WET: [],
            ZoneType.LIVING: [],
        }
        
        for room_spec in self.profile.rooms:
            room_type = room_spec.get("type", "room")
            zone = ROOM_TO_ZONE.get(room_type, ZoneType.LIVING)
            
            min_area = room_spec.get("min_area", 5.0)
            preferred_area = room_spec.get("preferred_area", min_area * 1.2)
            
            room = Room(
                type=room_type,
                area=preferred_area,
                name=f"{room_type}_{len(zone_rooms[zone])}",
            )
            zone_rooms[zone].append(room)
        
        self.zones = [
            FunctionalZone(zone_type=ZoneType.ENTRANCE, rooms=zone_rooms[ZoneType.ENTRANCE]),
            FunctionalZone(zone_type=ZoneType.WET, rooms=zone_rooms[ZoneType.WET]),
            FunctionalZone(zone_type=ZoneType.LIVING, rooms=zone_rooms[ZoneType.LIVING]),
        ]
    
    def _calculate_zone_sizes(self, apartment_width: float, apartment_height: float):
        entrance_zone = self.zones[0]
        entrance_zone.width = apartment_width
        entrance_zone.height = self.entrance_depth
        
        wet_zone = self.zones[1]
        wet_zone.width = apartment_width
        wet_zone.height = self.wet_zone_depth
        
        living_zone = self.zones[2]
        living_zone.width = apartment_width
        living_zone.height = max(0, apartment_height - self.entrance_depth - self.wet_zone_depth - self.corridor_width)
    
    def _place_zones(self, apartment_width: float, apartment_height: float):
        self.zones[0].x = 0
        self.zones[0].y = 0
        
        self.zones[1].x = 0
        self.zones[1].y = self.entrance_depth
        
        self.zones[2].x = 0
        self.zones[2].y = self.entrance_depth + self.wet_zone_depth + self.corridor_width
    
    def _place_rooms_in_zones_dense(self) -> List[Room]:
        """
        Плотная упаковка комнат в зоне (grid-алгоритм с вращением).
        
        Алгоритм:
        1. Сортируем комнаты по площади (убывание)
        2. Рассчитываем grid (rows x cols) под зону
        3. Размещаем комнаты в ячейках grid
        4. Если не помещается — пробуем повернуть на 90°
        5. Масштабируем под размер зоны
        """
        placed_rooms = []
        
        for zone in self.zones:
            if not zone.rooms:
                continue
            
            # Сортировка по площади
            sorted_rooms = sorted(zone.rooms, key=lambda r: r.area, reverse=True)
            
            # Расчет grid
            n_rooms = len(sorted_rooms)
            cols = math.ceil(math.sqrt(n_rooms * zone.width / zone.height))
            rows = math.ceil(n_rooms / cols)
            
            # Размер ячейки
            cell_width = zone.width / cols
            cell_height = zone.height / rows
            
            # Размещение
            room_idx = 0
            for row in range(rows):
                for col in range(cols):
                    if room_idx >= len(sorted_rooms):
                        break
                    
                    room = sorted_rooms[room_idx]
                    
                    # Расчет размеров комнаты
                    room_aspect = 1.2
                    room_height = math.sqrt(room.area / room_aspect)
                    room_width = room_height * room_aspect
                    
                    # Проверка: помещается ли в ячейку
                    fits_normal = room_width <= cell_width and room_height <= cell_height
                    
                    # Если не помещается — пробуем повернуть
                    if not fits_normal:
                        room_width, room_height = room_height, room_width
                    
                    # Масштабирование под ячейку
                    scale_x = cell_width / room_width
                    scale_y = cell_height / room_height
                    scale = min(scale_x, scale_y, 1.5)  # Макс +50%
                    
                    room_width *= scale
                    room_height *= scale
                    
                    # Координаты
                    room.x = zone.x + col * cell_width
                    room.y = zone.y + row * cell_height
                    room.width = room_width
                    room.height = room_height
                    
                    placed_rooms.append(room)
                    room_idx += 1
        
        return placed_rooms
    
    def _add_corridor(self, apartment_width: float, apartment_height: float) -> Optional[Room]:
        corridor_area = apartment_width * self.corridor_width
        
        if corridor_area < 3.0:
            return None
        
        corridor = Room(
            type="hallway",
            area=corridor_area,
            x=0,
            y=self.entrance_depth + self.wet_zone_depth,
            width=apartment_width,
            height=self.corridor_width,
            name="corridor_main",
        )
        
        return corridor
