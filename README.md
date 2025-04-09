<p align="center">
  <img src="https://your-url.com/logo.png" alt="geoenv" width="200">
</p>
<p align="center">
  <em>Map geographies to environments. Semantic, extensible, and built for global scale.</em>
</p>
<p align="center">
  <a href="https://github.com/clnsmth/geoenv/actions/workflows/ci-cd.yml">
    <img src="https://github.com/clnsmth/geoenv/actions/workflows/ci-cd.yml/badge.svg" alt="CI Status">
  </a>
  <a href="https://codecov.io/github/clnsmth/geoenv">
    <img src="https://codecov.io/github/clnsmth/geoenv/graph/badge.svg?token=2J4MNIXCTD" alt="Test Coverage">
  </a>
  <a href="https://www.repostatus.org/#wip">
    <img src="https://www.repostatus.org/badges/latest/wip.svg" alt="Project Status: WIP">
  </a>
</p>

# geoenv

---

**Documentation**: [https://geoenv.readthedocs.io/en/latest/](https://geoenv.readthedocs.io/en/latest/)

**Source Code**: [https://github.com/clnsmth/geoenv](https://github.com/clnsmth/geoenv)

---

`geoenv` is a Python library that links geographic locations—like points and polygons—to environmental descriptions using global datasets and semantic vocabularies.

It’s like reverse geocoding, but for **environments**.

Whether you're working with field samples, sensor deployments, or satellite observations, `geoenv` helps you describe the environment with consistent, interoperable metadata.

### Highlights

- **Global data support**  
  Works with terrestrial and ecological datasets at global scale.
  
- **Semantically rich**  
  Maps environmental terms to [ENVO](https://sites.google.com/site/environmentontology/) and other vocabularies.

- **Extensible**  
  Plug in your own data sources or vocabularies.

- **Built for integration**  
  Returns structured GeoJSON + Schema.org outputs for interoperability.

> Know of a useful dataset, vocabulary, or ontology? [Suggest it!](https://github.com/clnsmth/geoenv/issues)

---

## Quick Start

Install directly from GitHub:

```bash
pip install git+https://github.com/clnsmth/geoenv.git@main
```

Resolve a point on land:

```python
from geoenv.data_sources import WorldTerrestrialEcosystems
from geoenv.resolver import Resolver
from geoenv.geometry import Geometry

# Define a geometry in GeoJSON format
geometry = Geometry(
    {
        "type": "Point",
        "coordinates": [
            -122.622364,
            37.905931
        ]
    }
)

# Configure the resolver with one or more data sources
resolver = Resolver(data_source=[WorldTerrestrialEcosystems()])

# Resolve the geometry to environmental descriptions
response = resolver.get_environment(geometry)
```

The result is a GeoJSON Feature with structured environments mapped to ENVO (by default):

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

---

### But how do I link results back to my data? 

That's what the resolver's `identifier` and `description` parameters are for. Set these to what ever values are useful for your application.

```python
response = resolver.get_environment(
    geometry = geometry,
    identifier="5b4edec5-ea5e-471a-8a3c-2c1171d59dee",
    description="Point on land",
)
```

These will then be displayed in the GeoJSON response and accessible whenever you need it.

```json
{
  "type": "Feature",
  "identifier": "5b4edec5-ea5e-471a-8a3c-2c1171d59dee",
  "geometry": {... same as before},
  "properties": {
    "description": "Point on land",
    "environment": [... same as before]
  }
}


```

---

### Can I resolve against multiple data sources?

But we don't always know where a geometry will resolve to. That's OK. We can configure the resolver with a list of data sources to query and it will try them all.

```python
from geoenv.resolver import Resolver
from geoenv.data_sources import (WorldTerrestrialEcosystems, 
                                 EcologicalCoastalUnits,
                                 EcologicalMarineUnits)

# Now configured with 3 data sources
resolver = Resolver(
    data_source=[
        WorldTerrestrialEcosystems(),
        EcologicalCoastalUnits(),
        EcologicalMarineUnits()
    ]
)

response = resolver.get_environment(geometry)
```

The response is a list of environments listing each data source.

```json
response
```
---

### Support for Schema.org?


We may want to represent this in Schema.org format. The response is already structured to be easily converted to Schema.org. 

```python
response.to_schema_org()
```

Presto

```json
schema.org example
```
---

## Motivation
There is a vast amount of data available from diverse sources, and `geoenv` offers a straightforward way to expose the environmental semantics of these datasets. By doing so, it provides a mechanism to connect otherwise disparate data sources through a shared environmental context, unlocking new opportunities for integrated analysis and research.

---

## License
This project is licensed under the terms of the MIT license.