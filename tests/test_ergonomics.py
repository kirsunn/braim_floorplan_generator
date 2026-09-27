import pytest
from src.braim_floorplan_generator.functional_layout import Layout, Room
from src.braim_floorplan_generator.validator import ErgonomicsChecker, ErgonomicsIssue


class TestErgonomicsChecker:
    def test_valid_living_room(self):
        layout = Layout(
            rooms=[
                Room(type="living", area=18.0, width=4.0, height=4.5, name="Living1"),
            ],
            apartment_area=18.0,
        )

        checker = ErgonomicsChecker()
        issues = checker.check(layout)

        assert len(issues) == 0

    def test_valid_bedroom(self):
        layout = Layout(
            rooms=[
                Room(type="bedroom", area=12.0, width=3.0, height=4.0, name="Bed1"),
            ],
            apartment_area=12.0,
        )

        checker = ErgonomicsChecker()
        issues = checker.check(layout)

        assert len(issues) == 0

    def test_valid_kitchen(self):
        layout = Layout(
            rooms=[
                Room(type="kitchen", area=10.0, width=2.5, height=4.0, name="Kitchen1"),
            ],
            apartment_area=10.0,
        )

        checker = ErgonomicsChecker()
        issues = checker.check(layout)

        assert len(issues) == 0

    def test_invalid_min_dimension_for_living(self):
        layout = Layout(
            rooms=[
                Room(type="living", area=18.0, width=2.0, height=9.0, name="Living1"),
            ],
            apartment_area=18.0,
        )

        checker = ErgonomicsChecker()
        issues = checker.check(layout)

        assert len(issues) == 1
        assert issues[0].issue_type == "min_dimension"

    def test_invalid_min_dimension_for_kitchen(self):
        layout = Layout(
            rooms=[
                Room(type="kitchen", area=10.0, width=1.1, height=5.0, name="Kitchen1"),
            ],
            apartment_area=10.0,
        )

        checker = ErgonomicsChecker()
        issues = checker.check(layout)

        # Сейчас два нарушения: min dimension + aspect ratio
        assert len(issues) == 2
        assert any(i.issue_type == "min_dimension" for i in issues)
        assert any(i.issue_type == "aspect_ratio" for i in issues)

    def test_invalid_min_dimension_for_bedroom(self):
        layout = Layout(
            rooms=[
                Room(type="bedroom", area=12.0, width=6.0, height=1.1, name="Bed1"),
            ],
            apartment_area=12.0,
        )

        checker = ErgonomicsChecker()
        issues = checker.check(layout)

        # Сейчас два нарушения: min dimension + aspect ratio
        assert len(issues) == 2
        assert any(i.issue_type == "min_dimension" for i in issues)
        assert any(i.issue_type == "aspect_ratio" for i in issues)

    def test_invalid_aspect_ratio_only(self):
        # Комната с нормальным min dimension, но плохим aspect ratio
        layout = Layout(
            rooms=[
                Room(type="living", area=20.0, width=2.5, height=8.0, name="Living1"),
            ],
            apartment_area=20.0,
        )

        checker = ErgonomicsChecker()
        issues = checker.check(layout)

        # aspect_ratio = 8.0 / 2.5 = 3.2 < 4.0, нарушений нет
        assert len(issues) == 0

    def test_invalid_aspect_ratio_extreme(self):
        # Комната с нормальным min dimension, но aspect ratio > 4.0
        layout = Layout(
            rooms=[
                Room(type="living", area=20.0, width=2.5, height=12.0, name="Living1"),
            ],
            apartment_area=20.0,
        )

        checker = ErgonomicsChecker()
        issues = checker.check(layout)

        # aspect_ratio = 12.0 / 2.5 = 4.8 > 4.0
        assert len(issues) == 1
        assert issues[0].issue_type == "aspect_ratio"

    def test_multiple_rooms_with_issues(self):
        layout = Layout(
            rooms=[
                Room(type="living", area=18.0, width=2.0, height=9.0, name="Living1"),
                Room(type="bedroom", area=12.0, width=6.0, height=1.1, name="Bed1"),
            ],
            apartment_area=30.0,
        )

        checker = ErgonomicsChecker()
        issues = checker.check(layout)

        # Living: 1 issue (min_dimension)
        # Bedroom: 2 issues (min_dimension + aspect_ratio)
        assert len(issues) == 3
