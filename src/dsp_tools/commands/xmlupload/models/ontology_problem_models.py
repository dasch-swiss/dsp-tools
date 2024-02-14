import itertools
from dataclasses import dataclass

import pandas as pd

from dsp_tools.commands.xmlupload.models.ontology_lookup_models import TextValueData

separator = "\n    "
list_separator = "\n    - "
medium_separator = "\n----------------------------\n"
grand_separator = "\n\n---------------------------------------\n\n"
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
        msg = (
            f"\nSome property and/or class type(s) used in the XML are unknown.\n"
            f"The ontologies for your project on the server are:{list_separator}"
            f"{list_separator.join(self.ontos_on_server)}{grand_separator}"
        )
        cls_msg = self._compose_problem_string_for_cls()
        if cls_msg:
            msg += cls_msg + grand_separator
        prop_msg = self._compose_problem_string_for_props()
        if prop_msg:
            msg += prop_msg
        if (
            self._calculate_num_resources(self.classes) + self._calculate_num_resources(self.properties)
            > maximum_prints
        ):
            df = self._get_problems_as_df()
            return msg, df
        return msg, None

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

            return "The following resource(s) have an invalid resource type:\n\n" + medium_separator.join(problems)
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
            return "The following resource(s) have invalid property type(s):\n\n" + medium_separator.join(problems)
        else:
            return None


@dataclass
class InvalidTextValueEncodings:
    """This class takes instances that contain the information about resources and the properties that contain
    invalid encodings.
    It is responsible to communicate the problems to the user."""

    problematic_resources: list[TextValueData]

    def execute_problem_protocol(self) -> tuple[str, pd.DataFrame | None]:
        """
        This method composes an error message for the user.

        Returns:
            the error message and a dataframe with the errors if they exceed 50
        """
        msg = "\nSome text encodings used in the data is not conform with the gui-element specified in the ontology.\n"
        df = self._get_problems_as_df()
        if len(df) > maximum_prints:
            return msg, df
        additional_msg = self._make_msg_from_df(df)
        return msg + grand_separator + additional_msg, None

    def _get_problems_as_df(self) -> pd.DataFrame:
        def join_mixed_types(in_set: set[str | None]) -> str:
            return ", ".join([str(x) for x in in_set])

        df = pd.DataFrame(
            {
                "Resource ID": list(x.resource_id for x in self.problematic_resources),
                "Property Name": list(x.property_name for x in self.problematic_resources),
                "Encoding(s) Used": list(join_mixed_types(x.encoding) for x in self.problematic_resources),
            }
        )
        return df.sort_values(by=["Resource ID", "Property Name"], ignore_index=True)

    @staticmethod
    def _make_msg_from_df(df: pd.DataFrame) -> str:
        groups = df.groupby(by="Resource ID")
        return medium_separator.join(
            [InvalidTextValueEncodings._make_msg_for_one_resource(str(_id), res_df) for _id, res_df in groups]
        )

    @staticmethod
    def _make_msg_for_one_resource(res_id: str, res_df: pd.DataFrame) -> str:
        props = res_df["Property Name"].tolist()
        encding = res_df["Encoding(s) Used"].tolist()
        problems = [f"Property Name: '{p}' -> Encoding(s) Used: '{e}'" for p, e in zip(props, encding)]
        return f"Resource ID: '{res_id}'{list_separator}{list_separator.join(problems)}"
