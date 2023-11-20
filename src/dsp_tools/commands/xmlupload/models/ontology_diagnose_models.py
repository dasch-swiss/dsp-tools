# sourcery skip: use-fstring-for-concatenation

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from dsp_tools.models.exceptions import UserError


@dataclass(frozen=True)
class Ontology:
    """This class saves the properties and the classes from an ontology."""

    classes: list[str] = field(default_factory=list)
    properties: list[str] = field(default_factory=list)


@dataclass
class OntoCheckInformation:
    """This class saves information that is needed to check if consistency with the ontology."""

    default_ontology_prefix: str
    onto_lookup: dict[str, Ontology]
    save_location: Path


@dataclass
class InvalidOntologyElements:
    """This class saves and prints out the information regarding ontology classes and properties
    that are in the XML but not the ontology."""

    save_path: Path
    classes: list[list[str]] = field(default_factory=list)
    properties: list[list[str]] = field(default_factory=list)

    def execute_problem_protocol(self) -> None:
        """
        This function is executed if there are any elements in properties or classes.
        If there are more than 100 entries combined, then the result is also saved as an excel.

        Raises:
            UserError: If properties or classes have any entries.
        """
        extra_separator = "\n----------------------------"
        msg = "Some property and or class type(s) used in the XML are unknown:" + extra_separator
        cls_msg = self._print_problem_string_cls()
        if cls_msg:
            msg += cls_msg + extra_separator
        prop_msg = self._print_problem_string_props()
        if prop_msg:
            msg += prop_msg
        if len(self.classes) + len(self.properties) > 50:
            ex_name = "InvalidOntologyElements_in_XML.xlsx"
            self._get_and_save_problems_as_excel(ex_name)
            msg += extra_separator + f"\nAn excel: '{ex_name}' was saved at '{self.save_path}' listing the problems."
        raise UserError(msg)

    def _get_and_save_problems_as_excel(self, excel_name) -> None:
        df = self._get_problems_as_df()
        df.to_excel(excel_writer=Path(self.save_path, excel_name), sheet_name=" ", index=False)

    def _get_problems_as_df(self) -> pd.DataFrame:
        problems = [
            {
                "resource id": x[0],
                "problematic type": x[1],
                "problem": x[2],
            }
            for x in self.classes
        ]
        problems.extend(
            [
                {
                    "resource id": x[0],
                    "problematic type": x[1],
                    "problem": x[2],
                }
                for x in self.properties
            ]
        )
        return pd.DataFrame.from_records(problems)

    def _print_problem_string_cls(self) -> str:
        if self.classes:
            separator = "\n----------------------------\n"
            problems = [
                f"\tResource ID: '{x[0]}'\n\tResource Type: '{x[1]}'\n\tProblem: '{x[2]}'" for x in self.classes
            ]
            return "The following resource(s) have an invalid resource type:\n" + separator.join(problems)
        else:
            return ""

    def _print_problem_string_props(self) -> str:
        if self.properties:
            separator = "\n----------------------------\n"
            problems = [
                f"\tResource ID: '{x[0]}'\n\tProperty Name: '{x[1]}'\n\tProblem: '{x[2]}'" for x in self.properties
            ]
            return "The following resource(s) have invalid property type(s):\n" + separator.join(problems)
        else:
            return ""
