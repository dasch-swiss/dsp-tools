from rdflib.term import Node


def reformat_onto_iri(iri: Node) -> str:
    """Takes a rdflib Node and returns a prefixed IRI in string form."""
    iri_str = str(iri)
    if "http://www.w3.org/2000/01/rdf-schema#" in iri_str:
        return f'rdfs:{iri_str.split("#")[-1]}'
    onto = iri_str.split("/")[-2]
    ending = iri_str.split("#")[-1]
    if onto == "knora-api":
        return ending
    return f"{onto}:{ending}"


def reformat_data_iri(iri: Node) -> str:
    """Takes a rdflib Node with in the data namespace and returns only the suffix."""
    return str(iri).replace("http://data/", "")
