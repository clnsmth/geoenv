"""data_sources"""

from .ecological_coastal_units import EcologicalCoastalUnits
from .ecological_marine_units import EcologicalMarineUnits
from .world_terrestrial_ecosystems import WorldTerrestrialEcosystems
from .global_lakes_and_wetlands import GlobalLakesAndWetlands
from .global_river_classification import GlobalRiverClassification

__all__ = [
    "EcologicalCoastalUnits",
    "EcologicalMarineUnits",
    "WorldTerrestrialEcosystems",
    "GlobalLakesAndWetlands",
    "GlobalRiverClassification",
]
