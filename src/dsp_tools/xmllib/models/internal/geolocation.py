from enum import Enum


class CoordinateSystem(Enum):
    """
    The coordinate reference system of a geolocation value, with its code in the XML.
    Users do not select it: each public coordinates class in `xmllib.models.geolocation` sets it.
    """

    GEOGRAPHIC_CRS84 = "CRS84"
    PROJECTED_LV95 = "LV95"
    PROJECTED_LV03 = "LV03"
