from __future__ import annotations

import warnings
from collections.abc import Collection
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import TypeAlias
from typing import Union

import pandas as pd
from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.xml_validation import validate_xml_file
from dsp_tools.xmllib.constants import DASCH_SCHEMA
from dsp_tools.xmllib.constants import XML_NAMESPACE_MAP
from dsp_tools.xmllib.models.copyright_attributions import CopyrightAttribution
from dsp_tools.xmllib.models.copyright_attributions import CopyrightAttributions
from dsp_tools.xmllib.models.dsp_base_resources import AnnotationResource
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.licenses import License
from dsp_tools.xmllib.models.licenses import Licenses
from dsp_tools.xmllib.models.permissions import XMLPermissions
from dsp_tools.xmllib.models.resource import Resource

# ruff: noqa: D101


AnyResource: TypeAlias = Union[
    Resource, AnnotationResource, RegionResource, LinkResource, VideoSegmentResource, AudioSegmentResource
]


PRE_DEFINED_LICENSES = [
    License("CC_BY", "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    License("CC_BY_SA", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    License("CC_BY_NC", "CC BY-NC 4.0", "https://creativecommons.org/licenses/by-nc/4.0/"),
    License("CC_BY_NC_SA", "CC BY-NC-SA 4.0", "https://creativecommons.org/licenses/by-nc-sa/4.0/"),
    License("CC_BY_ND", "CC BY-ND 4.0", "https://creativecommons.org/licenses/by-nd/4.0/"),
    License("CC_BY_NC_ND", "CC BY-NC-ND 4.0", "https://creativecommons.org/licenses/by-nc-nd/4.0/"),
    License("CC0", "CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    License("unknown", "Copyright Not Evaluated", "https://rightsstatements.org/page/CNE/1.0/"),
]


@dataclass
class XMLRoot:
    shortcode: str
    default_ontology: str
    copyright_attributions: CopyrightAttributions
    licenses: Licenses
    resources: list[AnyResource] = field(default_factory=list)

    @staticmethod
    def create_new(shortcode: str, default_ontology: str) -> XMLRoot:
        """
        Create a new XML root, for one file.

        The following elements are added by default:
            - `<permissions>` (with default permissions, see [Configuration options](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/config-options/#xmllib.models.config_options.Permissions) for details)
            - `<copyright-attributions>` (empty)
            - `<licenses>` (with default licenses, see [Configuration options](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/config-options/#xmllib.models.config_options.PredefinedLicenses) for details)

        Args:
            shortcode: project shortcode
            default_ontology: name of the default ontology

        Returns:
            Instance of `XMLRoot`
        """  # noqa: E501 (Line too long)
        return XMLRoot(
            shortcode=shortcode,
            default_ontology=default_ontology,
            copyright_attributions=CopyrightAttributions(),
            licenses=Licenses(PRE_DEFINED_LICENSES),
        )

    def add_license(self, id_: str, text: str, uri: Any = None) -> XMLRoot:
        """
        Add a new license element.
        Please note that the id must be unique.

        Args:
            id_: which can be referenced in a `<bitstream>`
                or `<iiif-uri>` attribute, e.g. `<bitstream license="your_ID">`
            text: Text that should be displayed in the APP.
            uri: Optional URI liking to the license documentation.
                A `pd.isna()` check is done before adding the URI, therefore any value is permissible.

        Raises:
            InputError: If the id already exists

        Returns:
            The original XMLRoot with the added license.
        """
        if id_ in self.licenses.get_license_ids():
            raise InputError(f"A license with the ID '{id_}' already exists. All IDs must be unique.")
        new_uri = None
        if not pd.isna(uri):
            new_uri = uri
        self.licenses.licenses.append(License(id_, text, new_uri))
        return self

    def add_license_with_dict(self, license_dict: dict[str, tuple[str, Any]]) -> XMLRoot:
        """
        Add a new license element.
        Please note that the id must be unique.

        Args:
            license_dict: dictionary with the information for license elements.
                It should have the following structure: `{ id: (text, uri) }`
                A `pd.isna()` check is done before adding the URI, therefore, any value is permissible.

        Raises:
            InputError: If the id already exists

        Returns:
            The original XMLRoot with the added licenses.
        """
        if ids_exist := set(license_dict.keys()).intersection(self.licenses.get_license_ids()):
            raise InputError(
                f"The following license IDs already exist: {", ".join(ids_exist)}. All IDs must be unique."
            )
        for license_id, info_tuple in license_dict.items():
            new_uri = None
            if not pd.isna(info_tuple[1]):
                new_uri = info_tuple[1]
            self.licenses.licenses.append(License(license_id, info_tuple[0], new_uri))
        return self

    def add_copyright_attribution(self, id_: str, text: str) -> XMLRoot:
        """
        Add a new copyright attribution element.
        Please note that the id must be unique.

        Args:
            id_: which can be referenced in a `<bitstream>`
                or `<iiif-uri>` attribute, e.g. `<bitstream license="your_ID">`
            text: Text that should be displayed in the APP.

        Raises:
            InputError: If the id already exists

        Returns:
            The original XMLRoot with the added copyright attribution.
        """
        if id_ in self.copyright_attributions.get_copyright_attribution_ids():
            raise InputError(f"A copyright attribution with the ID '{id_}' already exists. All IDs must be unique.")
        self.copyright_attributions.copyright_attributions.append(CopyrightAttribution(id_, text))
        return self

    def add_copyright_attribution_with_dict(self, copyright_dict: dict[str, str]) -> XMLRoot:
        """
        Add a several new copyright attribution elements from a dictionary.
        Please note that the id must be unique.

        Args:
            copyright_dict: the dictionary should have the following structure: `{ id: text }`

        Raises:
            InputError: If the id already exists

        Returns:
            The original XMLRoot with the added copyright attributions.
        """
        if ids_exist := set(copyright_dict.keys()).intersection(
            self.copyright_attributions.get_copyright_attribution_ids()
        ):
            raise InputError(
                f"The following copyright IDs already exist: {", ".join(ids_exist)}. All IDs must be unique."
            )
        copyright_list = [CopyrightAttribution(k, v) for k, v in copyright_dict.items()]
        self.copyright_attributions.copyright_attributions.extend(copyright_list)
        return self

    def add_resource(self, resource: AnyResource) -> XMLRoot:
        """
        Add one resource to the root.

        Args:
            resource: any one of:
                    `Resource`,
                    `AnnotationResource`,
                    `RegionResource`,
                    `LinkResource`,
                    `VideoSegmentResource`,
                    `AudioSegmentResource`

        Returns:
            The original XMLRoot, with the added resource
        """
        self.resources.append(resource)
        return self

    def add_resource_multiple(self, resources: Collection[AnyResource]) -> XMLRoot:
        """
        Add a list of resources to the root.

        Args:
            resources: a list of:
                    `Resource`,
                    `AnnotationResource`,
                    `RegionResource`,
                    `LinkResource`,
                    `VideoSegmentResource`,
                    `AudioSegmentResource`
                    The types of the resources may be mixed.

        Returns:
            The original XMLRoot, with the added resource
        """
        self.resources.extend(resources)
        return self

    def add_resource_optional(self, resource: AnyResource | None) -> XMLRoot:
        """
        If the resource is not None, add it to the XMLRoot, otherwise return the XMLRoot unchanged.

        Args:
            resource: any one of:
                    `Resource`,
                    `AnnotationResource`,
                    `RegionResource`,
                    `LinkResource`,
                    `VideoSegmentResource`,
                    `AudioSegmentResource`

        Returns:
            The original XMLRoot, with the added value if it was not empty. Else the unchanged original XMLRoot.
        """
        if resource:
            self.resources.append(resource)
        return self

    def write_file(self, filepath: str | Path) -> None:
        """
        Write the finished XML to a file.

        Args:
            filepath: where to save the file

        Warning:
            if the XML is not valid according to the schema
        """
        root = self.serialise()
        etree.indent(root, space="    ")
        xml_string = etree.tostring(
            root,
            encoding="unicode",
            pretty_print=True,
            doctype='<?xml version="1.0" encoding="UTF-8"?>',
        )
        xml_string = xml_string.replace(r"\'", "'")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_string)
        try:
            validate_xml_file(input_file=filepath)
            print(f"The XML file was successfully saved to {filepath}")
        except BaseError as err:
            msg = (
                f"The XML file was successfully saved to {filepath}, "
                f"but the following Schema validation error(s) occurred: {err.message}"
            )
            warnings.warn(DspToolsUserWarning(msg))

    def serialise(self) -> etree._Element:
        """
        Create an `lxml.etree._Element` with the information in the root.
        If you wish to create a file, we recommend using the `write_file` method instead.

        Returns:
            The `XMLRoot` serialised as XML
        """
        root = self._make_root()
        permissions = XMLPermissions().serialise()
        root.extend(permissions)
        serialised_resources = [x.serialise() for x in self.resources]
        root.extend(serialised_resources)
        return root

    def _make_root(self) -> etree._Element:
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
