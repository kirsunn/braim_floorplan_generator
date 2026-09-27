"""
Unit-тесты проверки эргономики.
"""

import pytest
from braim_floorplan_generator import ErgonomicsChecker, RoomRequirements, Layout, Room


class TestRoomRequirements:
    """Тесты требований к комнатам."""
    
    def test_get_defaults(self):
        reqs = RoomRequirements.get_defaults()
        
        assert "bathroom" in reqs
        assert reqs["bathroom"].min_area == 3.0
        assert reqs["kitchen"].min_area == 8.0
        assert reqs["living"].min_area == 14.0


class TestErgonomicsChecker:
    """Тесты проверки эргономики."""
    
    def test_valid_layout(self):
        layout = Layout(
            rooms=[
                Room(type="living", area=18.0, width=4.5, height=4.0, name="Living1"),
                Room(type="bedroom", area=12.0, width=4.0, height=3.0, name="Bed1"),
            ],
            apartment_area=30.0,
        )
        
        checker = ErgonomicsChecker()
        issues = checker.check(layout)
        
        assert len(issues) == 0
        assert checker.is_valid(layout)
    
    def test_invalid_area(self):
        layout = Layout(
            rooms=[
                Room(type="bathroom", area=2.0, width=1.5, height=2.0, name="Bath1"),
            ],
            apartment_area=2.0,
        )
        
        checker = ErgonomicsChecker()
        issues = checker.check(layout)
        
        assert len(issues) == 1
        assert issues[0].issue_type == "min_area"
        assert issues[0].actual_value == 2.0
        assert issues[0].required_value == 3.0
    
    def test_invalid_width(self):
        layout = Layout(
            rooms=[
                Room(type="kitchen", area=10.0, width=1.5, height=5.0, name="Kitchen1"),
            ],
            apartment_area=10.0,
        )
        
        checker = ErgonomicsChecker()
        issues = checker.check(layout)
        
        assert len(issues) == 1
        assert issues[0].issue_type == "min_width"
        assert issues[0].actual_value == 1.5
        assert issues[0].required_value == 2.0
    
    def test_invalid_height(self):
        layout = Layout(
            rooms=[
                Room(type="bedroom", area=12.0, width=6.0, height=1.5, name="Bed1"),
            ],
            apartment_area=12.0,
        )
        
        checker = ErgonomicsChecker()
        issues = checker.check(layout)
        
        assert len(issues) == 1
        assert issues[0].issue_type == "min_height"
    
    def test_invalid_aspect_ratio(self):
        layout = Layout(
            rooms=[
                Room(type="living", area=20.0, width=10.0, height=1.0, name="Living1"),
            ],
            apartment_area=20.0,
        )
        
        checker = ErgonomicsChecker()
        issues = checker.check(layout)
        
        assert len(issues) == 1
        assert issues[0].issue_type == "max_aspect_ratio"
        assert issues[0].actual_value > 4.0
    
    def test_multiple_issues(self):
        layout = Layout(
            rooms=[
                Room(type="bathroom", area=1.0, width=0.8, height=1.0, name="Bath1"),
            ],
            apartment_area=1.0,
        )
        
        checker = ErgonomicsChecker()
        issues = checker.check(layout)
        
        assert len(issues) >= 2
    
    def test_unknown_room_type(self):
        layout = Layout(
            rooms=[
                Room(type="unknown_type", area=5.0, width=2.0, height=2.5, name="Unknown1"),
            ],
            apartment_area=5.0,
        )
        
        checker = ErgonomicsChecker()
        issues = checker.check(layout)
        
        assert len(issues) == 0
    
    def test_summary_valid(self):
        layout = Layout(
            rooms=[
                Room(type="living", area=18.0, width=4.5, height=4.0, name="Living1"),
            ],
            apartment_area=18.0,
        )
        
        checker = ErgonomicsChecker()
        summary = checker.summary(layout)
        
        assert "✓" in summary
        assert "Все проверки эргономики пройдены" in summary
    
    def test_summary_invalid(self):
        layout = Layout(
            rooms=[
                Room(type="bathroom", area=2.0, width=1.5, height=2.0, name="Bath1"),
            ],
            apartment_area=2.0,
        )
        
        checker = ErgonomicsChecker()
        summary = checker.summary(layout)
        
        assert "✗" in summary
        assert "Найдено проблем: 1" in summary
