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


def check_if_only_one_encoding_is_used_in_xml(root: etree._Element) -> tuple[bool, list[TextValueData] | None]:
    """
    This function analyses if all the encodings in the <text> elements are consistent within one <text-prop>

    This is correct:
    ```
    <text-prop name=":hasSimpleText">
        <text permissions="prop-default" encoding="utf8">Text 1</text>
        <text permissions="prop-default" encoding="utf8">Text 2</text>
    </text-prop>
    ```

    This is wrong:
    ```
    <text-prop name=":hasSimpleText">
        <text permissions="prop-default" encoding="utf8">Text 1</text>
        <text permissions="prop-default" encoding="xml">Text 2</text>
    </text-prop>
    ```

    Args:
        root: root of the data xml document

    Returns:
          True and None if all the elements are consistent
          False and a list of all the inconsistent <text-props>
    """
    text_props = _get_all_ids_prop_encoding_from_root(root)
    if (checked_props := _check_only_one_valid_encoding_used_all_props(text_props)) is not None:
        return False, checked_props
    return True, None


def _get_all_ids_prop_encoding_from_root(root: etree._Element) -> list[TextValueData]:
    res_list = []
    for res_input in root.iterchildren(tag="resource"):
        if (res_result := _get_id_prop_encoding_from_one_resource(res_input)) is not None:
            res_list.extend(res_result)
    return res_list


def _get_id_prop_encoding_from_one_resource(resource: etree._Element) -> list[TextValueData] | None:
    if not (children := list(resource.iterchildren(tag="text-prop"))):
        return None
    res_id = resource.attrib["id"]
    return [_get_prop_encoding_from_one_property(res_id, child) for child in children]


def _get_prop_encoding_from_one_property(res_id: str, property: etree._Element) -> TextValueData:
    prop_name = property.attrib["name"]
    child_attrib = [x.attrib for x in property.iterchildren()]
    encodings = {x["encoding"] for x in child_attrib}
    return TextValueData(res_id, prop_name, encodings)


def _check_only_one_valid_encoding_used_all_props(text_props: list[TextValueData]) -> list[TextValueData] | None:
    wrong_props = [x for x in text_props if not _check_only_one_valid_encoding_used_one_prop(x.encoding)]
    if len(wrong_props) == 0:
        return None
    return wrong_props


def _check_only_one_valid_encoding_used_one_prop(text_encodings: set[str]) -> bool:
    if text_encodings == {"xml"} or text_encodings == {"utf8"}:  # noqa: PLR1714
        return True
    return False


@dataclass
class InconsistentTextValueEncodings:
    """
    This class takes instances that contain the information about resources and the properties that contain
    invalid encodings.

    An invalid encoding would be a <text-prop> element, that contains
    <text encoding="utf8">
    and
    <text encoding="xml">
    It is responsible to communicate the problems to the user.
    """

    problematic_resources: list[TextValueData]

    def execute_problem_protocol(self) -> tuple[str, pd.DataFrame | None]:
        """
        This method composes an error message for the user.
        Returns:
            the error message and a dataframe with the errors if they exceed 50
        """
        msg = (
            "\nSome <text-prop> elements contain <text> elements that use both 'xml' and 'utf8' encoding.\n"
            "Only one encoding type can be used per <text-prop> element."
        )
        df = self._get_problems_as_df()
        if len(df) > maximum_prints:
            return msg, df
        additional_msg = self._make_msg_from_df(df)
        return msg + grand_separator + additional_msg, None

    def _get_problems_as_df(self) -> pd.DataFrame:
        df = pd.DataFrame(
            {
                "Resource ID": list(x.resource_id for x in self.problematic_resources),
                "Property Name": list(x.property_name for x in self.problematic_resources),
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
