from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

import regex

from dsp_tools.commands.get.legacy_models.helpers import OntoIri
from dsp_tools.error.exceptions import BaseError
from dsp_tools.utils.data_formats.iri_util import is_iri

# Module-level constants (previously class variables)
COMMON_ONTOLOGIES: dict[str, OntoIri] = {
    "foaf": OntoIri("http://xmlns.com/foaf/0.1/", False),
    "dc": OntoIri("http://purl.org/dc/elements/1.1/", False),
    "dcterms": OntoIri("http://purl.org/dc/terms/", False),
    "dcmi": OntoIri("http://purl.org/dc/dcmitype/", False),
    "skos": OntoIri("http://www.w3.org/2004/02/skos/core", True),
    "bibtex": OntoIri("http://purl.org/net/nknouf/ns/bibtex", True),
    "bibo": OntoIri("http://purl.org/ontology/bibo/", False),
    "cidoc": OntoIri("http://purl.org/NET/cidoc-crm/core", True),
    "schema": OntoIri("https://schema.org/", False),
    "edm": OntoIri("http://www.europeana.eu/schemas/edm/", False),
    "ebucore": OntoIri("http://www.ebu.ch/metadata/ontologies/ebucore/ebucore", True),
}

KNORA_ONTOLOGIES: dict[str, OntoIri] = {
    "knora-api": OntoIri("http://api.knora.org/ontology/knora-api/v2", True),
    "salsah-gui": OntoIri("http://api.knora.org/ontology/salsah-gui/v2", True),
}

BASE_ONTOLOGIES: dict[str, OntoIri] = {
    "rdf": OntoIri("http://www.w3.org/1999/02/22-rdf-syntax-ns", True),
    "rdfs": OntoIri("http://www.w3.org/2000/01/rdf-schema", True),
    "owl": OntoIri("http://www.w3.org/2002/07/owl", True),
    "xsd": OntoIri("http://www.w3.org/2001/XMLSchema", True),
}


@dataclass
class Context:
    """Holds a JSON-LD context with ontology IRIs and their associated prefixes."""

    context: dict[str, OntoIri] = field(default_factory=dict)
    rcontext: dict[str, str] = field(default_factory=dict)

    def add_context(self, prefix: str, iri: str | None = None) -> None:
        """
        Add a new context to a context instance.

        Args:
            prefix: The prefix that should be used
            iri: The IRI that belongs to this context prefix
        """
        match iri:
            case None:
                if prefix in KNORA_ONTOLOGIES:
                    return
                elif prefix in BASE_ONTOLOGIES:
                    return
                elif prefix in COMMON_ONTOLOGIES:
                    self.context[prefix] = COMMON_ONTOLOGIES[prefix]
            case str():
                if iri.endswith("#"):
                    iri = iri[:-1]
                    self.context[prefix] = OntoIri(iri, True)
                else:
                    self.context[prefix] = OntoIri(iri, False)
                self.rcontext[iri] = prefix

    def prefix_from_iri(self, iri: str) -> str | None:
        """
        Get the prefix from a full IRI.

        First searches in the known contexts. If not found, looks in common ontologies.
        If the ontology is found there, it's added to the context.

        Args:
            iri: The full IRI with or without trailing "#"

        Returns:
            The prefix of this context element, or None if not found

        Raises:
            BaseError: If the string does not conform to IRI pattern or cannot be resolved
        """
        if not is_iri(iri):
            raise BaseError("String does not conform to IRI patter: " + iri)
        if iri.endswith("#"):
            iri = iri[:-1]
        result = self.rcontext.get(iri)
        if result is None:
            entrylist = list(filter(lambda x: x[1].iri == iri, COMMON_ONTOLOGIES.items()))
            if len(entrylist) == 1:
                entry = entrylist[0]
                self.context[entry[0]] = entry[1]
                self.rcontext[entry[1].iri] = entry[0]
                result = entry[0]
            else:
                tmp = iri.split("/")
                if tmp[-1] == "v2":
                    # we have a knora ontology name "http://server/ontology/shortcode/shortname/v2"
                    self.context[tmp[-2]] = OntoIri(iri, True)
                    self.rcontext[iri] = tmp[-2]
                else:
                    raise BaseError("Iri cannot be resolved to a well-known prefix!")
        return result

    def get_prefixed_iri(self, iri: str | None) -> str | None:
        """
        Reduce a fully qualified IRI to a short one in the form "prefix:name".

        Args:
            iri: Fully qualified IRI

        Returns:
            Short form of IRI ("prefix:name") or None if not found
        """
        if iri is None:
            return None

        # check if the iri already has the form "prefix:name"
        m = regex.match(r"([\w-]+):([\w-]+)", iri)
        if m and m.span()[1] == len(iri):
            return iri

        if not is_iri(iri):
            raise BaseError(f"The IRI '{iri}' does not conform to the IRI pattern.")

        split_point = iri.find("#")
        if split_point == -1:
            split_point = iri.rfind("/")
            onto_part = iri[: split_point + 1]
            element = iri[split_point + 1 :]
        else:
            onto_part = iri[:split_point]
            element = iri[split_point + 1 :]

        prefix = self.rcontext.get(onto_part)
        if prefix is None:
            entry_list = list(filter(lambda x: x[1].iri == onto_part, COMMON_ONTOLOGIES.items()))
            if len(entry_list) == 1:
                entry = entry_list[0]
                self.context[entry[0]] = entry[1]
                self.rcontext[entry[1].iri] = entry[0]
                prefix = entry[0]
            else:
                return None
        return prefix + ":" + element

    def reduce_iri(self, iri_str: str, onto_name: str | None = None) -> str:
        """
        Reduce an IRI to the form used in definition JSON files.

        - External IRI with known prefix: "prefix:name"
        - Same ontology: ":name"
        - System ontology ("knora-api" or "salsah-gui"): "name"
        - Otherwise: returns as-is

        Args:
            iri_str: The IRI that should be reduced
            onto_name: The name of the ontology

        Returns:
            The reduced IRI if possible, otherwise the fully qualified IRI
        """
        knora_api = self.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = self.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")

        if is_iri(iri_str):
            if prefixed := self.get_prefixed_iri(iri_str):
                iri_str = prefixed
        tmp = iri_str.split(":")
        if tmp[0] == knora_api or tmp[0] == salsah_gui:
            return tmp[1]
        elif tmp[0] == onto_name:
            return ":" + tmp[1]
        else:
            return iri_str

    def to_json_obj(self) -> dict[str, str]:
        """Return a dictionary that can be serialized to JSON."""
        return {prefix: oinfo.iri + "#" if oinfo.hashtag else oinfo.iri for prefix, oinfo in self.context.items()}

    def get_externals_used(self) -> dict[str, str]:
        """Return externally used ontologies excluding standard ones."""
        exclude = ["rdf", "rdfs", "owl", "xsd", "knora-api", "salsah-gui"]
        return {prefix: onto.iri for prefix, onto in self.context.items() if prefix not in exclude}


def create_context(input_context: dict[str, str] | None = None) -> Context:
    """
    Create a Context from an optional dictionary of prefix-IRI pairs.

    If the hashtag "#" is used to append element names, the IRI must end with "#".

    Args:
        input_context: A dict of prefix-IRI pairs

    Returns:
        A Context instance with the provided prefixes plus standard ontologies
    """
    context: dict[str, OntoIri] = {}

    # Add ontologies from input context, if any
    if input_context:
        for prefix, onto in input_context.items():
            context[prefix] = OntoIri(onto.removesuffix("#"), onto.endswith(("#", "/v2")))

    # Add standard ontologies (rdf, rdfs, owl, xsd)
    for k, v in BASE_ONTOLOGIES.items():
        if k not in context:
            context[k] = v

    # Add DSP-API internal ontologies (knora-api, salsah-gui)
    for k, v in KNORA_ONTOLOGIES.items():
        if k not in context:
            context[k] = v

    rcontext = {v.iri: k for k, v in context.items()}

    return Context(context=context, rcontext=rcontext)
