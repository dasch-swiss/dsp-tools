from typing import Any

from loguru import logger

from dsp_tools.clients.group_user_clients import GroupClient
from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import CreateProblem
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.input_problems import UploadProblem
from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.server_project_info import GroupNameToIriLookup
from dsp_tools.commands.create.serialisation.project import serialise_one_group


def create_groups(
    groups: list[ParsedGroup],
    group_client: GroupClient,
    project_iri: str,
    group_lookup: GroupNameToIriLookup,
) -> tuple[GroupNameToIriLookup, CollectedProblems | None]:
    problems: list[CreateProblem] = []
    for gr in groups:
        if group_lookup.check_exists(gr.name):
            logger.debug(f"Group with the name '{gr.name}' already exists, skipping.")
            continue
        result = _create_one_group(gr, group_client, project_iri)
        if isinstance(result, UploadProblem):
            problems.append(result)
        else:
            group_lookup.add_iri(gr.name, result)
    all_problems = None
    if problems:
        all_problems = CollectedProblems("During the creation of the groups the following problems happened:", problems)
    return group_lookup, all_problems


def _create_one_group(group: ParsedGroup, group_client: GroupClient, project_iri: str) -> str | UploadProblem:
    serialised = serialise_one_group(group, project_iri)
    new_iri = group_client.create_new_group(serialised)
    if new_iri:
        return new_iri
    return UploadProblem(group.name, ProblemType.GROUP_COULD_NOT_BE_CREATED)


def get_existing_group_to_iri_lookup(group_client: GroupClient, project_iri: str) -> GroupNameToIriLookup:
    all_groups = group_client.get_all_groups()
    return _construct_group_lookup(all_groups, project_iri)


def _construct_group_lookup(all_groups: list[dict[str, Any]], project_iri: str) -> GroupNameToIriLookup:
    name2iri = {}
    for group in all_groups:
        group_project_iri = group["project"]["id"]
        if group_project_iri == project_iri:
            name2iri[group["name"]] = group["id"]
    return GroupNameToIriLookup(name2iri=name2iri)
