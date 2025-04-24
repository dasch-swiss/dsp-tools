from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedRichtext
from dsp_tools.commands.xmlupload.stash.graph_models import InfoForGraph
from dsp_tools.commands.xmlupload.stash.graph_models import LinkValueLink
from dsp_tools.commands.xmlupload.stash.graph_models import StandOffLink
from dsp_tools.utils.data_formats.iri_util import is_resource_iri


def create_info_for_graph_from_processed_resources(resources: list[ProcessedResource]) -> InfoForGraph:
    """Extracts information to create the graph to analyse the circular references."""
    all_links = []
    all_stand_off = []
    all_resource_ids = []
    for res in resources:
        links, stand_off = _process_one_resource(res)
        all_links.extend(links)
        all_stand_off.extend(stand_off)
        all_resource_ids.append(res.res_id)
    return InfoForGraph(
        all_resource_ids=all_resource_ids,
        link_values=all_links,
        standoff_links=all_stand_off,
    )


def _process_one_resource(resource: ProcessedResource) -> tuple[list[LinkValueLink], list[StandOffLink]]:
    link_values = []
    stand_off = []
    for val in resource.values:
        if isinstance(val, ProcessedLink):
            if is_resource_iri(val.value):
                continue
            link_values.append(
                LinkValueLink(
                    source_id=resource.res_id,
                    target_id=val.value,
                    link_uuid=val.value_uuid,
                )
            )
        elif isinstance(val, ProcessedRichtext):
            if val.resource_references:
                only_ids = {x for x in val.resource_references if not is_resource_iri(x)}
                if not only_ids:
                    continue
                stand_off.append(
                    StandOffLink(
                        source_id=resource.res_id,
                        target_ids=only_ids,
                        link_uuid=val.value_uuid,
                    )
                )
    return link_values, stand_off
