"""
Пример использования BRAIM Floorplan Generator.

Генерирует планировку 2-комнатной квартиры и экспортирует в IFC, SVG, JSON.
"""

from braim_floorplan_generator import (
    FloorplanGenerator,
    Profile,
    IFCExporter,
    SVGExporter,
    JSONExporter,
    ErgonomicsChecker,
    PlanValidator,
)
import os


def main():
    profile = Profile.from_dict({
        "apartment_area": 60.0,
        "rooms": [
            {"type": "living", "min_area": 14.0, "preferred_area": 18.0, "preferred_aspect_ratio": 1.2},
            {"type": "bedroom", "min_area": 8.0, "preferred_area": 12.0, "preferred_aspect_ratio": 1.3},
            {"type": "kitchen", "min_area": 8.0, "preferred_area": 10.0, "preferred_aspect_ratio": 1.1},
            {"type": "bathroom", "min_area": 3.0, "preferred_area": 4.0, "preferred_aspect_ratio": 1.0},
            {"type": "toilet", "min_area": 1.5, "preferred_area": 2.0, "preferred_aspect_ratio": 1.0},
            {"type": "hallway", "min_area": 3.0, "preferred_area": 5.0, "preferred_aspect_ratio": 2.0},
        ],
    })
    
    print("Генерация планировки...")
    generator = FloorplanGenerator(profile)
    layout = generator.generate()
    
    print(f"Создано комнат: {len(layout.rooms)}")
    print(f"Размеры квартиры: {layout.width:.2f} x {layout.height:.2f} м")
    print(f"Общая площадь: {layout.apartment_area:.1f} м²")
    print()
    
    print("Комнаты:")
    for room in layout.rooms:
        print(f"  {room.name:15} {room.type:10} {room.area:6.1f} м²  {room.width:5.2f} x {room.height:5.2f} м")
    print()
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Экспорт в {output_dir}/...")
    
    IFCExporter().export(layout, os.path.join(output_dir, "apartment.ifc"))
    print(f"  ✓ apartment.ifc")
    
    SVGExporter().export(layout, os.path.join(output_dir, "apartment.svg"))
    print(f"  ✓ apartment.svg")
    
    JSONExporter().export(layout, os.path.join(output_dir, "apartment.json"))
    print(f"  ✓ apartment.json")
    
    print()
    print("Проверка эргономики...")
    ergonomics = ErgonomicsChecker()
    print(ergonomics.summary(layout))
    
    print()
    print("IDS-валидация (упрощённая)...")
    validator = PlanValidator()
    
    validator.add_rule({
        "name": "Min area for living",
        "entity": "IfcSpace",
        "property": "Pset_SpaceCommon.NetFloorArea",
        "operator": ">=",
        "value": 14.0,
        "filter": {"type": "living"},
    })
    validator.add_rule({
        "name": "Min area for bedroom",
        "entity": "IfcSpace",
        "property": "Pset_SpaceCommon.NetFloorArea",
        "operator": ">=",
        "value": 8.0,
        "filter": {"type": "bedroom"},
    })
    validator.add_rule({
        "name": "Min area for kitchen",
        "entity": "IfcSpace",
        "property": "Pset_SpaceCommon.NetFloorArea",
        "operator": ">=",
        "value": 8.0,
        "filter": {"type": "kitchen"},
    })
    validator.add_rule({
        "name": "Min area for bathroom",
        "entity": "IfcSpace",
        "property": "Pset_SpaceCommon.NetFloorArea",
        "operator": ">=",
        "value": 3.0,
        "filter": {"type": "bathroom"},
    })
    
    report = validator.validate_layout(layout)
    print(report.summary())
    
    import json
    with open(os.path.join(output_dir, "validation_report.json"), "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"  ✓ validation_report.json")
    
    print()
    print("Готово!")


if __name__ == "__main__":
    main()
