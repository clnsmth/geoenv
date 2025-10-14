# geoenv

_Map geometries to environmental semantics_

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
![example workflow](https://github.com/clnsmth/geoenv/actions/workflows/ci-cd.yml/badge.svg)
[![codecov](https://codecov.io/github/clnsmth/geoenv/graph/badge.svg?token=2J4MNIXCTD)](https://codecov.io/github/clnsmth/geoenv)
![PyPI - Version](https://img.shields.io/pypi/v/geoenv?color=blue)


`geoenv` is a Python library that maps geospatial geometries, such as points and polygons, to environmental terms in vocabularies/ontologies (e.g. [ENVO](https://sites.google.com/site/environmentontology/)). It’s like reverse geocoding, but for environments.

## Features

- **Broad scale environmental context:** Provides consistent broad scale environmental context supplementing local scale environmental descriptions.  
- **Global Coverage**: Provides worldwide resolution of terrestrial, coastal, and marine environments.  
- **GeoJSON Output:** Outputs data as a GeoJSON Feature, for integration with other tools and libraries.  
- **Concurrent Data Resolution:** Leverages `asyncio` to query multiple geospatial data sources concurrently, providing fast results.
- **Modular and Extensible**: Designed with a modular architecture to facilitate integration of new data sources and vocabularies.

## Quick Start

Install from PyPI:

```bash
$ pip install geoenv
```

Resolve a point location to environmental descriptions:

```python
import asyncio
from geoenv.geometry import Geometry
from geoenv.resolver import Resolver
from geoenv.data_sources import (WorldTerrestrialEcosystems,
                                 EcologicalMarineUnits,
                                 EcologicalCoastalUnits)

# Define a geometry in GeoJSON format (Point or Polygon)
geometry = Geometry(
    {
        "type": "Point",
        "coordinates": [
            -122.622364,
            37.905931
        ]
    }
)

# Set up the resolver. When the location's environment is not known, 
# multiple data sources are included to cover potential environment 
# types.
resolver = Resolver(
    data_source=[
        WorldTerrestrialEcosystems(),
        EcologicalMarineUnits(),
        EcologicalCoastalUnits(),
    ]
)

# Resolve the geometry to environmental descriptions. The resolver 
# queries multiple data sources concurrently using `asyncio`.
response = asyncio.run(resolver.resolve(geometry))

# Access response data.
print(response.data)
```

The response is a GeoJSON `Feature` with environmental terms mapped to [ENVO](https://sites.google.com/site/environmentontology/) (by default). Only resolved environments are included:

```json
{
  "type": "Feature",
  "identifier": null,
  "geometry": {
    "type": "Point",
    "coordinates": [
      -122.622364,
      37.905931
    ]
  },
  "properties": {
    "description": null,
    "environment": [
      {
        "type": "Environment",
        "dataSource": {
          "identifier": "https://doi.org/10.5066/P9DO61LP",
          "name": "WorldTerrestrialEcosystems"
        },
        "dateCreated": "2025-03-07 15:53:09",
        "properties": {
          "temperature": "Warm Temperate",
          "moisture": "Moist",
          "landCover": "Cropland",
          "landForm": "Mountains",
          "climate": "Warm Temperate Moist",
          "ecosystem": "Warm Temperate Moist Cropland on Mountains"
        },
        "mappedProperties": [
          {
            "label": "temperate",
            "uri": "http://purl.obolibrary.org/obo/ENVO_01000206"
          },
          {
            "label": "humid air",
            "uri": "http://purl.obolibrary.org/obo/ENVO_01000828"
          },
          {
            "label": "area of cropland",
            "uri": "http://purl.obolibrary.org/obo/ENVO_01000892"
          },
          {
            "label": "mountain range",
            "uri": "http://purl.obolibrary.org/obo/ENVO_00000080"
          }
        ]
      }
    ]
  }
}


```

## Motivation

Finding datasets based on their environmental context is a challenge in data synthesis. The process often relies on vague or inconsistent metadata. This variability presents a barrier to reliable, large-scale analysis due to time lost in data discovery and incomplete search results.

`geoenv` helps address this challenge by using a dataset’s originating location as a consistent and objective starting point. It can programmatically map the geometry of this location to standardized environmental terms, providing a scalable and repeatable method for generating interoperable metadata. This approach aims to enrich datasets with uniform, semantic metadata, making them potentially easier to discover, query, and integrate at scale.

## Related Projects

The [Global Ecosystems Atlas](https://globalecosystemsatlas.org/) is a project that provides a comprehensive, harmonized open resource on the world's ecosystems. It standardizes diverse geospatial datasets by mapping them to the [IUCN Global Ecosystem Typology](https://global-ecosystems.org/), a hierarchical classification of environments.

## Contributing

We welcome contributions! If you know of a useful data source or vocabulary, and have ideas for new features, or find a bug, please [open an issue](https://github.com/clnsmth/geoenv/issues) to start a discussion.

## License

This project is licensed under the terms of the MIT license.