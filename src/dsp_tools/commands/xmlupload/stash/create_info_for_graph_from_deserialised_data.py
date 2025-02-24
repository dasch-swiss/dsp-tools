import regex

from dsp_tools.commands.xmlupload.stash.graph_models import InfoForGraph
from dsp_tools.commands.xmlupload.stash.graph_models import LinkValueLink
from dsp_tools.commands.xmlupload.stash.graph_models import StandOffLink
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation


def create_info_for_graph_from_data(data: DataDeserialised) -> InfoForGraph:
    """Extracts information to create the graph to analyse the circular references."""


def _process_one_resource(resource: ResourceDeserialised) -> tuple[list[LinkValueLink], list[StandOffLink]]:
    pass


def _process_richtext_value(value: ValueInformation, res_id: str) -> StandOffLink | None:
    if not (links_in_text := set(regex.findall(pattern=r'href="(.*?)"', string=value.user_facing_value))):
        return None
    links = set()
    for lnk in links_in_text:
        if internal_id := regex.search(r"IRI:(.*):IRI", lnk):
            links.add(internal_id.group(1))
        else:
            links.add(lnk)
    return StandOffLink(
        source_id=res_id,
        target_ids=links,
        link_uuid=value.value_uuid,
    )


def _process_link_value(value: ValueInformation, res_id: str) -> LinkValueLink:
    return LinkValueLink(
        source_id=res_id,
        target_id=value.user_facing_value,
        link_uuid=value.value_uuid,
    )
