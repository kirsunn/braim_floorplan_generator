"""
Экспорт планировки в SVG.

Ручная отрисовка 2D-плана с выводом:
- Контуров комнат
- Названий комнат
- Площадей
"""

from .generator import Layout, Room


class SVGExporter:
    """Экспортёр планировки в SVG."""
    
    def __init__(self, scale: float = 50.0, margin: float = 20.0):
        self.scale = scale
        self.margin = margin
    
    def export(self, layout: Layout, filepath: str) -> None:
        if not layout.rooms:
            svg_content = self._create_empty_svg()
        else:
            svg_content = self._create_svg(layout)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
    
    def _create_svg(self, layout: Layout) -> str:
        width_px = layout.width * self.scale + 2 * self.margin
        height_px = layout.height * self.scale + 2 * self.margin
        
        svg_parts = []
        
        svg_parts.append(f'<?xml version="1.0" encoding="UTF-8"?>')
        svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px:.1f}" height="{height_px:.1f}" viewBox="0 0 {width_px:.1f} {height_px:.1f}">')
        
        svg_parts.append(f'  <rect x="0" y="0" width="{width_px:.1f}" height="{height_px:.1f}" fill="white"/>')
        
        apartment_x = self.margin
        apartment_y = self.margin
        apartment_w = layout.width * self.scale
        apartment_h = layout.height * self.scale
        
        svg_parts.append(f'  <rect x="{apartment_x:.1f}" y="{apartment_y:.1f}" width="{apartment_w:.1f}" height="{apartment_h:.1f}" fill="none" stroke="black" stroke-width="2"/>')
        
        for room in layout.rooms:
            room_svg = self._draw_room(room)
            svg_parts.append(room_svg)
        
        svg_parts.append(f'  <text x="{self.margin + 10:.1f}" y="{self.margin + 20:.1f}" font-size="14" fill="gray">')
        svg_parts.append(f'    Apartment: {layout.apartment_area:.1f} m²')
        svg_parts.append(f'  </text>')
        
        svg_parts.append('</svg>')
        
        return "\n".join(svg_parts)
    
    def _draw_room(self, room: Room) -> str:
        room_x = self.margin + room.x * self.scale
        room_y = self.margin + room.y * self.scale
        room_w = room.width * self.scale
        room_h = room.height * self.scale
        
        parts = []
        
        parts.append(f'  <rect x="{room_x:.1f}" y="{room_y:.1f}" width="{room_w:.1f}" height="{room_h:.1f}" fill="lightblue" stroke="gray" stroke-width="1" opacity="0.5"/>')
        
        center_x = room_x + room_w / 2
        center_y = room_y + room_h / 2
        
        parts.append(f'  <text x="{center_x:.1f}" y="{center_y:.1f}" font-size="12" fill="black" text-anchor="middle" dominant-baseline="middle">')
        parts.append(f'    {room.name}')
        parts.append(f'  </text>')
        
        area_y = center_y + 15
        parts.append(f'  <text x="{center_x:.1f}" y="{area_y:.1f}" font-size="10" fill="darkgray" text-anchor="middle">')
        parts.append(f'    {room.area:.1f} m²')
        parts.append(f'  </text>')
        
        return "\n".join(parts)
    
    def _create_empty_svg(self) -> str:
        width_px = 400 + 2 * self.margin
        height_px = 300 + 2 * self.margin
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width_px:.1f}" height="{height_px:.1f}" viewBox="0 0 {width_px:.1f} {height_px:.1f}">
  <rect x="0" y="0" width="{width_px:.1f}" height="{height_px:.1f}" fill="white"/>
  <text x="{self.margin + 10:.1f}" y="{self.margin + 30:.1f}" font-size="14" fill="gray">
    No rooms generated
  </text>
</svg>'''
