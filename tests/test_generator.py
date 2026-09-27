"""
Unit-тесты генератора планировок.
"""

import pytest
from braim_floorplan_generator import FloorplanGenerator, Profile, Room


class TestProfile:
    """Тесты профиля."""
    
    def test_from_dict(self):
        data = {
            "apartment_area": 60.0,
            "rooms": [
                {"type": "living", "min_area": 14.0, "preferred_area": 18.0},
                {"type": "bedroom", "min_area": 8.0, "preferred_area": 12.0},
            ],
        }
        profile = Profile.from_dict(data)
        
        assert profile.apartment_area == 60.0
        assert len(profile.rooms) == 2
        assert profile.rooms[0]["type"] == "living"
    
    def test_from_json_file(self, tmp_path):
        import json
        filepath = tmp_path / "profile.json"
        data = {
            "apartment_area": 50.0,
            "rooms": [{"type": "kitchen", "min_area": 8.0}],
        }
        with open(filepath, "w") as f:
            json.dump(data, f)
        
        profile = Profile.from_json_file(str(filepath))
        
        assert profile.apartment_area == 50.0
        assert len(profile.rooms) == 1


class TestRoom:
    """Тесты комнаты."""
    
    def test_aspect_ratio(self):
        room = Room(type="living", area=20.0, width=5.0, height=4.0)
        assert room.aspect_ratio == 1.25
    
    def test_aspect_ratio_zero_height(self):
        room = Room(type="living", area=20.0, width=5.0, height=0.0)
        assert room.aspect_ratio == 0.0
    
    def test_to_dict(self):
        room = Room(type="bedroom", area=12.0, x=1.0, y=2.0, width=4.0, height=3.0, name="Bed1")
        d = room.to_dict()
        
        assert d["type"] == "bedroom"
        assert d["area"] == 12.0
        assert d["x"] == 1.0
        assert d["name"] == "Bed1"


class TestFloorplanGenerator:
    """Тесты генератора."""
    
    def test_generate_empty_profile(self):
        profile = Profile(apartment_area=50.0, rooms=[])
        generator = FloorplanGenerator(profile)
        layout = generator.generate()
        
        assert len(layout.rooms) == 0
        assert layout.width == 0.0
        assert layout.height == 0.0
    
    def test_generate_single_room(self):
        profile = Profile(
            apartment_area=20.0,
            rooms=[{"type": "living", "min_area": 14.0, "preferred_area": 18.0}],
        )
        generator = FloorplanGenerator(profile)
        layout = generator.generate()
        
        assert len(layout.rooms) == 1
        room = layout.rooms[0]
        assert room.type == "living"
        assert room.area >= 14.0
    
    def test_generate_multiple_rooms(self):
        profile = Profile(
            apartment_area=60.0,
            rooms=[
                {"type": "living", "min_area": 14.0},
                {"type": "bedroom", "min_area": 8.0},
                {"type": "kitchen", "min_area": 8.0},
                {"type": "bathroom", "min_area": 3.0},
            ],
        )
        generator = FloorplanGenerator(profile)
        layout = generator.generate()
        
        assert len(layout.rooms) == 4
        
        for room in layout.rooms:
            assert room.x >= 0.0
            assert room.y >= 0.0
            assert room.width > 0.0
            assert room.height > 0.0
    
    def test_room_areas_sum(self):
        total_min_area = 14.0 + 8.0 + 8.0 + 3.0 + 1.5 + 3.0
        profile = Profile(
            apartment_area=total_min_area,
            rooms=[
                {"type": "living", "min_area": 14.0},
                {"type": "bedroom", "min_area": 8.0},
                {"type": "kitchen", "min_area": 8.0},
                {"type": "bathroom", "min_area": 3.0},
                {"type": "toilet", "min_area": 1.5},
                {"type": "hallway", "min_area": 3.0},
            ],
        )
        generator = FloorplanGenerator(profile)
        layout = generator.generate()
        
        total_area = sum(room.area for room in layout.rooms)
        assert abs(total_area - total_min_area) < 1.0
    
    def test_max_aspect_ratio(self):
        profile = Profile(
            apartment_area=50.0,
            rooms=[
                {"type": "living", "min_area": 14.0, "preferred_aspect_ratio": 5.0},
            ],
        )
        generator = FloorplanGenerator(profile, max_aspect_ratio=4.0)
        layout = generator.generate()
        
        room = layout.rooms[0]
        assert room.aspect_ratio <= 4.0
