from __future__ import annotations

from typing import Any

from dsp_tools.connection.connection import Connection
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.xmlupload.consistency_check_model import ProjectOntology

logger = get_logger(__name__)


def _get_project_ontology_names_from_server(con: Connection, project_shortcode: str) -> list[str]:
    project_info = con.get(f"/admin/projects/shortcode/{project_shortcode}")
    ontologies = project_info["project"]["ontologies"]
    return [x.split("/")[-1] for x in ontologies]


def _get_all_project_ontologies_from_server(
    con: Connection, project_shortcode: str, ontology_names: list[str]
) -> dict[str, list[dict[str, Any]]]:
    onto_dict = dict()
    for onto in ontology_names:
        onto_dict[onto] = _get_single_ontology_from_server(con, project_shortcode, onto)
    return onto_dict


def _get_single_ontology_from_server(con: Connection, project_shortcode: str, ontology_name: str) -> ProjectOntology:
    onto_list: dict[str, list[dict[str, Any]]] = con.get(f"/ontology/{project_shortcode}/{ontology_name}/v2")
    return ProjectOntology.make(ontology_info=onto_list["@graph"], ontology_name=ontology_name)
