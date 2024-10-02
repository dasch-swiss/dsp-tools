from enum import Enum
from enum import auto

from lxml import etree

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


class Permissions(Enum):
    open = auto()
    restricted = auto()
    restricted_view = auto()


class XMLPermissions:
    def get(self) -> list[etree._Element]:
        pass
