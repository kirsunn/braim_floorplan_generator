"""
Визуализация планировки через matplotlib.

Запуск:
    python examples/visualize.py output/apartment.json

Или с примером:
    python examples/visualize.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import sys
import os


def load_layout(filepath: str) -> dict:
    """Загружает планировку из JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def visualize(layout: dict, output_path: str = None):
    """
    Визуализирует планировку.
    
    Args:
        layout: Словарь с планировкой (из JSON)
        output_path: Путь для сохранения изображения (опционально)
    """
    rooms = layout.get("rooms", [])
    apartment = layout.get("apartment", {})
    
    # Создание фигуры
    fig, ax = plt.subplots(1, figsize=(12, 8))
    
    # Контур квартиры
    width = apartment.get("width", 0)
    height = apartment.get("height", 0)
    
    if width > 0 and height > 0:
        ax.add_patch(
            patches.Rectangle(
                (0, 0), width, height,
                linewidth=3, edgecolor='black', facecolor='none',
                label='Apartment boundary'
            )
        )
    
    # Цвета для разных типов комнат
    colors = {
        "living": "#FFE4B5",      # Moccasin
        "bedroom": "#B0E0E6",     # PowderBlue
        "kitchen": "#FFDAB9",     # PeachPuff
        "bathroom": "#E6E6FA",    # Lavender
        "toilet": "#F0E68C",      # Khaki
        "hallway": "#F5F5DC",     # Beige
    }
    
    # Отрисовка комнат
    for room in rooms:
        x = room.get("x", 0)
        y = room.get("y", 0)
        w = room.get("width", 0)
        h = room.get("height", 0)
        room_type = room.get("type", "room")
        area = room.get("area", 0)
        name = room.get("name", "")
        
        color = colors.get(room_type, "#CCCCCC")
        
        # Прямоугольник комнаты
        rect = patches.Rectangle(
            (x, y), w, h,
            linewidth=1, edgecolor='gray', facecolor=color,
            alpha=0.7
        )
        ax.add_patch(rect)
        
        # Подпись
        label = f"{name}\n{area:.1f} м²"
        ax.text(
            x + w/2, y + h/2,
            label,
            ha='center', va='center',
            fontsize=10, fontweight='bold',
            color='black'
        )
    
    # Настройки
    ax.set_xlim(-1, width + 1)
    ax.set_ylim(-1, height + 1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Width (m)')
    ax.set_ylabel('Height (m)')
    ax.set_title(f'Floorplan - {apartment.get("area", 0):.1f} m²')
    
    # Легенда
    legend_elements = [
        patches.Patch(facecolor=colors.get(t, "#CCCCCC"), label=t.capitalize())
        for t in ["living", "bedroom", "kitchen", "bathroom", "toilet", "hallway"]
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
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
    output_image = "output/floorplan.png"
    visualize(layout, output_path=output_image)
    print(f"Visualization saved to {output_image}")


if __name__ == "__main__":
    main()
