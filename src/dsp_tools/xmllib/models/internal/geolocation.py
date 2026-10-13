from enum import Enum


class CoordinateSystem(Enum):
    """
    The coordinate reference system of a geolocation value.
    The name of each member states whether the system is geographic or projected.

    - `GEOGRAPHIC_CRS84`: WGS84 with the longitude first. Coordinates: `(longitude, latitude)`
    - `PROJECTED_LV95`: the Swiss system LV95. Coordinates: `(easting, northing)`
    - `PROJECTED_LV03`: the Swiss system LV03. Coordinates: `(easting, northing)`

    Examples:
        ```python
        resource = resource.add_geolocation(
            prop_name=":propName",
            crs=xmllib.CoordinateSystem.PROJECTED_LV95,
            value=("2600000", "1200000"),
        )
        ```
    """

    GEOGRAPHIC_CRS84 = "CRS84"
    PROJECTED_LV95 = "LV95"
    PROJECTED_LV03 = "LV03"
