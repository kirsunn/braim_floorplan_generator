"""
Экспорт планировки в JSON.

Полное описание планировки:
- Комнаты (тип, площадь, координаты, размеры)
- Двери (заготовки для будущей реализации)
- Окна (заготовки для будущей реализации)
- Общие параметры квартиры
"""

import json
from .generator import Layout


class JSONExporter:
    """Экспортёр планировки в JSON."""
    
    def __init__(self, indent: int = 2):
        self.indent = indent
    
    def export(self, layout: Layout, filepath: str) -> None:
        data = self._to_dict(layout)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=self.indent, ensure_ascii=False)
    
    def _to_dict(self, layout: Layout) -> dict:
        return {
            "apartment": {
                "area": layout.apartment_area,
                "width": layout.width,
                "height": layout.height,
            },
            "rooms": [room.to_dict() for room in layout.rooms],
            "doors": [],
            "windows": [],
            "metadata": {
                "generator": "BRAIM Floorplan Generator",
                "version": "0.1.0",
            },
        }
