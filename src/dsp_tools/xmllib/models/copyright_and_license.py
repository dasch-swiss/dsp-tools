from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pandas as pd

from dsp_tools.models.exceptions import InputError


@dataclass
class CopyrightAndLicense:
    copyright_attribution: list[CopyrightAttribution] = field(default_factory=list)
    license: list[License] = field(default_factory=list)

    @staticmethod
    def create_new() -> CopyrightAndLicense:
        """
        Creates a new copyright attribution and license container.
        New copyright attributions and licenses can be added.

        The following creative commons licenses are included by default:
        The fist value is the reference ID to reference in the attribute.
            - ID: CC-BY | URI: https://creativecommons.org/licenses/by/4.0/
            - ID: CC-BY-SA | URI: https://creativecommons.org/licenses/by-sa/4.0/
            - ID: CC-BY-NC | URI: https://creativecommons.org/licenses/by-nc/4.0/
            - ID: CC-BY-NC-SA | URI: https://creativecommons.org/licenses/by-nc-sa/4.0/
            - ID: CC-BY-ND | URI: https://creativecommons.org/licenses/by-nd/4.0/
            - ID: CC-BY-NC-ND | URI: https://creativecommons.org/licenses/by-nc-nd/4.0/
            - ID: CC0 | URI: https://creativecommons.org/publicdomain/zero/1.0/

        Returns:
            A CopyrightAndLicense object with the default licenses.
        """
        return CopyrightAndLicense(license=CREATIVE_COMMONS_LICENSES)

    def add_copyright_attribution(self, id_: str, text: str) -> CopyrightAndLicense:
        """
        Add a new copyright attribution element.
        Please note that the id must be unique, this will raise an error if it is not.

        Args:
            id_: ID which is referenced in the attributes of the XML
            text: Text that should be displayed in the APP.

        Returns:
            The original CopyrightAndLicense with the added copyright attribution.
        """
        if id_ in self._get_copyright_attribution_ids():
            raise InputError(
                f"Copyright attribution with the ID '{id_}' and the text '{text}' already exists. "
                f"All IDs must be unique."
            )
        self.copyright_attribution.append(CopyrightAttribution(id_, text))
        return self

    def add_copyright_attribution_with_dict(self, copyright_dict: dict[str, str]) -> CopyrightAndLicense:
        """
        Add a several new copyright attribution elements from a dictionary.
        Please note that the id must be unique, this will raise an error if it is not.

        Args:
            copyright_dict: the dictionary should have the following structure: { id: text }

        Returns:
            The original CopyrightAndLicense with the added copyright attributions.
        """
        if ids_exist := set(copyright_dict.keys()).intersection(self._get_copyright_attribution_ids()):
            raise InputError(
                f"The following copyright IDs already exist: {", ".join(ids_exist)}. All IDs must be unique."
            )
        copyright_list = [CopyrightAttribution(k, v) for k, v in copyright_dict.items()]
        self.copyright_attribution.extend(copyright_list)
        return self

    def _get_copyright_attribution_ids(self) -> set[str]:
        return {x.id_ for x in self.copyright_attribution}

    def add_license(self, id_: str, text: str, uri: Any = None) -> CopyrightAndLicense:
        """
        Add a new license element.
        Please note that the id must be unique, this will raise an error if it is not.

        Args:
            id_: ID which is referenced in the attributes of the XML
            text: Text that should be displayed in the APP.
            uri: Optional URI liking to the license documentation.
            A pd.isna() check is done before adding the URI, therefore any value is permissible.

        Returns:
            The original CopyrightAndLicense with the added license.
        """
        if id_ in self._get_license_ids():
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
        Please note that the id must be unique, this will raise an error if it is not.

        Args:
            license_dict: dictionary with the information for license elements.
            It should have the following structure: { id: (text, uri) }
            A pd.isna() check is done before adding the URI, therefore, any value is permissible.

        Returns:
            The original CopyrightAndLicense with the added licenses.
        """
        for license_id, info_tuple in license_dict:
            self.add_license(license_id, info_tuple[0], info_tuple[1])
        return self

    def _get_license_ids(self) -> set[str]:
        return {x.id_ for x in self.license}


@dataclass
class CopyrightAttribution:
    id_: str
    text: str

    @staticmethod
    def create_new(id_: str, text: str) -> CopyrightAttribution:
        pass


@dataclass
class License:
    id_: str
    text: str
    uri: str | None

    @staticmethod
    def create_new(id_: str, text: str, uri: str | None = None) -> License:
        pass


CREATIVE_COMMONS_LICENSES = [
    License("CC-BY", "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
    License("CC-BY-SA", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
    License("CC-BY-NC", "CC BY-NC 4.0", "https://creativecommons.org/licenses/by-nc/4.0/"),
    License("CC-BY-NC-SA", "CC BY-NC-SA 4.0", "https://creativecommons.org/licenses/by-nc-sa/4.0/"),
    License("CC-BY-ND", "CC BY-ND 4.0", "https://creativecommons.org/licenses/by-nd/4.0/"),
    License("CC-BY-NC-ND", "CC BY-NC-ND 4.0", "https://creativecommons.org/licenses/by-nc-nd/4.0/"),
    License("CC0", "CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
]
