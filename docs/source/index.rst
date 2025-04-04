Welcome to `geoenv`
===================

Release v\ |version|. (:ref:`Installation <quickstart>`)

.. image:: https://www.repostatus.org/badges/latest/wip.svg
    :target: https://www.repostatus.org/#wip
    :alt: Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.

.. image:: https://github.com/clnsmth/geoenv/actions/workflows/ci-cd.yml/badge.svg
    :target: https://github.com/clnsmth/geoenv/actions/workflows/ci-cd.yml
    :alt: CI/CD pipeline status

.. image:: https://codecov.io/github/clnsmth/geoenv/graph/badge.svg?token=2J4MNIXCTD
    :target: https://codecov.io/github/clnsmth/geoenv
    :alt: Code coverage status

`geoenv` is a Python library that links geographic coordinates to environmental properties at a global scale. These properties are described using the terminology of the source data, with options to map to other semantic resources, including controlled vocabularies and ontologies. By default, `geoenv` maps to ENVO (`Environment Ontology`_).

If you know of a data source, vocabulary, or ontology that could enhance this effort, please share it—even if it overlaps with existing resources.

.. _Environment Ontology: https://sites.google.com/site/environmentontology/

Motivation
----------

There is a vast amount of data available from diverse sources, and geoenv offers a straightforward way to expose the environmental semantics of these datasets. By doing so, it provides a mechanism to connect otherwise disparate data sources through a shared environmental context, unlocking new opportunities for integrated analysis and research.

Quick Start
-----------

Install the current release from GitHub.

.. code-block:: bash

    pip install git+https://github.com/clnsmth/geoenv.git@main

Resolve a geometry to its environment(s).

.. code-block:: python

    from geoenv.data_sources import WorldTerrestrialEcosystems
    from geoenv.resolver import Resolver
    from geoenv.geometry import Geometry

    # Create a geometry in GeoJSON format
    point_on_land = {
        "type": "Point",
        "coordinates": [
            -122.622364,
            37.905931
        ]
    }
    geometry = Geometry(point_on_land)

    # Configure the resolver with one or more data sources
    resolver = Resolver(data_source=[WorldTerrestrialEcosystems()])

    # Resolve the geometry to environmental descriptions
    response = resolver.resolve(
        geometry,
        identifier="5b4edec5-ea5e-471a-8a3c-2c1171d59dee",
        description="Point on land",
    )

The response is a GeoJSON Feature containing a list of environments and their associated properties. These properties map to semantic resources, ENVO by default.

.. code-block:: json

    {
      "type": "Feature",
      "identifier": "5b4edec5-ea5e-471a-8a3c-2c1171d59dee",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -122.622364,
          37.905931
        ]
      },
      "properties": {
        "description": "Point on land",
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


Format the response as Schema.org.

.. code-block:: python

    schema_org = response.to_schema_org()




The API Documentation / Guide
-----------------------------

If you are looking for information on a specific function, class, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   user/api


The Contributor Guide
---------------------

If you want to contribute to the project, this part of the documentation is for
you.

.. toctree::
   :maxdepth: 3

   dev/contributing

The Maintainer Guide
--------------------

If you are a project maintainer, this part of the documentation is for
you.

.. toctree::
   :maxdepth: 3

   dev/maintaining

Project Design
--------------

The project design documentation provides an overview of the project's
architecture and design decisions.

.. toctree::
   :maxdepth: 3

   dev/design
