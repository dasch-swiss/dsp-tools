from copy import deepcopy
from pathlib import Path

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.richtext_id2iri import replace_ids_if_found
from dsp_tools.utils.json_parsing import parse_json_file
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue


def use_id2iri_mapping_to_replace_ids(resources: list[ParsedResource], id2iri_file: Path) -> list[ParsedResource]:
    lookup = parse_json_file(id2iri_file)
    iri_lookup = IriResolver(lookup)
    return _replace_all_ids_with_iris(resources, iri_lookup)


def _replace_all_ids_with_iris(resources: list[ParsedResource], iri_lookup: IriResolver) -> list[ParsedResource]:
    return [_process_one_resource(r, iri_lookup) for r in resources]


def _process_one_resource(res: ParsedResource, iri_lookup: IriResolver) -> ParsedResource:
    new_vals = []
    previous_vals = deepcopy(res.values)
    for v in previous_vals:
        if v.value_type == KnoraValueType.LINK_VALUE:
            new_vals.append(_process_link_value(v, iri_lookup))
        elif v.value_type == KnoraValueType.RICHTEXT_VALUE:
            new_vals.append(_process_richtext_value(v, iri_lookup))
        else:
            new_vals.append(v)
    res.values = new_vals
    return res


def _process_link_value(val: ParsedValue, iri_lookup: IriResolver) -> ParsedValue:
    if found := iri_lookup.get(val.value):
        val.value = found
    return val


def _process_richtext_value(val: ParsedValue, iri_lookup: IriResolver) -> ParsedValue:
    replaced, _ = replace_ids_if_found(val.value, iri_lookup)
    val.value = replaced
    return val
