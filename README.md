# geoenv

_Map geographies to environmental semantics._

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
![example workflow](https://github.com/clnsmth/geoenv/actions/workflows/ci-cd.yml/badge.svg)
[![codecov](https://codecov.io/github/clnsmth/geoenv/graph/badge.svg?token=2J4MNIXCTD)](https://codecov.io/github/clnsmth/geoenv)

`geoenv` is a Python library that links geographic locations—like points and polygons—to environmental descriptions using global datasets and semantic vocabularies.

It’s like reverse geocoding, but for environments.

Whether you're working with field samples, sensor deployments, or satellite observations, `geoenv` helps you describe the environment with consistent, interoperable metadata.

### Highlights

- **Global data support**:  
  Works with terrestrial, coastal, and marine environments at global scale.
  
- **Semantically rich**:  
  Maps environmental terms to [ENVO](https://sites.google.com/site/environmentontology/) and other vocabularies.

- **Extensible**:  
  Plug in new data sources or vocabularies.

- **Built for integration**:  
  Returns structured GeoJSON + Schema.org outputs for interoperability.

> Know of a useful data source or vocabulary? [Suggest it!](https://github.com/clnsmth/geoenv/issues)


## Quick Start

Install directly from GitHub:

```bash
pip install git+https://github.com/clnsmth/geoenv.git@main
```

Resolve a point on land:

```python
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

# Resolve the geometry to environmental descriptions
response = resolver.get_environment(geometry)
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


## Motivation
There is a vast amount of data available from diverse sources, and `geoenv` offers a straightforward way to expose the environmental semantics of these datasets. By doing so, it provides a mechanism to connect otherwise disparate data sources through a shared environmental context, unlocking new opportunities for integrated analysis and research.



## License
This project is licensed under the terms of the MIT license.