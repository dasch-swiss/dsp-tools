# sourcery skip: use-fstring-for-concatenation

import itertools
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class OntoInfo:
    """This class saves the properties and the classes from an ontology."""

    classes: list[str] = field(default_factory=list)
    properties: list[str] = field(default_factory=list)


@dataclass
class OntoCheckInformation:
    """This class saves information needed to check the consistency with the ontology."""

    default_ontology_prefix: str
    onto_lookup: dict[str, OntoInfo]
    save_location: Path


@dataclass(frozen=True)
class InvalidOntologyElements:
    """This class saves and prints out the information regarding ontology classes and properties
    that are in the XML but not the ontology."""

    classes: list[tuple[str, list[str], str]]
    properties: list[tuple[str, list[str], str]]

    def execute_problem_protocol(self) -> tuple[str, pd.DataFrame | None]:
        """
        If there are any elements in properties or classes,
        this method composes an error message.

        Returns:
            the error message and a dataframe with the errors if they exceed 50 or None
        """
        extra_separator = "\n\n---------------------------------------\n\n"
        msg = "\nSome property and/or class type(s) used in the XML are unknown:" + extra_separator
        cls_msg = self._compose_problem_string_cls()
        if cls_msg:
            msg += cls_msg + extra_separator
        prop_msg = self._compose_problem_string_props()
        if prop_msg:
            msg += prop_msg
        if len(self.classes) + len(self.properties) > 50:
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

    def _compose_problem_string_cls(self) -> str | None:
        if self.classes:
            separator = "\n----------------------------\n"

            def _format_cls(cls_tup: tuple[str, list[str], str]) -> str:
                ids = "\n\t- " + "\n\t- ".join(cls_tup[1])
                return f"\tResource Type: '{cls_tup[0]}'\n\tProblem: '{cls_tup[2]}'\n\tResource ID(s):{ids}"

            problems = [_format_cls(x) for x in self.classes]

            return "The following resource(s) have an invalid resource type:\n\n" + separator.join(problems)
        else:
            return None

    def _compose_problem_string_props(self) -> str | None:
        if self.properties:
            separator = "\n----------------------------\n"

            def _format_prop(prop_tup: tuple[str, list[str], str]) -> str:
                ids = "\n\t- " + "\n\t- ".join(prop_tup[1])
                return f"\tProperty Name: '{prop_tup[0]}'\n\tProblem: '{prop_tup[2]}'\n\tResource ID(s):{ids}"

            problems = [_format_prop(x) for x in self.properties]
            return "The following resource(s) have invalid property type(s):\n\n" + separator.join(problems)
        else:
            return None
