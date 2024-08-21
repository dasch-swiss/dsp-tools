from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from lxml import etree

from dsp_tools.commands.excel2xml import append_permissions
from dsp_tools.commands.excel2xml import write_xml
from dsp_tools.commands.xmllib.models.resource import Resource

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


@dataclass
class XMLRoot:
    shortcode: str
    default_ontology: str
    resources: list[Resource] = field(default_factory=list)

    def make_root(self) -> etree._Element:
        schema_url = (
            "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/data.xsd"
        )
        schema_location_key = str(etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation"))
        schema_location_value = f"https://dasch.swiss/schema {schema_url}"
        return etree.Element(
            f"{DASCH_SCHEMA}knora",
            attrib={
                schema_location_key: schema_location_value,
                "shortcode": self.shortcode,
                "default-ontology": self.default_ontology,
            },
            nsmap=XML_NAMESPACE_MAP,
        )

    def serialise(self) -> etree._Element:
        root = self.make_root()
        root = append_permissions(root)
        serialised_resources = [x.serialise() for x in self.resources]
        root.extend(serialised_resources)
        return root

    def write_file(self, filepath: str | Path) -> None:
        root = self.serialise()
        write_xml(root, filepath)
