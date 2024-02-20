from dataclasses import dataclass


@dataclass
class TextValueData:
    resource_id: str
    property_name: str
    encoding: set[str]
