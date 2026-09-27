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
    ENTRANCE = "entrance"      # Входная зона
    WET = "wet"                # Мокрая зона
    LIVING = "living"          # Жилая зона


# Маппинг типов комнат в зоны
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
    """
    Функциональная зона с комнатами.
    
    Attributes:
        zone_type: Тип зоны
        rooms: Список комнат в зоне
        x, y: Координаты зоны (левый нижний угол)
        width, height: Размеры зоны
    """
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
    
    Алгоритм:
    1. Группируем комнаты по зонам
    2. Рассчитываем размеры зон
    3. Размещаем зоны в периметре (вход → мокрая → жилая)
    4. Внутри зон размещаем комнаты
    5. Добавляем коридор для связи
    """
    
    def __init__(self, profile: Profile, 
                 entrance_depth_mm: float = 2500,
                 wet_zone_depth_mm: float = 3500,
                 corridor_width_mm: float = 1200):
        """
        Args:
            profile: Профиль квартиры
            entrance_depth_mm: Глубина входной зоны (мм)
            wet_zone_depth_mm: Глубина мокрой зоны (мм)
            corridor_width_mm: Ширина коридора (мм)
        """
        self.profile = profile
        self.entrance_depth = entrance_depth_mm / 1000  # м
        self.wet_zone_depth = wet_zone_depth_mm / 1000  # м
        self.corridor_width = corridor_width_mm / 1000  # м
        
        self.zones: List[FunctionalZone] = []
    
    def generate(self, perimeter_width_mm: float, perimeter_height_mm: float) -> Layout:
        """
        Генерирует планировку с функциональным зонированием.
        
        Args:
            perimeter_width_mm: Ширина периметра в мм
            perimeter_height_mm: Высота периметра в мм
        
        Returns:
            Layout с размещёнными комнатами
        """
        # Конвертируем в метры
        width_m = perimeter_width_mm / 1000
        height_m = perimeter_height_mm / 1000
        
        # 1. Группировка по зонам
        self._group_rooms_by_zone()
        
        # 2. Расчёт размеров зон
        self._calculate_zone_sizes(width_m, height_m)
        
        # 3. Размещение зон
        self._place_zones(width_m, height_m)
        
        # 4. Размещение комнат внутри зон
        rooms = self._place_rooms_in_zones()
        
        # 5. Добавляем коридор
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
        """Группирует комнаты из профиля по зонам."""
        zone_rooms = {
            ZoneType.ENTRANCE: [],
            ZoneType.WET: [],
            ZoneType.LIVING: [],
        }
        
        for room_spec in self.profile.rooms:
            room_type = room_spec.get("type", "room")
            zone = ROOM_TO_ZONE.get(room_type, ZoneType.LIVING)
            
            # Создаём комнату (размеры рассчитаем позже)
            min_area = room_spec.get("min_area", 5.0)
            preferred_area = room_spec.get("preferred_area", min_area * 1.2)
            
            room = Room(
                type=room_type,
                area=preferred_area,
                name=f"{room_type}_{len(zone_rooms[zone])}",
            )
            zone_rooms[zone].append(room)
        
        # Создаём зоны
        self.zones = [
            FunctionalZone(zone_type=ZoneType.ENTRANCE, rooms=zone_rooms[ZoneType.ENTRANCE]),
            FunctionalZone(zone_type=ZoneType.WET, rooms=zone_rooms[ZoneType.WET]),
            FunctionalZone(zone_type=ZoneType.LIVING, rooms=zone_rooms[ZoneType.LIVING]),
        ]
    
    def _calculate_zone_sizes(self, apartment_width: float, apartment_height: float):
        """
        Рассчитывает размеры зон.
        
        Стратегия:
        - Входная зона: глубина фиксирована (entrance_depth), ширина = apartment_width
        - Мокрая зона: глубина фиксирована (wet_zone_depth), ширина = apartment_width
        - Жилая зона: остаток высоты
        """
        # Входная зона (внизу)
        entrance_zone = self.zones[0]
        entrance_zone.width = apartment_width
        entrance_zone.height = self.entrance_depth
        
        # Мокрая зона (посередине)
        wet_zone = self.zones[1]
        wet_zone.width = apartment_width
        wet_zone.height = self.wet_zone_depth
        
        # Жилая зона (вверху)
        living_zone = self.zones[2]
        living_zone.width = apartment_width
        living_zone.height = max(0, apartment_height - self.entrance_depth - self.wet_zone_depth - self.corridor_width)
    
    def _place_zones(self, apartment_width: float, apartment_height: float):
        """
        Размещает зоны в периметре.
        
        Схема:
        ┌─────────────────────┐
        │   Жилая зона        │  y = entrance + wet + corridor
        ├─────────────────────┤
        │   Коридор           │  y = entrance + wet
        ├─────────────────────┤
        │   Мокрая зона       │  y = entrance
        ├─────────────────────┤
        │   Входная зона      │  y = 0
        └─────────────────────┘
        """
        # Входная зона (y=0)
        self.zones[0].x = 0
        self.zones[0].y = 0
        
        # Мокрая зона
        self.zones[1].x = 0
        self.zones[1].y = self.entrance_depth
        
        # Жилая зона
        self.zones[2].x = 0
        self.zones[2].y = self.entrance_depth + self.wet_zone_depth + self.corridor_width
    
    def _place_rooms_in_zones(self) -> List[Room]:
        """
        Размещает комнаты внутри зон.
        
        Алгоритм для каждой зоны:
        1. Сортируем комнаты по площади (убывание)
        2. Рассчитываем размеры под зону
        3. Раскладываем слева-направо с переносом
        """
        placed_rooms = []
        
        for zone in self.zones:
            if not zone.rooms:
                continue
            
            # Сортировка по площади
            sorted_rooms = sorted(zone.rooms, key=lambda r: r.area, reverse=True)
            
            # Расчёт общей площади комнат в зоне
            total_room_area = sum(r.area for r in sorted_rooms)
            
            # Если площадь комнат больше зоны — масштабируем
            if total_room_area > zone.area:
                scale = math.sqrt(zone.area / total_room_area)
            else:
                scale = 1.0
            
            # Размещение shelf-алгоритмом
            x_offset = 0
            y_offset = 0
            row_height = 0
            
            for room in sorted_rooms:
                # Расчёт размеров с масштабом
                room_aspect = 1.2  # width/height
                room_area_scaled = room.area * scale
                
                room_height = math.sqrt(room_area_scaled / room_aspect)
                room_width = room_height * room_aspect
                
                # Проверка: если не помещается в строку — перенос
                if x_offset + room_width > zone.width:
                    x_offset = 0
                    y_offset += row_height
                    row_height = 0
                
                # Проверка: если не помещается по высоте — пропускаем
                if y_offset + room_height > zone.height:
                    print(f"Warning: Room {room.name} doesn't fit in zone {zone.zone_type.value}")
                    continue
                
                # Размещение
                room.x = zone.x + x_offset
                room.y = zone.y + y_offset
                room.width = room_width
                room.height = room_height
                
                placed_rooms.append(room)
                
                x_offset += room_width
                row_height = max(row_height, room_height)
        
        return placed_rooms
    
    def _add_corridor(self, apartment_width: float, apartment_height: float) -> Optional[Room]:
        """
        Добавляет коридор между зонами.
        
        Коридор идёт горизонтально между мокрой и жилой зоной.
        """
        corridor_area = apartment_width * self.corridor_width
        
        if corridor_area < 3.0:  # Минимальная площадь коридора
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
