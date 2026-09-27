# V1 Geometry Validation Specification

**Статус:** Draft  
**Версия:** 0.1.0  
**Дата:** 2026-09-27

## 1. Overview

V1 validation проверяет **геометрическую корректность** analytical layout:

- containment комнат внутри boundary
- отсутствие пересечений между комнатами
- отсутствие коллизий с forbidden zones
- соответствие declared area геометрической
- min dimension по типу комнаты
- proportion rules из ConstraintProfile

## 2. Правила V1

| Rule ID | Описание | Severity |
|---------|----------|----------|
| `GEOM-CONTAIN-001` | Все комнаты полностью внутри boundary | ERROR |
| `GEOM-OVERLAP-001` | Комнаты не пересекаются | ERROR |
| `GEOM-FORBIDDEN-001` | Нет коллизий с forbidden zones | ERROR |
| `GEOM-AREA-001` | \|declared_area - geometric_area\| ≤ tolerance | WARNING |
| `GEOM-MINDIM-001` | Min dimension ≥ минимума типа комнаты | ERROR |
| `GEOM-RATIO-001` | Aspect ratio ≤ profile.max_aspect_ratio | WARNING |

## 3. Geometry Model

```python
from shapely.geometry import Polygon, box

class AnalyticalRoom:
    polygon: Polygon  # room geometry
    declared_area_m2: float
    room_type: str
    id: str
```

## 4. Implementation Plan

### 4.1 Shapely Adapter

```python
def room_to_polygon(room: AnalyticalRoom) -> Polygon:
    return box(room.x_mm, room.y_mm, 
               room.x_mm + room.width_mm, 
               room.y_mm + room.height_mm)
```

### 4.2 Правила

```python
def check_containment(room: Polygon, boundary: Polygon) -> bool:
    return room.within(boundary)

def check_overlap(rooms: List[Polygon]) -> List[Tuple[int, int]]:
    overlaps = []
    for i, r1 in enumerate(rooms):
        for j, r2 in enumerate(rooms[i+1:], i+1):
            if r1.intersects(r2):
                overlaps.append((i, j))
    return overlaps

def check_forbidden(room: Polygon, zones: List[Polygon]) -> bool:
    for zone in zones:
        if room.intersects(zone):
            return False
    return True
```

## 5. Тесты

- 6 комнат, все внутри boundary → VALID
- 1 комната выходит за boundary → GEOM-CONTAIN-001 ERROR
- 2 комнаты пересекаются → GEOM-OVERLAP-001 ERROR
- Комната пересекает forbidden zone → GEOM-FORBIDDEN-001 ERROR

## 6. Связанные документы

- `docs/validation_v0.md` — V0 structural validation
- `docs/validation_v2_spec.md` — V2 functional/access (planned)