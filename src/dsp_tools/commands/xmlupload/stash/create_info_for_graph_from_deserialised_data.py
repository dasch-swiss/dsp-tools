
from dsp_tools.commands.xmlupload.stash.graph_models import ResptrLink
from dsp_tools.commands.xmlupload.stash.graph_models import XMLLink, InfoForGraph
from dsp_tools.utils.iri_util import is_resource_iri
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadata
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TripleObjectType
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation


def create_info_for_graph_from_data(data: DataDeserialised) -> InfoForGraph:
    pass


def _process_one_resource(resource: ResourceDeserialised) -> list[XMLLink]:
    pass

