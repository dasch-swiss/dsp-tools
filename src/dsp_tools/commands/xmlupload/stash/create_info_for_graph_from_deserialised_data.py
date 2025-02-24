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


def _process_richtext_value(value: ValueInformation, res_id: str) -> list[StandOffLink]:
    pass


def _process_link_value(value: ValueInformation, res_id: str) -> list[LinkValueLink]:
    pass
