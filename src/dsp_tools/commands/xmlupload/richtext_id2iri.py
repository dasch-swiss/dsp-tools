import regex

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.error.exceptions import BaseError


def replace_internal_ids_with_iris_in_richtext(richtext_str: str, iri_resolver: IriResolver) -> str:
    ids_used = _find_internal_ids(richtext_str)
    return _replace_ids(richtext_str, ids_used, iri_resolver)


def _replace_ids(txt: str, ids_used: set[str], iri_resolver: IriResolver) -> str:
    for id_ in ids_used:
        if iri := iri_resolver.get(id_):
            txt = txt.replace(f'href="IRI:{id_}:IRI"', f'href="{iri}"')
        else:
            raise BaseError(f"Internal ID '{id_}' could not be resolved to an IRI")
    return txt


def _find_internal_ids(txt: str) -> set[str]:
    return set(regex.findall(pattern='href="IRI:(.*?):IRI"', string=txt))
