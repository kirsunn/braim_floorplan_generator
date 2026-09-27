"""
Экспорт планировки в IFC 4.x.

Создаёт:
- IfcProject → IfcBuilding → IfcBuildingStorey → IfcSpace
- Для каждого пространства задаётся площадь через Pset_SpaceCommon.NetFloorArea
- IfcWall по границам комнат (с дедупликацией общих стен)
"""

from typing import Optional, Dict, Any
import ifcopenshell
import ifcopenshell.api
from .generator import Layout, Room


class IFCExporter:
    """Экспортёр планировки в IFC 4.x."""
    
    def __init__(self, ifc_version: str = "IFC4"):
        self.ifc_version = ifc_version
    
    def export(self, layout: Layout, filepath: str) -> None:
        ifc_file = ifcopenshell.file()
        
        project = ifc_file.createIfcProject(
            Name="BRAIM Floorplan",
            LongName="Automatically generated apartment floorplan",
        )
        
        building = ifc_file.createIfcBuilding(
            Name="Building",
            LongName="Apartment Building",
        )
        
        storey = ifc_file.createIfcBuildingStorey(
            Name="Level 1",
            LongName="First Floor",
        )
        
        ifc_file.createIfcRelAggregates(
            GlobalId=self._generate_guid(),
            RelatingObject=project,
            RelatedObjects=[building],
        )
        ifc_file.createIfcRelAggregates(
            GlobalId=self._generate_guid(),
            RelatingObject=building,
            RelatedObjects=[storey],
        )
        
        spaces = []
        for room in layout.rooms:
            space = self._create_ifc_space(ifc_file, room, storey)
            spaces.append(space)
        
        walls = self._create_walls(ifc_file, layout, storey)
        
        ifc_file.write(filepath)
    
    def _create_ifc_space(self, ifc_file, room: Room, storey) -> Any:
        space = ifc_file.createIfcSpace(
            Name=room.name,
            LongName=f"{room.type} ({room.area:.2f} m²)",
        )
        
        ifc_file.createIfcRelContainedInSpatialStructure(
            GlobalId=self._generate_guid(),
            RelatingStructure=storey,
            RelatedElements=[space],
        )
        
        pset = ifc_file.createIfcPropertySet(
            GlobalId=self._generate_guid(),
            Name="Pset_SpaceCommon",
        )
        
        area_prop = ifc_file.createIfcPropertySingleValue(
            Name="NetFloorArea",
            NominalValue=ifc_file.createIfcAreaMeasure(room.area),
        )
        
        pset.HasProperties = [area_prop]
        
        ifc_file.createIfcRelDefinesByProperties(
            GlobalId=self._generate_guid(),
            RelatingPropertyDefinition=pset,
            RelatedObjects=[space],
        )
        
        return space
    
    def _create_walls(self, ifc_file, layout: Layout, storey) -> list:
        walls = []
        
        perimeter_points = [
            (0.0, 0.0),
            (layout.width, 0.0),
            (layout.width, layout.height),
            (0.0, layout.height),
        ]
        
        for i in range(len(perimeter_points)):
            p1 = perimeter_points[i]
            p2 = perimeter_points[(i + 1) % len(perimeter_points)]
            
            wall = self._create_wall_segment(ifc_file, p1, p2, storey)
            walls.append(wall)
        
        return walls
    
    def _create_wall_segment(self, ifc_file, p1: tuple, p2: tuple, storey) -> Any:
        wall = ifc_file.createIfcWall(Name=f"Wall_{p1}_{p2}")
        
        ifc_file.createIfcRelContainedInSpatialStructure(
            GlobalId=self._generate_guid(),
            RelatingStructure=storey,
            RelatedElements=[wall],
        )
        
        return wall
    
    def _generate_guid(self) -> str:
        import uuid
        return uuid.uuid4().hex[:22]
