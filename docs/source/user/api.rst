.. _api:

Developer Interface
===================

.. Generally, we want to exclude low level Class members from the public API
   docs to methods that are not intended for public use.

Main Interface
--------------

.. automodule:: geoenv.resolver
   :members:
   :exclude-members: data_source

Data Sources
------------

.. autoclass:: geoenv.data_sources.WorldTerrestrialEcosystems
   :members:
   :exclude-members: get_environment, convert_data, unique_environment,
      has_environment, data, geometry, properties, set_properties

.. autoclass:: geoenv.data_sources.EcologicalCoastalUnits
   :members:
   :exclude-members: convert_data, data, geometry, get_environment,
      has_environment, properties, set_properties, unique_environment

.. autoclass:: geoenv.data_sources.EcologicalMarineUnits
   :members:
   :exclude-members: convert_codes_to_values, convert_data, data, geometry,
      get_environment, get_environments_for_geometry_z_values, has_environment,
      properties, set_properties, unique_environment

Geometry
--------

.. automodule:: geoenv.geometry
   :members:
   :exclude-members: grid_sample_polygon

Response
--------

.. automodule:: geoenv.response
   :members:
   :exclude-members: properties, construct_response

Environment
-----------

.. automodule:: geoenv.environment
   :members:

Utilities
---------

.. automodule:: geoenv.utilities
   :members:
   :exclude-members: EnvironmentDataModel, get_properties

