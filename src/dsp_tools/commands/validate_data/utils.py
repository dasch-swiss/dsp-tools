from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias


def reformat_any_iri(iri: SubjectObjectTypeAlias | str) -> str:
    """
    Reformats any kind of IRI, if it starts with data then it treats is like a data IRI.
    Otherwise, like an ontology IRI.

    Args:
        iri: Input IRI

    Returns:
        reformatted string
    """
    iri_str = str(iri)
    if iri_str.startswith("http://data/"):
        return reformat_data_iri(iri_str)
    if iri_str.startswith("http://rdfh.ch/"):
        return iri_str
    return reformat_onto_iri(iri_str)


def reformat_onto_iri(iri: SubjectObjectTypeAlias | str) -> str:
    """Takes a rdflib Node and returns a prefixed IRI in string form."""
    iri_str = str(iri)
    if "http://www.w3.org/2000/01/rdf-schema#" in iri_str:
        return f"rdfs:{iri_str.split('#')[-1]}"
    onto = iri_str.split("/")[-2]
    ending = iri_str.split("#")[-1]
    if onto == "knora-api":
        return ending
    return f"{onto}:{ending}"


def reformat_data_iri(iri: SubjectObjectTypeAlias | str) -> str:
    """Takes a rdflib Node with in the data namespace and returns only the suffix."""
    return str(iri).replace("http://data/", "", 1)
