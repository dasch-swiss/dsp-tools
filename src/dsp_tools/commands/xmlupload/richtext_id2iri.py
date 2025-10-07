import regex

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.error.exceptions import Id2IriReplacementError


def replace_internal_ids_with_iris_if_found(richtext_str: str, iri_resolver: IriResolver) -> str:
    ids_used = find_internal_ids(richtext_str)
    if ids_used:
        richtext_str, _ = _replace_ids_if_found(richtext_str, ids_used, iri_resolver)
    return richtext_str


def prepare_richtext_string_for_upload(richtext_str: str, iri_resolver: IriResolver) -> str:
    ids_used = find_internal_ids(richtext_str)
    if ids_used:
        richtext_str, ids_not_found = _replace_ids_if_found(richtext_str, ids_used, iri_resolver)
        if ids_not_found:
            raise Id2IriReplacementError(
                f"Internal ID(s) in richtext '{', '.join(ids_not_found)}' could not be resolved to an IRI"
            )
    return _richtext_as_xml(richtext_str)


def _replace_ids_if_found(txt: str, ids_used: set[str], iri_resolver: IriResolver) -> tuple[str, set[str]]:
    not_found = set()
    for id_ in ids_used:
        if iri_found := iri_resolver.get(id_):
            txt = _replace_one_id(txt, id_, iri_found)
        else:
            not_found.add(id_)
    return txt, not_found


def _replace_one_id(txt: str, id_: str, iri: str) -> str:
    return txt.replace(f'href="IRI:{id_}:IRI"', f'href="{iri}"')


def find_internal_ids(txt: str) -> set[str]:
    return set(regex.findall(pattern='href="IRI:(.*?):IRI"', string=txt))


def _richtext_as_xml(richtext_str: str) -> str:
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<text>{richtext_str}</text>'
