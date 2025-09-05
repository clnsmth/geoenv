# geoenv

_Map geometries to environmental semantics_

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
![example workflow](https://github.com/clnsmth/geoenv/actions/workflows/ci-cd.yml/badge.svg)
[![codecov](https://codecov.io/github/clnsmth/geoenv/graph/badge.svg?token=2J4MNIXCTD)](https://codecov.io/github/clnsmth/geoenv)
![PyPI - Version](https://img.shields.io/pypi/v/geoenv?color=blue)


`geoenv` is a Python library that maps geospatial geometries, such as points and polygons, to standardized environmental terms. It’s like reverse geocoding, but for environments. 

## Motivation

Finding datasets based on their environmental context is a challenge in data synthesis. The process often relies on vague or inconsistent metadata. This variability presents a barrier to reliable, large-scale analysis due to time lost in data discovery and incomplete search results.

`geoenv` helps address this challenge by using a dataset’s originating location as a consistent and objective starting point. It can programmatically map the geometry of this location to standardized environmental terms, providing a scalable and repeatable method for generating interoperable metadata. This approach aims to enrich datasets with uniform, semantic metadata, making them potentially easier to discover, query, and integrate at scale.


## Key Features

- **Automated Semantic Annotation:** Supplements inconsistent, manual descriptions with standardized environmental terms from controlled vocabularies.
- **Structured, Interoperable Output:** Generates GeoJSON objects enriched with formal terms from [ENVO](https://sites.google.com/site/environmentontology/) (by default).
- **Global Coverage:** Provides worldwide coverage for terrestrial, coastal, and marine environments using high-resolution data sources.
- **Extensible:** Designed to accommodate new data sources or vocabularies for specific research needs.

> Know of a useful data source or vocabulary? [Suggest it!](https://github.com/clnsmth/geoenv/issues)


## Quick Start

Install from PyPI:

```bash
pip install geoenv
```

Resolve a point on land:

```python
import asyncio
from geoenv.data_sources import WorldTerrestrialEcosystems
from geoenv.geometry import Geometry
from geoenv.resolver import Resolver

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

# Configure the resolver with a data source (there can be multiple)
resolver = Resolver(data_source=[WorldTerrestrialEcosystems()])

# Resolve the geometry to environmental descriptions. Concurrent resolution 
# to multiple data sources is supported via asyncio.
response = asyncio.run(resolver.resolve(geometry))
```

The response is a GeoJSON `Feature` with structured environments mapped to [ENVO](https://sites.google.com/site/environmentontology/) (by default):

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

## Related Projects

The [Global Ecosystems Atlas](https://globalecosystemsatlas.org/) is a project that provides a comprehensive, harmonized open resource on the world's ecosystems. It standardizes diverse geospatial datasets by mapping them to the [IUCN Global Ecosystem Typology](https://global-ecosystems.org/), a hierarchical classification of environments.

## Contributing

We welcome contributions! If you know of a useful data source or vocabulary, and have ideas for new features, or find a bug, please [open an issue](https://github.com/clnsmth/geoenv/issues) to start a discussion.

## License

This project is licensed under the terms of the MIT license.