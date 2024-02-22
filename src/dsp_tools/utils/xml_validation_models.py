from dataclasses import dataclass

import pandas as pd

list_separator = "\n    - "
medium_separator = "\n----------------------------\n"
grand_separator = "\n\n---------------------------------------\n\n"

maximum_prints = 50


@dataclass
class TextValueData:
    resource_id: str
    property_name: str
    encoding: set[str]


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
        return base_msg + grand_separator + _make_msg_from_df(df), None

    def _get_problems_as_df(self) -> pd.DataFrame:
        df = pd.DataFrame(
            {
                "Resource ID": [x.resource_id for x in self.problematic_resources],
                "Property Name": [x.property_name for x in self.problematic_resources],
            }
        )
        return df.sort_values(by=["Resource ID", "Property Name"], ignore_index=True)


def _make_msg_from_df(df: pd.DataFrame) -> str:
    groups = df.groupby(by="Resource ID")
    return medium_separator.join([_make_msg_for_one_resource(str(_id), res_df) for _id, res_df in groups])


def _make_msg_for_one_resource(res_id: str, res_df: pd.DataFrame) -> str:
    problems = [f"Property Name: '{p}'" for p in res_df["Property Name"].tolist()]
    return f"Resource ID: '{res_id}'{list_separator}{list_separator.join(problems)}"
