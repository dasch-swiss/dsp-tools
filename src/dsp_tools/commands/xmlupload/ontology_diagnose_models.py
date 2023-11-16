# sourcery skip: use-fstring-for-concatenation

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import regex
from regex import Pattern

from dsp_tools.models.exceptions import UserError


@dataclass(frozen=True)
class Ontology:
    """This class saves the properties and the classes from an ontology."""

    classes: list[str] = field(default_factory=list)
    properties: list[str] = field(default_factory=list)


@dataclass
class OntoDiagnoseTool:
    """This class returns the regex for the ontology"""

    default_ontology_prefix: str
    onto_lookup: dict[str, Ontology]
    save_location: Path
    default_ontology_colon: Pattern[str] = field(default=regex.compile(r"^:[A-Za-z]+$"))
    knora_undeclared: Pattern[str] = field(default=regex.compile(r"^[A-Za-z]+$"))
    generic_prefixed_ontology: Pattern[str] = field(default=regex.compile(r"^[A-Za-z]+-?[A-Za-z]+:[A-Za-z]+$"))


@dataclass
class UnknownOntologyElements:
    """This class saves
    and puts out the information ontology classes and properties that are in the XML but not the ontology."""

    save_path: Path
    classes: list[tuple[str, str]] = field(default_factory=list)
    properties: list[tuple[str, str]] = field(default_factory=list)

    def not_empty(self) -> bool:
        """
        Returns false if there are no classes or properties saved.

        Returns:
            bool
        """
        return any([self.classes, self.properties])

    def execute_problem_protocol(self) -> None:
        """
        This function is executed if there are any elements in properties or classes.
        If there are more than 100 entries combined, then the result is also saved as an excel.

        Raises:
            UserError: If properties or classes has any entries the problems.
        """
        if len(self.classes) + len(self.properties) > 100:
            self._save_problems_as_excel()
        cls_msg = self._print_problem_string_cls()
        prop_msg = self._print_problem_string_props()
        raise UserError("Some property and or class type(s) used in the XML are unknown:\n" + cls_msg + prop_msg)

    def _save_problems_as_excel(self) -> None:
        cls_di = {
            "type": "resources",
            "resource id": [x[0] for x in self.classes],
            "problematic type": [x[1] for x in self.classes],
        }
        prop_di = {
            "type": "property",
            "resource id": [x[0] for x in self.properties],
            "problematic type": [x[1] for x in self.properties],
        }
        df = pd.DataFrame.from_records([cls_di, prop_di])
        df.to_excel(
            excel_writer=Path(self.save_path, "ProblematicOntologyElements_in_XML.xlsx"), sheet_name=" ", index=False
        )

    def _print_problem_string_cls(self) -> str:
        if self.classes:
            problems = [f"\tResource ID: {x[0]}, Resource Type: {x[1]}" for x in self.classes]
            return "\n\tThe following resources have an invalid resource type:\n\t" + "\n\t- ".join(problems)
        else:
            return ""

    def _print_problem_string_props(self) -> str:
        if self.properties:
            problems = [f"\tResource ID: {x[0]}, Property Name: {x[1]}" for x in self.properties]
            return "\n\tThe following resources have an invalid property type(s):\n\t" + "\n\t- ".join(problems)
        else:
            return ""
