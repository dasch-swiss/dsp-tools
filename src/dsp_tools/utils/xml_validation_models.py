from dataclasses import dataclass

import pandas as pd
from lxml import etree

list_separator = "\n    - "
medium_separator = "\n----------------------------\n"
grand_separator = "\n\n---------------------------------------\n\n"

maximum_prints = 50


@dataclass
class TextValueData:
    resource_id: str
    property_name: str
    encoding: set[str]


def check_if_only_one_encoding_is_used_per_prop_in_root(
    root: etree._Element,
) -> list[TextValueData]:
    """
    Check if all the encodings in the <text> elements are consistent within one <text-prop>

    This is correct:
    ```
    <text-prop name=":hasSimpleText">
        <text encoding="utf8">Text 1</text>
        <text encoding="utf8">Text 2</text>
    </text-prop>
    ```

    This is wrong:
    ```
    <text-prop name=":hasSimpleText">
        <text encoding="utf8">Text 1</text>
        <text encoding="xml">Text 2</text>
    </text-prop>
    ```

    Args:
        root: root of the data xml document

    Returns:
          True and None if all the elements are consistent
          False and a list of all the inconsistent <text-props>
    """
    text_props = _get_all_ids_and_encodings_from_root(root)
    return _check_only_one_valid_encoding_used_all_props(text_props)


def _get_all_ids_and_encodings_from_root(
    root: etree._Element,
) -> list[TextValueData]:
    res_list = []
    for res_input in root.iterchildren(tag="resource"):
        res_list.extend(_get_encodings_from_one_resource(res_input))
    return res_list


def _get_encodings_from_one_resource(resource: etree._Element) -> list[TextValueData]:
    res_id = resource.attrib["id"]
    return [_get_encodings_from_one_property(res_id, child) for child in list(resource.iterchildren(tag="text-prop"))]


def _get_encodings_from_one_property(res_id: str, property: etree._Element) -> TextValueData:
    prop_name = property.attrib["name"]
    encodings = {x.attrib["encoding"] for x in property.iterchildren()}
    return TextValueData(res_id, prop_name, encodings)


def _check_only_one_valid_encoding_used_all_props(text_props: list[TextValueData]) -> list[TextValueData]:
    return [x for x in text_props if not len(x.encoding) == 1]


@dataclass
class InconsistentTextValueEncodings:
    """
    This class implements the `Problem` protocol
    for resources and properties that contain invalid encodings.

    An invalid encoding would be a <text-prop> element, that contains
    <text encoding="utf8">
    and
    <text encoding="xml">
    """

    problematic_resources: list[TextValueData]

    def execute_problem_protocol(self) -> tuple[str, pd.DataFrame | None]:
        """
        This method composes an error message for the user.
        If the number of errors exceeds `maximum_prints`,
        the errors are additionally returned as a dataframe that can be saved as a CSV file.

        Returns:
            the error message, and optionally a dataframe with the errors
        """
        base_msg = (
            "\nSome <text-prop> elements contain <text> elements that use both 'xml' and 'utf8' encoding.\n"
            "Only one encoding type can be used within one <text-prop> element."
        )
        df = self._get_problems_as_df()
        if len(df) > maximum_prints:
            return base_msg, df
        return base_msg + grand_separator + self._make_msg_from_df(df), None

    def _get_problems_as_df(self) -> pd.DataFrame:
        df = pd.DataFrame(
            {
                "Resource ID": [x.resource_id for x in self.problematic_resources],
                "Property Name": [x.property_name for x in self.problematic_resources],
            }
        )
        return df.sort_values(by=["Resource ID", "Property Name"], ignore_index=True)

    @staticmethod
    def _make_msg_from_df(df: pd.DataFrame) -> str:
        groups = df.groupby(by="Resource ID")
        return medium_separator.join(
            [InconsistentTextValueEncodings._make_msg_for_one_resource(str(_id), res_df) for _id, res_df in groups]
        )

    @staticmethod
    def _make_msg_for_one_resource(res_id: str, res_df: pd.DataFrame) -> str:
        problems = [f"Property Name: '{p}'" for p in res_df["Property Name"].tolist()]
        return f"Resource ID: '{res_id}'{list_separator}{list_separator.join(problems)}"
