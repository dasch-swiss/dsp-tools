from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStash
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash


def stash_circular_references(
    resources: list[IntermediaryResource], stash_lookup: dict[str, list[str]]
) -> Stash | None:
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
    resource: IntermediaryResource,
    stash_lookup: dict[str, list[str]],
) -> tuple[list[LinkValueStashItem], list[StandoffStashItem]]:
    stashed_link_values: list[LinkValueStashItem] = []
    stashed_standoff_values: list[StandoffStashItem] = []

    for val in resource.values.copy():
        if isinstance(val, IntermediaryLink):
            if val.value_uuid not in stash_lookup[resource.res_id]:
                continue
            stashed_link_values.append(_stash_link(val, resource.res_id, resource.type_iri))
            resource.values.remove(val)
        elif isinstance(val, IntermediaryRichtext):
            if val.value_uuid not in stash_lookup[resource.res_id]:
                continue
            # val.value is a KnoraStandoffXml text with problematic links.
            # stash it, then replace the problematic text with a UUID
            stashed_standoff_values.append(_stash_standoff(val, resource.res_id, resource.type_iri))

    return stashed_link_values, stashed_standoff_values


def _stash_link(
    value: IntermediaryLink,
    res_id: str,
    res_type: str,
) -> LinkValueStashItem:
    return LinkValueStashItem(
        res_id=res_id,
        res_type=res_type,
        prop_name=value.prop_iri,
        target_id=value.value,
        permission=str(value.permissions) if value.permissions else None,
    )


def _stash_standoff(value: IntermediaryRichtext, res_id: str, res_type: str) -> StandoffStashItem:
    actual_text = value.value
    # Replace the content with the UUID
    value.value = FormattedTextValue(value.value_uuid)
    # It is not necessary to add the permissions to the StandoffStashItem.
    # Because when no new permissions are given during an update request,
    # the permissions of the previous value are taken.
    return StandoffStashItem(
        res_id=res_id,
        res_type=res_type,
        uuid=value.value_uuid,
        prop_name=value.prop_iri,
        value=actual_text,
    )
