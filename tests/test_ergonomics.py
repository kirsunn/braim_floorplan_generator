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

def test_invalid_min_dimension_for_living(self):
    # 2.0 x 9.0 → min_dim=2.0 < 3.0, aspect_ratio=4.5 > 4.0
    # Ожидаем 2 issues
    layout = Layout(
        rooms=[
            Room(type="living", area=18.0, width=2.0, height=9.0, name="Living1"),
        ],
        apartment_area=18.0,
    )

    checker = ErgonomicsChecker()
    issues = checker.check(layout)

    assert len(issues) == 2
    assert any(i.issue_type == "min_dimension" for i in issues)
    assert any(i.issue_type == "aspect_ratio" for i in issues)


def test_invalid_aspect_ratio_only(self):
    # Комната с НОРМАЛЬНЫМ min dimension, но aspect ratio > 4.0
    # min_dim >= 3.0, например 3.0 x 13.0 → aspect_ratio=4.33 > 4.0
    layout = Layout(
        rooms=[
            Room(type="living", area=39.0, width=3.0, height=13.0, name="Living1"),
        ],
        apartment_area=39.0,
    )

    checker = ErgonomicsChecker()
    issues = checker.check(layout)

    # aspect_ratio = 13.0 / 3.0 = 4.33 > 4.0, min_dim = 3.0 >= 3.0 OK
    assert len(issues) == 1
    assert issues[0].issue_type == "aspect_ratio"


def test_invalid_aspect_ratio_extreme(self):
    # Комната с НОРМАЛЬНЫМ min dimension, но aspect ratio > 4.0
    # min_dim >= 3.0, например 3.0 x 15.0 → aspect_ratio=5.0 > 4.0
    layout = Layout(
        rooms=[
            Room(type="living", area=45.0, width=3.0, height=15.0, name="Living1"),
        ],
        apartment_area=45.0,
    )

    checker = ErgonomicsChecker()
    issues = checker.check(layout)

    # aspect_ratio = 15.0 / 3.0 = 5.0 > 4.0, min_dim = 3.0 >= 3.0 OK
    assert len(issues) == 1
    assert issues[0].issue_type == "aspect_ratio"


def test_multiple_rooms_with_issues(self):
    # Living: 2.0 x 9.0 → 2 issues (min_dim + aspect_ratio)
    # Bedroom: 6.0 x 1.1 → 2 issues (min_dim + aspect_ratio)
    # Total: 4 issues
    layout = Layout(
        rooms=[
            Room(type="living", area=18.0, width=2.0, height=9.0, name="Living1"),
            Room(type="bedroom", area=12.0, width=6.0, height=1.1, name="Bed1"),
        ],
        apartment_area=30.0,
    )

    checker = ErgonomicsChecker()
    issues = checker.check(layout)

    assert len(issues) == 4