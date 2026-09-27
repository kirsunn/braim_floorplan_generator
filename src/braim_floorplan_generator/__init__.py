"""
BRAIM Floorplan Generator

Python-библиотека для автоматической генерации планировок квартир с экспортом в IFC 4.x, SVG и JSON,
а также валидацией по эргономическим нормам через IDS-правила.
"""

from .generator import FloorplanGenerator, Profile, Room, Layout
from .ifc_exporter import IFCExporter
from .svg_exporter import SVGExporter
from .json_exporter import JSONExporter
from .ergonomics import ErgonomicsChecker, RoomRequirements
from .validator import PlanValidator

__version__ = "0.1.0"
__all__ = [
    "FloorplanGenerator",
    "Profile",
    "Room",
    "Layout",
    "IFCExporter",
    "SVGExporter",
    "JSONExporter",
    "ErgonomicsChecker",
    "RoomRequirements",
    "PlanValidator",
]
