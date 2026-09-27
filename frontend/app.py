"""
PyScript app for BRAIM Floorplan Generator frontend.
"""

import json
from js import document
from braim_floorplan_generator import (
    FloorplanGenerator,
    Profile,
    SVGExporter,
    ErgonomicsChecker,
)


def run_script():
    """Execute user script and visualize."""
    script = document.getElementById("script-input").value
    output_div = document.getElementById("output")
    status_div = document.getElementById("status")
    
    try:
        output_div.innerHTML = "Running..."
        
        # Execute script
        exec(script)
        
        # Load generated JSON
        with open("output/apartment.json", "r") as f:
            layout_data = json.load(f)
        
        # Visualize
        visualize(layout_data)
        
        output_div.innerHTML = "✓ Generation complete!"
        status_div.innerHTML = '<div class="status success">Success!</div>'
        
    except Exception as e:
        output_div.innerHTML = f"✗ Error: {str(e)}"
        status_div.innerHTML = f'<div class="status error">Error: {str(e)}</div>'


def visualize(layout_data: dict):
    """Draw 2D floorplan in SVG."""
    svg = document.getElementById("visualization")
    rooms = layout_data.get("rooms", [])
    apartment = layout_data.get("apartment", {})
    
    width = apartment.get("width", 10)
    height = apartment.get("height", 7)
    
    # Scale to fit SVG
    scale = min(750 / width, 550 / height)
    margin = 25
    
    # Clear SVG
    svg.innerHTML = ""
    
    # Apartment boundary
    boundary = f'''
        <rect x="{margin}" y="{margin}" 
              width="{width * scale}" height="{height * scale}"
              fill="none" stroke="black" stroke-width="3"/>
    '''
    svg.innerHTML += boundary
    
    # Colors
    colors = {
        "living": "#FFE4B5",
        "bedroom": "#B0E0E6",
        "kitchen": "#FFDAB9",
        "bathroom": "#E6E6FA",
        "toilet": "#F0E68C",
        "hallway": "#F5F5DC",
    }
    
    # Rooms
    for room in rooms:
        x = margin + room["x"] * scale
        y = margin + room["y"] * scale
        w = room["width"] * scale
        h = room["height"] * scale
        
        color = colors.get(room["type"], "#CCCCCC")
        
        room_svg = f'''
            <rect x="{x}" y="{y}" width="{w}" height="{h}"
                  fill="{color}" stroke="gray" stroke-width="1" opacity="0.7"/>
            <text x="{x + w/2}" y="{y + h/2}" 
                  text-anchor="middle" dominant-baseline="middle"
                  font-size="12" font-weight="bold" fill="black">
                {room["name"]}\n{room["area"]:.1f} m²
            </text>
        '''
        svg.innerHTML += room_svg
    
    # Title
    title = f'''
        <text x="{margin + 10}" y="{margin + 20}" 
              font-size="14" fill="gray">
            Apartment: {apartment.get("area", 0):.1f} m²
        </text>
    '''
    svg.innerHTML += title


def load_example():
    """Load example script."""
    example = '''from braim_floorplan_generator import (
    FloorplanGenerator,
    Profile,
    IFCExporter,
    SVGExporter,
    JSONExporter,
    ErgonomicsChecker,
    PlanValidator,
)
import os

profile = Profile.from_dict({
    "apartment_area": 60.0,
    "rooms": [
        {"type": "living", "min_area": 14.0, "preferred_area": 18.0},
        {"type": "bedroom", "min_area": 8.0, "preferred_area": 12.0},
        {"type": "kitchen", "min_area": 8.0, "preferred_area": 10.0},
        {"type": "bathroom", "min_area": 3.0, "preferred_area": 4.0},
        {"type": "toilet", "min_area": 1.5, "preferred_area": 2.0},
        {"type": "hallway", "min_area": 3.0, "preferred_area": 5.0},
    ],
})

generator = FloorplanGenerator(profile)
layout = generator.generate()

print(f"Generated {len(layout.rooms)} rooms")
print(f"Apartment: {layout.width:.2f} x {layout.height:.2f} m")

for room in layout.rooms:
    print(f"  {room.name}: {room.area:.1f} m², {room.width*1000:.0f} x {room.height*1000:.0f} mm")

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

IFCExporter().export(layout, os.path.join(output_dir, "apartment.ifc"))
SVGExporter().export(layout, os.path.join(output_dir, "apartment.svg"))
JSONExporter().export(layout, os.path.join(output_dir, "apartment.json"))

print("Export complete!")
'''
    document.getElementById("script-input").value = example


# Bind functions to window
import js
js.window.runScript = run_script
js.window.loadExample = load_example
