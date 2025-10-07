import regex

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.error.exceptions import Id2IriReplacementError


def replace_internal_ids_with_iris_in_richtext_raises(richtext_str: str, iri_resolver: IriResolver) -> str:
    ids_used = _find_internal_ids(richtext_str)
    if ids_used:
        return _replace_ids_raises(richtext_str, ids_used, iri_resolver)
    return richtext_str


def _replace_ids_raises(txt: str, ids_used: set[str], iri_resolver: IriResolver) -> str:
    for id_ in ids_used:
        txt = _replace_one_id(txt, id_, iri_resolver)
    return txt


def replace_internal_ids_with_iris_if_found(richtext_str: str, iri_resolver: IriResolver) -> str:
    ids_used = _find_internal_ids(richtext_str)
    if ids_used:
        return _replace_ids_if_found(richtext_str, ids_used, iri_resolver)
    return richtext_str


def _replace_ids_if_found(txt: str, ids_used: set[str], iri_resolver: IriResolver) -> str:
    for id_ in ids_used:
        try:
            txt = _replace_one_id(txt, id_, iri_resolver)
        except Id2IriReplacementError:
            continue
    return txt


def _replace_one_id(txt: str, id_: str, iri_resolver: IriResolver) -> str:
    if iri := iri_resolver.get(id_):
        return txt.replace(f'href="IRI:{id_}:IRI"', f'href="{iri}"')
    else:
        raise Id2IriReplacementError(f"Internal ID '{id_}' could not be resolved to an IRI")


def _find_internal_ids(txt: str) -> set[str]:
    return set(regex.findall(pattern='href="IRI:(.*?):IRI"', string=txt))
