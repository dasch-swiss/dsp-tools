from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue


def replace_ids_with_iris(resources: list[ParsedResource], iri_lookup: IriResolver) -> list[ParsedResource]:
    pass


def _process_one_resource(res: ParsedResource, iri_lookup: IriResolver) -> ParsedResource:
    pass


def _process_link_value(val: ParsedValue, iri_lookup: IriResolver) -> ParsedValue:
    pass


def _process_richtext_value(val: ParsedValue, iri_lookup: IriResolver) -> ParsedValue:
    pass
