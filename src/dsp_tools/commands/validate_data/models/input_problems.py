from __future__ import annotations

import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path

import regex
from loguru import logger
from rdflib import Graph

from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.error.custom_warnings import DspToolsUserWarning

LIST_SEPARATOR = "\n    - "
GRAND_SEPARATOR = "\n\n----------------------------\n"


@dataclass
class OntologyValidationProblem:
    problems: list[OntologyResourceProblem]

    def get_msg(self) -> str:
        probs = sorted(self.problems, key=lambda x: x.res_iri)
        problems = [x.get_msg() for x in probs]
        return (
            "The ontology structure contains errors that prevent the validation of the data.\n"
            "Please correct the following errors and re-upload the corrected ontology.\n"
            f"Once those two steps are done, the command `validate-data` will find any problems in the data.\n"
            f"{LIST_SEPARATOR}{LIST_SEPARATOR.join(problems)}"
        )


@dataclass
class OntologyResourceProblem:
    res_iri: str
    msg: str

    def get_msg(self) -> str:
        return f"Resource Class: {self.res_iri} | Problem: {self.msg}"


@dataclass
class UnknownClassesInData:
    unknown_classes: set[str]
    defined_classes: set[str]

    def __post_init__(self) -> None:
        self.unknown_classes = {reformat_onto_iri(x) for x in self.unknown_classes}
        self.defined_classes = {reformat_onto_iri(x) for x in self.defined_classes}

    def get_msg(self) -> str:
        if unknown := self._get_unknown_ontos_msg():
            return unknown
        return self._get_unknown_classes_msg()

    def _get_unknown_ontos_msg(self) -> str:
        def split_prefix(relative_iri: str) -> str | None:
            if ":" not in relative_iri:
                return None
            return relative_iri.split(":")[0]

        used_ontos = set(not_knora for x in self.unknown_classes if (not_knora := split_prefix(x)))
        exising_ontos = set(not_knora for x in self.defined_classes if (not_knora := split_prefix(x)))
        msg = ""
        if unknown := used_ontos - exising_ontos:
            msg = (
                f"Your data uses ontologies that don't exist in the database.\n"
                f"The following ontologies that are used in the data are unknown: {', '.join(unknown)}\n"
                f"The following ontologies are uploaded: {', '.join(exising_ontos)}"
            )
        return msg

    def _get_unknown_classes_msg(self) -> str:
        unknown_classes = sorted(list(self.unknown_classes))
        known_classes = sorted(list(self.defined_classes))
        return (
            f"Your data uses resource classes that do not exist in the ontologies in the database.\n"
            f"The following classes that are used in the data are unknown: {', '.join(unknown_classes)}\n"
            f"The following classes exist in the uploaded ontologies: {', '.join(known_classes)}"
        )


@dataclass
class UnexpectedResults:
    components: list[str]

    def save_inform_user(self, results_graph: Graph, shacl: Graph, data: Graph) -> None:
        cwdr = Path.cwd()
        prefix = f"{datetime.now()!s}_"
        components = sorted(self.components)
        logger.info(f"Unexpected components found: {', '.join(components)}")
        msg = (
            f"Unexpected violations were found in the validation results:"
            f"{LIST_SEPARATOR}{LIST_SEPARATOR.join(components)}\n"
            f"Please contact the development team with the files starting with the timestamp '{prefix}' "
            f"in the directory '{cwdr}'."
        )
        save_path = cwdr / f"{prefix}validation_result.ttl"
        results_graph.serialize(save_path)
        shacl_p = cwdr / f"{prefix}shacl.ttl"
        shacl.serialize(shacl_p)
        data_p = cwdr / f"{prefix}data.ttl"
        data.serialize(data_p)
        warnings.warn(DspToolsUserWarning(msg))


@dataclass
class AllProblems:
    problems: list[InputProblem]
    unexpected_results: list[UnexpectedComponent]


@dataclass
class SortedProblems:
    unique_violations: list[InputProblem]
    user_info: list[InputProblem]
    unexpected_shacl_validation_components: list[str]


@dataclass
class UserPrintMessages:
    problems: str | None
    referenced_absolute_iris: str | None


@dataclass
class InputProblem:
    problem_type: ProblemType
    res_id: str
    res_type: str
    prop_name: str
    message: str | None = None
    input_value: str | None = None
    input_type: str | None = None
    expected: str | None = None

    def __post_init__(self) -> None:
        self.message = self._clean_input(self.message)
        self.expected = self._clean_input(self.expected)

    def _clean_input(self, to_clean: str | None) -> str | None:
        if not to_clean:
            return None
        if not regex.search(r"\S+", to_clean):
            return None
        str_split = [content for x in to_clean.split(" ") if (content := x.strip())]
        return " ".join(str_split)


class ProblemType(StrEnum):
    GENERIC = "generic"
    FILE_VALUE = "file problem"
    MAX_CARD = "Maximum Cardinality Violation"
    MIN_CARD = "Minimum Cardinality Violation"
    NON_EXISTING_CARD = "The resource class does not have a cardinality for this property."
    FILE_VALUE_PROHIBITED = "A file was added to the resource. This resource type must not have a file."
    VALUE_TYPE_MISMATCH = "Value Type Mismatch"
    INPUT_REGEX = "Wrong Format of Input"
    LINK_TARGET_TYPE_MISMATCH = "Linked Resource Type Mismatch"
    INEXISTENT_LINKED_RESOURCE = "Linked Resource does not exist"
    DUPLICATE_VALUE = "Your input is duplicated"
