"""
Пример загрузки и использования JSON конфига.

Запуск:
    python examples/load_config.py
"""

from braim_floorplan_generator.config import LayoutConfig
import json


def main():
    # Загрузка конфига
    config_path = "configs/2room_linear.json"
    
    print(f"Loading config from {config_path}...")
    config = LayoutConfig.from_json_file(config_path)
    
    # Вывод информации
    print(f"\n=== {config.name} ===")
    print(f"Description: {config.perimeter.type} perimeter")
    print(f"Perimeter: {config.perimeter.width_mm/1000:.1f} x {config.perimeter.height_mm/1000:.1f} м")
    print(f"Functional scheme: {config.functional_scheme}")
    print(f"Zones: {len(config.zones)}")
    print(f"Rooms: {len(config.rooms)}")
    
    # Зоны
    print("\n=== Zones ===")
    for zone_name, zone_config in config.zones.items():
        print(f"  {zone_name}: {zone_config.position}, depth={zone_config.depth_mm/1000:.1f} м")
    
    # Комнаты
    print("\n=== Rooms ===")
    for room in config.rooms:
        zone_str = f" ({room.zone})" if room.zone else ""
        print(f"  {room.type}{zone_str}: {room.min_area}-{room.preferred_area} м²")
    
    # Ограничения
    print("\n=== Constraints ===")
    print(f"  Corridor width: {config.constraints.min_corridor_width_mm} мм")
    print(f"  Kitchen near bathroom: {config.constraints.kitchen_near_bathroom}")
    print(f"  Bedroom quiet zone: {config.constraints.bedroom_quiet_zone}")
    print(f"  Max aspect ratio: {config.constraints.max_aspect_ratio}")
    
    # Сохранение обратно в JSON
    output_path = "output/config_test.json"
    config.save_json(output_path)
    print(f"\nSaved test config to {output_path}")


if __name__ == "__main__":
    main()
