"""
3D-визуализация планировки через matplotlib mplot3d.

Запуск:
    python examples/visualize_3d.py output/apartment.json

Или с примером:
    python examples/visualize_3d.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import json
import sys
import os


def load_layout(filepath: str) -> dict:
    """Загружает планировку из JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def create_room_3d(x: float, y: float, width: float, height: float, 
                   wall_height: float = 2.8) -> list:
    """
    Создаёт 3D-геометрию комнаты (стены).
    
    Args:
        x, y: Координаты левого нижнего угла (м)
        width, height: Размеры комнаты (м)
        wall_height: Высота стен (м)
    
    Returns:
        Список вершин для Poly3DCollection
    """
    # Вершины комнаты (8 углов)
    vertices = [
        # Пол (z=0)
        (x, y, 0),
        (x + width, y, 0),
        (x + width, y + height, 0),
        (x, y + height, 0),
        # Потолок (z=wall_height)
        (x, y, wall_height),
        (x + width, y, wall_height),
        (x + width, y + height, wall_height),
        (x, y + height, wall_height),
    ]
    
    # Грани (индексы вершин)
    faces = [
        # Пол
        [0, 1, 2, 3],
        # Потолок
        [4, 5, 6, 7],
        # Стены
        [0, 1, 5, 4],  # Передняя
        [2, 3, 7, 6],  # Задняя
        [1, 2, 6, 5],  # Правая
        [3, 0, 4, 7],  # Левая
    ]
    
    return vertices, faces


def visualize_3d(layout: dict, output_path: str = None, 
                 wall_height: float = 2.8, show_floor: bool = True):
    """
    Визуализирует планировку в 3D.
    
    Args:
        layout: Словарь с планировкой (из JSON)
        output_path: Путь для сохранения изображения (опционально)
        wall_height: Высота стен (м)
        show_floor: Показывать ли пол
    """
    rooms = layout.get("rooms", [])
    apartment = layout.get("apartment", {})
    
    # Создание фигуры
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Цвета для разных типов комнат
    colors = {
        "living": "#FFE4B5",      # Moccasin
        "bedroom": "#B0E0E6",     # PowderBlue
        "kitchen": "#FFDAB9",     # PeachPuff
        "bathroom": "#E6E6FA",    # Lavender
        "toilet": "#F0E68C",      # Khaki
        "hallway": "#F5F5DC",     # Beige
    }
    
    # Отрисовка комнат в 3D
    for room in rooms:
        x = room.get("x", 0)
        y = room.get("y", 0)
        w = room.get("width", 0)
        h = room.get("height", 0)
        room_type = room.get("type", "room")
        area = room.get("area", 0)
        name = room.get("name", "")
        
        color = colors.get(room_type, "#CCCCCC")
        
        if show_floor:
            # Пол комнаты
            floor_verts = [
                [x, y, 0],
                [x + w, y, 0],
                [x + w, y + h, 0],
                [x, y + h, 0],
            ]
            floor = patches.Polygon(floor_verts, facecolor=color, alpha=0.5)
            ax.add_patch(floor)
        
        # Стены (линии)
        # Вертикальные линии по углам
        for corner_x, corner_y in [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]:
            ax.plot([corner_x, corner_x], [corner_y, corner_y], 
                   [0, wall_height], color='gray', linewidth=1.5, alpha=0.7)
        
        # Горизонтальные линии (верх стен)
        top_edges = [
            [(x, y, wall_height), (x + w, y, wall_height)],
            [(x + w, y, wall_height), (x + w, y + h, wall_height)],
            [(x + w, y + h, wall_height), (x, y + h, wall_height)],
            [(x, y + h, wall_height), (x, y, wall_height)],
        ]
        for edge in top_edges:
            ax.plot(*zip(*edge), color='gray', linewidth=1.5, alpha=0.7)
        
        # Подпись (над комнатой)
        label = f"{name}\n{area:.1f} м²"
        ax.text(x + w/2, y + h/2, wall_height + 0.3,
               label, ha='center', va='center',
               fontsize=9, fontweight='bold', color='black')
    
    # Контур квартиры
    width = apartment.get("width", 0)
    height = apartment.get("height", 0)
    
    if width > 0 and height > 0:
        # Пол
        if show_floor:
            apartment_floor = patches.Polygon(
                [[0, 0], [width, 0], [width, height], [0, height]],
                facecolor='none', edgecolor='black', linewidth=2
            )
            ax.add_patch(apartment_floor)
        
        # Вертикальные линии по углам
        for corner_x, corner_y in [(0, 0), (width, 0), (width, height), (0, height)]:
            ax.plot([corner_x, corner_x], [corner_y, corner_y], 
                   [0, wall_height + 0.5], color='black', linewidth=2)
    
    # Настройки
    ax.set_xlim(-1, width + 1)
    ax.set_ylim(-1, height + 1)
    ax.set_zlim(0, wall_height + 1)
    ax.set_xlabel('Width (m)')
    ax.set_ylabel('Height (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title(f'3D Floorplan - {apartment.get("area", 0):.1f} m²')
    
    # Угол обзора
    ax.view_init(elev=30, azim=45)
    
    plt.tight_layout()
    
    # Сохранение или показ
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {output_path}")
    else:
        plt.show()


def main():
    # Путь к JSON по умолчанию
    default_json = "output/apartment.json"
    
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = default_json
    
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        print(f"Run 'python examples/generate_apartment.py' first to create {default_json}")
        sys.exit(1)
    
    # Загрузка
    print(f"Loading {json_path}...")
    layout = load_layout(json_path)
    
    # Визуализация
    output_image = "output/floorplan_3d.png"
    visualize_3d(layout, output_path=output_image, wall_height=2.8, show_floor=True)
    print(f"3D visualization saved to {output_image}")


if __name__ == "__main__":
    main()
