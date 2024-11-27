from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pandas as pd
from lxml import etree

from dsp_tools.models.exceptions import InputError

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"

# TODO: separate object

@dataclass
class CopyrightAndLicense:
    copyright_attribution: list[CopyrightAttribution] = field(default_factory=list)
    license: list[License] = field(default_factory=list)

    @staticmethod
    def create_new() -> CopyrightAndLicense:
        """
        Creates a new copyright attribution and license container.
        New copyright attributions and licenses can be added.

        The following licenses are included by default:
        They can be referenced through a string or one of the PreDefinedLicenses
            - `CC_BY` [Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
            - `CC_BY_SA` [Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/)
            - `CC_BY_NC` [Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/)
            - `CC_BY_NC_SA` [Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/)
            - `CC_BY_ND` [Attribution-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nd/4.0/)
            - `CC_BY_NC_ND` [Attribution-NonCommercial-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nc-nd/4.0/)
            - `CC0` [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
            - `UNKNOWN` [Copyright Not Evaluated](http://rightsstatements.org/vocab/CNE/1.0/)

        Returns:
            A CopyrightAndLicense object with the default licenses.
        """
        return CopyrightAndLicense(license=PRE_DEFINED_LICENSES)

    def add_copyright_attribution(self, id_: str, text: str) -> CopyrightAndLicense:
        """
        Add a new copyright attribution element.
        Please note that the id must be unique.

        Args:
            id_: ID which is referenced in the attributes of the XML
            text: Text that should be displayed in the APP.

        Raises:
            InputError: If the id already exists

        Returns:
            The original CopyrightAndLicense with the added copyright attribution.
        """
        if id_ in self.get_copyright_attribution_ids():
            raise InputError(
                f"Copyright attribution with the ID '{id_}' and the text '{text}' already exists. "
                f"All IDs must be unique."
            )
        self.copyright_attribution.append(CopyrightAttribution(id_, text))
        return self

    def add_copyright_attribution_with_dict(self, copyright_dict: dict[str, str]) -> CopyrightAndLicense:
        """
        Add a several new copyright attribution elements from a dictionary.
        Please note that the id must be unique.

        Args:
            copyright_dict: the dictionary should have the following structure: { id: text }

        Raises:
            InputError: If the id already exists

        Returns:
            The original CopyrightAndLicense with the added copyright attributions.
        """
        if ids_exist := set(copyright_dict.keys()).intersection(self.get_copyright_attribution_ids()):
            raise InputError(
                f"The following copyright IDs already exist: {", ".join(ids_exist)}. All IDs must be unique."
            )
        copyright_list = [CopyrightAttribution(k, v) for k, v in copyright_dict.items()]
        self.copyright_attribution.extend(copyright_list)
        return self

    def get_copyright_attribution_ids(self) -> set[str]:
        return {x.id_ for x in self.copyright_attribution}

    def add_license(self, id_: str, text: str, uri: Any = None) -> CopyrightAndLicense:
        """
        Add a new license element.
        Please note that the id must be unique.

        Args:
            id_: ID which is referenced in the attributes of the XML
            text: Text that should be displayed in the APP.
            uri: Optional URI liking to the license documentation.
            A pd.isna() check is done before adding the URI, therefore any value is permissible.

        Raises:
            InputError: If the id already exists

        Returns:
            The original CopyrightAndLicense with the added license.
        """
        if id_ in self.get_license_ids():
            raise InputError(
                f"A license with the ID '{id_}' and the text '{text}' already exists. " f"All IDs must be unique."
            )
        new_uri = None
        if not pd.isna(uri):
            new_uri = uri
        self.license.append(License(id_, text, new_uri))
        return self

    def add_license_with_dict(self, license_dict: dict[str, tuple[str, Any]]) -> CopyrightAndLicense:
        """
        Add a new license element.
        Please note that the id must be unique.

        Args:
            license_dict: dictionary with the information for license elements.
                It should have the following structure: { id:
                (text, uri) } A pd.isna() check is done before adding the URI, therefore, any value is permissible.

        Raises:
            InputError: If the id already exists

        Returns:
            The original CopyrightAndLicense with the added licenses.
        """
        if ids_exist := set(license_dict.keys()).intersection(self.get_copyright_attribution_ids()):
            raise InputError(
                f"The following license IDs already exist: {", ".join(ids_exist)}. All IDs must be unique."
            )
        for license_id, info_tuple in license_dict.items():
            new_uri = None
            if not pd.isna(info_tuple[1]):
                new_uri = info_tuple[1]
            self.license.append(License(license_id, info_tuple[0], new_uri))
        return self

    def get_license_ids(self) -> set[str]:
        return {x.id_ for x in self.license}

    def serialise_copyright_attributions(self) -> etree._Element:
        copyrights = etree.Element(f"{DASCH_SCHEMA}copyrights", nsmap=XML_NAMESPACE_MAP)
        for copy_right in self.copyright_attribution:
            attrib = {"id": copy_right.id_}
            ele = etree.Element(f"{DASCH_SCHEMA}copyright", attrib=attrib, nsmap=XML_NAMESPACE_MAP)
            ele.text = copy_right.text
            copyrights.append(ele)
        return copyrights

    def serialise_license(self) -> etree._Element:
        licenses = etree.Element(f"{DASCH_SCHEMA}licenses", nsmap=XML_NAMESPACE_MAP)
        for one_license in self.license:
            attrib = {"id": one_license.id_}
            if one_license.uri:
                attrib["uri"] = one_license.uri
                ele = etree.Element(f"{DASCH_SCHEMA}license", attrib=attrib, nsmap=XML_NAMESPACE_MAP)
                ele.text = one_license.text
                licenses.append(ele)
        return licenses


@dataclass
class CopyrightAttribution:
    id_: str
    text: str


@dataclass
class License:
    id_: str
    text: str
    uri: str | None


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
