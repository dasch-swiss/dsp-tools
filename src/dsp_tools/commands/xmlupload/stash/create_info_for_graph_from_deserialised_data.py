import regex

from dsp_tools.commands.xmlupload.stash.graph_models import InfoForGraph
from dsp_tools.commands.xmlupload.stash.graph_models import LinkValueLink
from dsp_tools.commands.xmlupload.stash.graph_models import StandOffLink
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation


def create_info_for_graph_from_data(data: DataDeserialised) -> InfoForGraph:
    """Extracts information to create the graph to analyse the circular references."""
    all_links = []
    all_stand_off = []
    all_resource_ids = []
    for res in data.resources:
        links, stand_off = _process_one_resource(res)
        all_links.extend(links)
        all_stand_off.extend(stand_off)
        all_resource_ids.append(res.res_id)
    return InfoForGraph(
        all_resource_ids=all_resource_ids,
        link_values=all_links,
        standoff_links=all_stand_off,
    )


def _process_one_resource(resource: ResourceDeserialised) -> tuple[list[LinkValueLink], list[StandOffLink]]:
    link_values = []
    stand_off = []
    for val in resource.values:
        if val.knora_type == KnoraValueType.LINK_VALUE:
            link_values.append(_process_link_value(val, resource.res_id))
        elif val.knora_type == KnoraValueType.RICHTEXT_VALUE:
            if links := _process_richtext_value(val, resource.res_id):
                stand_off.append(links)
    return link_values, stand_off


def _process_link_value(value: ValueInformation, res_id: str) -> LinkValueLink:
    return LinkValueLink(
        source_id=res_id,
        target_id=value.user_facing_value,
        link_uuid=value.value_uuid,
    )


def _process_richtext_value(value: ValueInformation, res_id: str) -> StandOffLink | None:
    if not (links := _get_stand_off_links(value.user_facing_value)):
        return None
    return StandOffLink(
        source_id=res_id,
        target_ids=links,
        link_uuid=value.value_uuid,
    )


def _get_stand_off_links(text: str) -> set[str] | None:
    if not (links_in_text := set(regex.findall(pattern=r'href="(.*?)"', string=text))):
        return None
    links = set()
    for lnk in links_in_text:
        if internal_id := regex.search(r"IRI:(.*):IRI", lnk):
            links.add(internal_id.group(1))
        else:
            links.add(lnk)
    return links
