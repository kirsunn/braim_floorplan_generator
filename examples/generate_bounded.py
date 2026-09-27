"""
Генерация планировки в ограниченном периметре (в осях дома).

Поддерживает:
- Прямоугольный периметр
- Ломаная фигура (полигон)

Запуск:
    python examples/generate_bounded.py

Пример профиля с периметром:
{
    "apartment_area": 60,
    "perimeter": {
        "type": "rectangle",  // или "polygon"
        "width": 12000,       // мм
        "height": 8000        // мм
    },
    "rooms": [...]
}
"""

from braim_floorplan_generator import FloorplanGenerator, Profile, Layout, Room
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import os


def generate_in_rectangle(width_mm: float, height_mm: float, 
                          room_areas: list, min_dimension_mm: float = 1200):
    """
    Генерирует планировку в прямоугольном периметре.
    
    Args:
        width_mm: Ширина периметра в мм
        height_mm: Высота периметра в мм
        room_areas: Список площадей комнат в м²
        min_dimension_mm: Минимальный размер комнаты в мм
    
    Returns:
        Layout с размещёнными комнатами
    """
    # Конвертируем в метры
    width_m = width_mm / 1000
    height_m = height_mm / 1000
    
    # Создаём профиль
    rooms = []
    for i, area in enumerate(room_areas):
        rooms.append({
            "type": "room",
            "min_area": area,
            "preferred_area": area * 1.1,
        })
    
    profile = Profile(
        apartment_area=sum(room_areas),
        rooms=rooms,
    )
    
    # Генерация
    generator = FloorplanGenerator(profile)
    layout = generator.generate()
    
    # Масштабирование под периметр
    if layout.width > 0:
        scale_x = width_m / layout.width
    else:
        scale_x = 1.0
    
    if layout.height > 0:
        scale_y = height_m / layout.height
    else:
        scale_y = 1.0
    
    # Используем минимальный масштаб, чтобы всё поместилось
    scale = min(scale_x, scale_y) * 0.95  # 5% запас
    
    # Применяем масштабирование
    scaled_rooms = []
    for room in layout.rooms:
        scaled_room = Room(
            type=room.type,
            area=room.area * scale * scale,  # Площадь масштабируется квадратом
            x=room.x * scale,
            y=room.y * scale,
            width=room.width * scale,
            height=room.height * scale,
            name=room.name,
        )
        scaled_rooms.append(scaled_room)
    
    return Layout(
        rooms=scaled_rooms,
        apartment_area=sum(r.area for r in scaled_rooms),
        width=width_m,
        height=height_m,
    )


def visualize_bounded(layout: Layout, perimeter_type: str = "rectangle",
                      perimeter_points: list = None, output_path: str = None):
    """
    Визуализирует планировку в периметре.
    
    Args:
        layout: Планировка
        perimeter_type: "rectangle" или "polygon"
        perimeter_points: Точки периметра для polygon [(x, y), ...]
        output_path: Путь для сохранения
    """
    fig, ax = plt.subplots(1, figsize=(12, 8))
    
    # Периметр
    if perimeter_type == "rectangle":
        ax.add_patch(
            patches.Rectangle(
                (0, 0), layout.width, layout.height,
                linewidth=3, edgecolor='red', facecolor='none',
                label='Perimeter (axes)'
            )
        )
    elif perimeter_type == "polygon" and perimeter_points:
        polygon = patches.Polygon(
            perimeter_points, closed=True,
            linewidth=3, edgecolor='red', facecolor='none',
            label='Perimeter (axes)'
        )
        ax.add_patch(polygon)
    
    # Цвета
    colors = {
        "room": "#B0E0E6",
        "living": "#FFE4B5",
        "bedroom": "#B0E0E6",
        "kitchen": "#FFDAB9",
        "bathroom": "#E6E6FA",
        "toilet": "#F0E68C",
        "hallway": "#F5F5DC",
    }
    
    # Комнаты
    for room in layout.rooms:
        x = room.x
        y = room.y
        w = room.width
        h = room.height
        
        color = colors.get(room.type, "#CCCCCC")
        
        rect = patches.Rectangle(
            (x, y), w, h,
            linewidth=1, edgecolor='gray', facecolor=color,
            alpha=0.7
        )
        ax.add_patch(rect)
        
        # Подпись
        label = f"{room.name}\n{room.area:.1f} м²\n{w*1000:.0f} x {h*1000:.0f} мм"
        ax.text(
            x + w/2, y + h/2,
            label,
            ha='center', va='center',
            fontsize=8, fontweight='bold',
            color='black'
        )
    
    # Настройки
    if perimeter_type == "rectangle":
        ax.set_xlim(-1, layout.width + 1)
        ax.set_ylim(-1, layout.height + 1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Width (m)')
    ax.set_ylabel('Height (m)')
    ax.set_title(f'Floorplan in Bounded Perimeter - {layout.apartment_area:.1f} m²')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {output_path}")
    else:
        plt.show()


def main():
    # Пример 1: Прямоугольный периметр 12x8 м (в осях)
    print("=== Example 1: Rectangle perimeter 12x8 m ===")
    
    width_mm = 12000  # 12 м
    height_mm = 8000  # 8 м
    
    # Площади комнат (м²)
    room_areas = [18, 14, 10, 5, 3, 4]  # living, bedroom, kitchen, bathroom, toilet, hallway
    
    layout = generate_in_rectangle(width_mm, height_mm, room_areas)
    
    print(f"Perimeter: {width_mm/1000:.1f} x {height_mm/1000:.1f} м")
    print(f"Generated {len(layout.rooms)} rooms:")
    for room in layout.rooms:
        print(f"  {room.name}: {room.area:.1f} м², {room.width*1000:.0f} x {room.height*1000:.0f} мм")
    
    # Визуализация
    output_image = "output/bounded_floorplan.png"
    visualize_bounded(layout, perimeter_type="rectangle", output_path=output_image)
    print(f"Visualization saved to {output_image}\n")
    
    # Пример 2: L-образный периметр (полигон)
    print("=== Example 2: L-shaped perimeter ===")
    
    # Точки периметра (мм → м)
    perimeter_points_m = [
        (0, 0),
        (15, 0),
        (15, 6),
        (8, 6),
        (8, 10),
        (0, 10),
    ]
    
    # Для простоты используем bounding box
    max_x = max(p[0] for p in perimeter_points_m)
    max_y = max(p[1] for p in perimeter_points_m)
    
    layout2 = generate_in_rectangle(max_x * 1000, max_y * 1000, room_areas)
    
    output_image2 = "output/lshape_floorplan.png"
    visualize_bounded(layout2, perimeter_type="polygon", 
                     perimeter_points=perimeter_points_m, output_path=output_image2)
    print(f"L-shaped visualization saved to {output_image2}")


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    main()
