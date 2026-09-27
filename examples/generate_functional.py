"""
Генерация планировки с функциональным зонированием.

Зонирование:
- Входная зона: hallway, toilet
- Мокрая зона: bathroom, kitchen
- Жилая зона: living, bedroom

Запуск:
    python examples/generate_functional.py
"""

from braim_floorplan_generator import Profile
from braim_floorplan_generator.functional_layout import FunctionalLayoutGenerator
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os


def visualize_functional(layout, output_path=None):
    """Визуализация функциональной планировки."""
    fig, ax = plt.subplots(1, figsize=(12, 8))
    
    # Контур квартиры
    ax.add_patch(
        patches.Rectangle(
            (0, 0), layout.width, layout.height,
            linewidth=3, edgecolor='black', facecolor='none'
        )
    )
    
    # Цвета зон
    zone_colors = {
        "entrance": "#F5F5DC",   # Beige
        "wet": "#B0E0E6",        # PowderBlue
        "living": "#FFE4B5",     # Moccasin
        "hallway": "#D3D3D3",    # LightGray
    }
    
    # Комнаты
    for room in layout.rooms:
        color = zone_colors.get(room.type, "#CCCCCC")
        
        rect = patches.Rectangle(
            (room.x, room.y), room.width, room.height,
            linewidth=1, edgecolor='gray', facecolor=color,
            alpha=0.7
        )
        ax.add_patch(rect)
        
        # Подпись
        label = f"{room.name}\n{room.area:.1f} м²\n{room.width*1000:.0f} x {room.height*1000:.0f} мм"
        ax.text(
            room.x + room.width/2, room.y + room.height/2,
            label,
            ha='center', va='center',
            fontsize=8, fontweight='bold',
            color='black'
        )
    
    # Настройки
    ax.set_xlim(-1, layout.width + 1)
    ax.set_ylim(-1, layout.height + 1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Width (m)')
    ax.set_ylabel('Height (m)')
    ax.set_title(f'Functional Floorplan - {layout.apartment_area:.1f} m²')
    
    # Легенда зон
    legend_elements = [
        patches.Patch(facecolor=zone_colors["entrance"], label='Entrance (hallway, toilet)'),
        patches.Patch(facecolor=zone_colors["wet"], label='Wet (bathroom, kitchen)'),
        patches.Patch(facecolor=zone_colors["living"], label='Living (living, bedroom)'),
        patches.Patch(facecolor=zone_colors["hallway"], label='Corridor'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {output_path}")
    else:
        plt.show()


def main():
    # Профиль 2-комнатной квартиры
    profile = Profile.from_dict({
        "apartment_area": 60.0,
        "rooms": [
            {"type": "toilet", "min_area": 1.5, "preferred_area": 2.0},
            {"type": "bathroom", "min_area": 3.0, "preferred_area": 4.0},
            {"type": "kitchen", "min_area": 8.0, "preferred_area": 10.0},
            {"type": "living", "min_area": 14.0, "preferred_area": 18.0},
            {"type": "bedroom", "min_area": 8.0, "preferred_area": 12.0},
        ],
    })
    
    # Периметр в осях (мм)
    perimeter_width_mm = 10000  # 10 м
    perimeter_height_mm = 7000  # 7 м
    
    print("=== Functional Layout Generator ===")
    print(f"Perimeter: {perimeter_width_mm/1000:.1f} x {perimeter_height_mm/1000:.1f} м")
    print(f"Rooms: {len(profile.rooms)}")
    print()
    
    # Генерация
    generator = FunctionalLayoutGenerator(
        profile,
        entrance_depth_mm=2000,    # 2 м входная зона
        wet_zone_depth_mm=3000,    # 3 м мокрая зона
        corridor_width_mm=1200,    # 1.2 м коридор
    )
    
    layout = generator.generate(perimeter_width_mm, perimeter_height_mm)
    
    print(f"Generated {len(layout.rooms)} rooms:")
    for room in layout.rooms:
        print(f"  {room.name:15} {room.type:10} {room.area:5.1f} м²  {room.width*1000:6.0f} x {room.height*1000:6.0f} мм  @ ({room.x:.2f}, {room.y:.2f})")
    print()
    
    # Визуализация
    output_image = "output/functional_floorplan.png"
    visualize_functional(layout, output_path=output_image)
    print(f"Visualization saved to {output_image}")


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    main()
