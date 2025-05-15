from __future__ import annotations

from typing import Optional

import regex

from dsp_tools.commands.project.legacy_models.helpers import ContextType
from dsp_tools.commands.project.legacy_models.helpers import OntoIri
from dsp_tools.error.exceptions import BaseError
from dsp_tools.utils.data_formats.iri_util import is_iri


class ContextIterator:
    _context: Context
    _prefixes: list[str]
    _index: int

    def __init__(self, context: Context):
        self._context = context
        self._prefixes = list(self._context.context)
        self._index = 0

    def __next__(self) -> tuple[Optional[str], Optional[OntoIri]]:
        if len(self._context.context) == 0 and self._index == 0:
            return None, None
        elif self._index < len(self._context.context):
            tmp = self._prefixes[self._index]
            self._index += 1
            return tmp, self._context.context[tmp]
        else:
            raise StopIteration


class Context:
    """
    This class holds a JSON-LD context with the ontology IRI's and the associated prefixes
    """

    _context: ContextType
    _rcontext: dict[str, str]

    common_ontologies = ContextType(
        {
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
    )

    knora_ontologies = ContextType(
        {
            "knora-api": OntoIri("http://api.knora.org/ontology/knora-api/v2", True),
            "salsah-gui": OntoIri("http://api.knora.org/ontology/salsah-gui/v2", True),
        }
    )

    base_ontologies = ContextType(
        {
            "rdf": OntoIri("http://www.w3.org/1999/02/22-rdf-syntax-ns", True),
            "rdfs": OntoIri("http://www.w3.org/2000/01/rdf-schema", True),
            "owl": OntoIri("http://www.w3.org/2002/07/owl", True),
            "xsd": OntoIri("http://www.w3.org/2001/XMLSchema", True),
        }
    )

    def __init__(self, context: Optional[dict[str, str]] = None):
        """
        THe Constructor of the Context. It takes one optional parameter which as a dict of
        prefix - ontology-iri pairs. If the hashtag "#" is used to append element name, the
        ontology-iri *must* end with "#"!
        :param context: A dict of prefix - ontology-iri pairs
        """
        self._context = ContextType({})

        # add ontologies from context, if any
        if context:
            for prefix, onto in context.items():
                self._context[prefix] = OntoIri(onto.removesuffix("#"), onto.endswith(("#", "/v2")))

        # add standard ontologies (rdf, rdfs, owl, xsl)
        for k, v in self.base_ontologies.items():
            if not self._context.get(k):
                self._context[k] = v

        # add DSP-API internal ontologies (knora-api, salsah-gui)
        for k, v in self.knora_ontologies.items():
            if not self._context.get(k):
                self._context[k] = v

        self._rcontext = {v.iri: k for k, v in self._context.items()}

    def __getitem__(self, key: str) -> OntoIri:
        return self._context[key]

    def __contains__(self, key: str) -> bool:
        return key in self._context

    def __iter__(self) -> ContextIterator:
        return ContextIterator(self)

    def __str__(self) -> str:
        output = "Context:\n"
        for prefix, val in self._context.items():
            output += "  " + prefix + ": " + val.iri + "\n"
        return output

    #
    # now we have a lot of getters/setters
    #
    @property
    def context(self) -> ContextType:
        return self._context

    @context.setter
    def context(self, value: ContextType) -> None:
        """
        Setter function for the context out of a dict in the form { prefix1 : iri1, prefix2, iri2, …}

        :param value: Dictionary of context
        :return: None
        """
        if value is not None and isinstance(value, ContextType):
            self._context = value
        else:
            raise BaseError("Error in parameter to context setter")

    def add_context(self, prefix: str, iri: Optional[str] = None) -> None:
        """
        Add a new context to a context instance

        :param prefix: The prefix that should be used
        :param iri: The IRI that belongs to this context prefix
        :return: None
        """
        match iri:
            case None:
                if prefix in self.knora_ontologies:
                    return
                elif prefix in self.base_ontologies:
                    return
                elif prefix in self.common_ontologies:
                    self._context[prefix] = self.common_ontologies[prefix]
            case str():
                if iri.endswith("#"):
                    iri = iri[:-1]
                    self._context[prefix] = OntoIri(iri, True)
                else:
                    self._context[prefix] = OntoIri(iri, False)
        self._rcontext[iri] = prefix

    def iri_from_prefix(self, prefix: str) -> Optional[str]:
        """
        Returns the full IRI belonging to this prefix, without trailing "#"!

        :param prefix: Prefix of the context entry
        :return: The full IRI without trailing "#"
        """
        # if self.__is_iri(prefix):
        if is_iri(prefix):
            return prefix
        if self._context.get(prefix) is not None:
            return self._context.get(prefix).iri
        else:
            return None

    def prefix_from_iri(self, iri: str) -> Optional[str]:
        """
        Get the IRI from a full context that has or has not a trailing "#". It first searches in the normal list
        of contexted. If the iri is not found there, it looks in the list common (external) ontologies. If the
        ontology is found there, this ontology is added to the list of known ontology and it's prefix is returned.
        If nothing is found, None is returns

        :param iri: The full IRI with or without trailing "#", or
        :return: the prefix of this context element, or None, if not found
        """
        # if not self.__is_iri(iri):
        if not is_iri(iri):
            raise BaseError("String does not conform to IRI patter: " + iri)
        if iri.endswith("#"):
            iri = iri[:-1]
        result = self._rcontext.get(iri)
        if result is None:
            entrylist = list(filter(lambda x: x[1].iri == iri, self.common_ontologies.items()))
            if len(entrylist) == 1:
                entry = entrylist[0]
                self._context[entry[0]] = entry[1]  # add to list of prefixes used
                self._rcontext[entry[1].iri] = entry[0]
                result = entry[0]
            else:
                tmp = iri.split("/")
                if tmp[-1] == "v2":
                    #
                    # we have a knora ontology name "http://server/ontology/shortcode/shortname/v2"
                    self._context[tmp[-2]] = OntoIri(iri, True)  # add to list of prefixes used
                    self._rcontext[iri] = tmp[-2]
                else:
                    raise BaseError("Iri cannot be resolved to a well-known prefix!")
        return result

    def get_qualified_iri(self, val: Optional[str]) -> Optional[str]:
        """
        Given an IRI, its fully qualified name is returned.

        Args:
            val: The input IRI

        Returns:
            the fully qualified IRI
        """
        if not val:
            return None
        if is_iri(val):
            return val
        tmp = val.split(":")
        if len(tmp) < 2:
            raise BaseError("There is no separator to identify the prefix: " + val)
        iri_info = self._context.get(tmp[0])
        if iri_info is None:
            entrylist = list(filter(lambda x: x[1].iri == tmp[0], self.common_ontologies.items()))
            if len(entrylist) == 1:
                entry = entrylist[0]
                self._context[entry[0]] = entry[1]  # add to list of prefixes used
                self._rcontext[entry[1].iri] = entry[0]
                iri_info = entry[1]
            else:
                raise BaseError("Ontology not known! Cannot generate fully qualified IRI")
        if iri_info.hashtag:
            return iri_info.iri + "#" + tmp[1]
        else:
            return iri_info.iri + tmp[1]

    def get_prefixed_iri(self, iri: Optional[str]) -> Optional[str]:
        """
        We reduce a fully qualified IRI to a short one in the form "prefix:name"

        :param iri: Fully qualified IRI
        :return: Return short from of IRI ("prefix:name")
        """
        if iri is None:
            return None

        # check if the iri already has the form "prefix:name"
        m = regex.match("([\\w-]+):([\\w-]+)", iri)
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

        prefix = self._rcontext.get(onto_part)
        if prefix is None:
            entry_list = list(filter(lambda x: x[1].iri == onto_part, self.common_ontologies.items()))
            if len(entry_list) == 1:
                entry = entry_list[0]
                self._context[entry[0]] = entry[1]  # add to list of prefixes used
                self._rcontext[entry[1].iri] = entry[0]
                prefix = entry[0]
            else:
                return None
        return prefix + ":" + element

    def reduce_iri(self, iri_str: str, onto_name: Optional[str] = None) -> str:
        """
        Reduces an IRI to the form that is used within the definition JSON file. It expects the context object to have
        entries (prefixes) for all IRIs:
        - if it's an external IRI and the ontology can be extracted as prefix it returns: "prefix:name"
        - if it's in the same ontology, it returns: ":name"
        - if it's a system ontology ("knora-api" or "salsah-gui") it returns: "name"
        - if the IRI can't be reduced, it's returned as is

        Args:
            iri_str: the IRI that should be reduced
            onto_name: the name of the ontology

        Returns:
            The reduced IRI if possible otherwise the fully qualified IRI
        """
        knora_api = self.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = self.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")

        if is_iri(iri_str):
            if self.get_prefixed_iri(iri_str):
                iri_str = self.get_prefixed_iri(iri_str)
        tmp = iri_str.split(":")
        if tmp[0] == knora_api or tmp[0] == salsah_gui:
            return tmp[1]
        elif tmp[0] == onto_name:
            return ":" + tmp[1]
        else:
            return iri_str

    def toJsonObj(self) -> dict[str, str]:
        """
        Return a python object that can be jsonfied...
        :return: Object to be jsonfied
        """
        return {prefix: oinfo.iri + "#" if oinfo.hashtag else oinfo.iri for prefix, oinfo in self._context.items()}

    def get_externals_used(self) -> dict[str, str]:
        exclude = ["rdf", "rdfs", "owl", "xsd", "knora-api", "salsah-gui"]
        return {prefix: onto.iri for prefix, onto in self._context.items() if prefix not in exclude}
