def get_default_json_ld_context() -> dict[str, str]:
    """
    Returns the JSON-LD context as a dictionary.

    Returns:
        JSON-LD context as a dictionary.
    """
    return {
        "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
        "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    }


def get_json_ld_context_for_project(ontos: dict[str, str]) -> dict[str, str]:
    """Provided a dictionary of ontology names and IRIs, returns a JSON-LD context for the project."""
    context = get_default_json_ld_context()
    project_context = {k: f"{v}#" for k, v in ontos.items()}
    context.update(project_context)
    return context
