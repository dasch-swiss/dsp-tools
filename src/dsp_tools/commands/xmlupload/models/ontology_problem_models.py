import itertools
from dataclasses import dataclass

import pandas as pd

from dsp_tools.commands.xmlupload.models.ontology_lookup_models import TextValueData

separator = "\n    "
list_separator = "\n    - "
medium_separator = "\n\n"
maximum_prints = 50


@dataclass(frozen=True)
class InvalidOntologyElementsInData:
    """This class saves and prints out the information regarding ontology classes and properties
    that are in the XML but not the ontology."""

    classes: list[tuple[str, list[str], str]]
    properties: list[tuple[str, list[str], str]]
    ontos_on_server: list[str]

    def execute_problem_protocol(self) -> tuple[str, pd.DataFrame | None]:
        """
        If there are any elements in properties or classes,
        this method composes an error message.

        Returns:
            the error message and a dataframe with the errors if they exceed 50 or None
        """
        base_msg = (
            f"\nSome property and/or class type(s) used in the XML are unknown.\n"
            f"The ontologies for your project on the server are:{list_separator}"
            f"{list_separator.join(self.ontos_on_server)}{medium_separator}"
        )
        if cls_msg := self._compose_problem_string_for_cls():
            base_msg += cls_msg + "\n"
        if prop_msg := self._compose_problem_string_for_props():
            base_msg += prop_msg + "\n"
        if (
            self._calculate_num_resources(self.classes) + self._calculate_num_resources(self.properties)
            > maximum_prints
        ):
            df = self._get_problems_as_df()
            return base_msg, df
        return base_msg, None

    def _get_problems_as_df(self) -> pd.DataFrame:
        problems = [
            [
                {
                    "problematic type": probs[0],
                    "resource id": x,
                    "problem": probs[2],
                }
                for x in probs[1]
            ]
            for probs in self.classes
        ]
        problems.extend(
            [
                [
                    {
                        "problematic type": probs[0],
                        "resource id": x,
                        "problem": probs[2],
                    }
                    for x in probs[1]
                ]
                for probs in self.properties
            ]
        )
        unpacked: list[dict[str, str]] = list(itertools.chain(*problems))
        return pd.DataFrame.from_records(unpacked)

    def _calculate_num_resources(self, to_count: list[tuple[str, list[str], str]]) -> int:
        return sum((len(x[1]) for x in to_count))

    def _compose_problem_string_for_cls(self) -> str | None:
        if self.classes:
            if self._calculate_num_resources(self.classes) > maximum_prints:
                return "Many resources have an invalid resource type.\nPlease consult the file for details."

            def _format_cls(cls_tup: tuple[str, list[str], str]) -> str:
                ids = list_separator + list_separator.join(cls_tup[1])
                return (
                    f"    Resource Type: '{cls_tup[0]}'{separator}"
                    f"Problem: '{cls_tup[2]}'{separator}"
                    f"Resource ID(s):{ids}"
                )

            problems = [_format_cls(x) for x in self.classes]

            return (
                f"The following resource(s) have an invalid resource type:{medium_separator}"
                + medium_separator.join(problems)
                + "\n"
            )
        else:
            return None

    def _compose_problem_string_for_props(self) -> str | None:
        if self.properties:
            if self._calculate_num_resources(self.properties) > maximum_prints:
                return "Many properties have an invalid resource type.\nPlease consult the file for details."

            def _format_prop(prop_tup: tuple[str, list[str], str]) -> str:
                ids = list_separator + list_separator.join(prop_tup[1])
                return (
                    f"    Property Name: '{prop_tup[0]}'{separator}"
                    f"Problem: '{prop_tup[2]}'{separator}"
                    f"Resource ID(s):{ids}"
                )

            problems = [_format_prop(x) for x in self.properties]
            return (
                f"The following resource(s) have invalid property type(s):{medium_separator}"
                + medium_separator.join(problems)
                + "\n"
            )
        else:
            return None


@dataclass
class InvalidTextValueEncodings:
    """
    This class contains information about resources and the respective properties that have invalid text encodings.

    An invalid encoding would be a property that specifies `knora-api:Richtext` in the ontology,
        but the `<text>` elements use: `<text encoding="utf8">`.
    OR
    A property that specifies `knora-api:Textarea` or `knora-api:SimpleText`
        but the `<text>` elements use: `<text encoding="xml">`.
    """

    problematic_resources: list[TextValueData]

    def execute_problem_protocol(self) -> tuple[str, pd.DataFrame | None]:
        """
        This method composes an error message for the user.

        Returns:
            the error message and a dataframe with the errors if they exceed the maximum allowed print statements
        """
        base_msg = (
            "\nSome text encodings used in the XML data file are not conform with the gui_element "
            "specified in the JSON ontology.\n"
            "Please consult the ontology regarding the assigned gui_elements."
        )
        df = self._get_problems_as_df()
        if len(df) > maximum_prints:
            return base_msg, df
        return base_msg + medium_separator + _make_msg_from_df(df), None

    def _get_problems_as_df(self) -> pd.DataFrame:
        df = pd.DataFrame(
            {
                "Resource ID": [x.resource_id for x in self.problematic_resources],
                "Resource Type": [x.res_type for x in self.problematic_resources],
                "Property Name": [x.property_name for x in self.problematic_resources],
                "Encoding Used": [x.encoding for x in self.problematic_resources],
            }
        )
        return df.sort_values(by=["Resource Type", "Resource ID", "Property Name"], ignore_index=True)


def _make_msg_from_df(df: pd.DataFrame) -> str:
    groups = df.groupby(by="Resource ID")
    return medium_separator.join([_make_msg_for_one_resource(str(_id), res_df) for _id, res_df in groups])


def _make_msg_for_one_resource(res_id: str, res_df: pd.DataFrame) -> str:
    props = res_df["Property Name"].tolist()
    encding = res_df["Encoding Used"].tolist()
    restype = next(iter(res_df["Resource Type"]))
    problems = [f"Property Name: '{p}' -> Encoding Used: '{e}'" for p, e in zip(props, encding)]
    return f"Resource ID: '{res_id}' | Resource Type: '{restype}'{list_separator}{list_separator.join(problems)}"
