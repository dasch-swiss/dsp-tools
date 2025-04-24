from copy import deepcopy

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedRichtext
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStash
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash


def stash_circular_references(resources: list[ProcessedResource], stash_lookup: dict[str, list[str]]) -> Stash | None:
    """Stash the values that would create circular references and remove them from the Resources."""
    stashed_link_values: list[LinkValueStashItem] = []
    stashed_standoff_values: list[StandoffStashItem] = []

    if not stash_lookup:
        return None

    for res in resources:
        if res.res_id not in stash_lookup:
            continue
        links, standoff = _process_one_resource(res, stash_lookup)
        stashed_link_values.extend(links)
        stashed_standoff_values.extend(standoff)

    standoff_stash = StandoffStash.make(stashed_standoff_values)
    link_value_stash = LinkValueStash.make(stashed_link_values)
    return Stash.make(standoff_stash=standoff_stash, link_value_stash=link_value_stash)


def _process_one_resource(
    resource: ProcessedResource,
    stash_lookup: dict[str, list[str]],
) -> tuple[list[LinkValueStashItem], list[StandoffStashItem]]:
    stashed_link_values: list[LinkValueStashItem] = []
    stashed_standoff_values: list[StandoffStashItem] = []

    for val in resource.values.copy():
        if isinstance(val, ProcessedLink):
            if val.value_uuid not in stash_lookup[resource.res_id]:
                continue
            stashed_link_values.append(LinkValueStashItem(resource.res_id, resource.type_iri, val))
            resource.values.remove(val)
        elif isinstance(val, ProcessedRichtext):
            if val.value_uuid not in stash_lookup[resource.res_id]:
                continue
            # val.value is a KnoraStandoffXml text with problematic links.
            # stash it, then replace the problematic text with a UUID
            stashed_standoff_values.append(_stash_standoff(val, resource.res_id, resource.type_iri))

    return stashed_link_values, stashed_standoff_values


def _stash_standoff(value: ProcessedRichtext, res_id: str, res_type: str) -> StandoffStashItem:
    original_value = deepcopy(value)
    # Replace the content with the UUID
    value.value = FormattedTextValue(value.value_uuid)
    # It is not necessary to add the permissions to the StandoffStashItem.
    # Because when no new permissions are given during an update request,
    # the permissions of the previous value are taken.
    return StandoffStashItem(
        res_id=res_id,
        res_type=res_type,
        value=original_value,
    )
