# pylint: disable=missing-class-docstring,missing-function-docstring

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from typing import Any, Optional, Pattern, Union

import regex

from dsp_tools.models.exceptions import BaseError

#
# here we do some data typing that should help
#


@dataclass(frozen=True)
class OntoIri:
    """
    Holds an ontology IRI

    Attributes:
        iri: the ontology IRI
        hashtag: True if "#" is used to separate elements, False if element name is appended after "/"
    """

    iri: str
    hashtag: bool


ContextType = dict[str, OntoIri]


class IriTest:  # pylint: disable=too-few-public-methods
    __iri_regexp = regex.compile("^(http)s?://([\\w\\.\\-~]+)?(:\\d{,6})?(/[\\w\\-~]+)*(#[\\w\\-~]*)?")

    @classmethod
    def test(cls, val: str) -> bool:
        m = cls.__iri_regexp.match(val)
        return m.span()[1] == len(val) if m else False


@unique
class Actions(Enum):
    Create = 1
    Read = 2
    Update = 3
    Delete = 4


@unique
class Cardinality(Enum):
    C_1 = "1"
    C_0_1 = "0-1"
    C_1_n = "1-n"
    C_0_n = "0-n"


class ContextIterator:  # pylint: disable=too-few-public-methods
    _context: "Context"
    _prefixes: list[str]
    _index: int

    def __init__(self, context: "Context"):
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
    _exp: Pattern[str]

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
        # regexp to test for a complete IRI (including fragment identifier)
        self._exp = regex.compile("^(http)s?://([\\w\\.\\-~]+)?(:\\d{,6})?(/[\\w\\-~]+)*(#[\\w\\-~]*)?")
        self._context = ContextType({})

        # add ontologies from context, if any
        if context:
            for prefix, onto in context.items():
                self._context[prefix] = OntoIri(onto.removesuffix("#"), onto.endswith("#") or onto.endswith("/v2"))

        # add standard ontologies (rdf, rdfs, owl, xsl)
        for k, v in self.base_ontologies.items():
            if not self._context.get(k):
                self._context[k] = v

        # add DSP-API internal ontologies (knora-api, salsah-gui)
        for k, v in self.knora_ontologies.items():
            if not self._context.get(k):
                self._context[k] = v

        self._rcontext = {v.iri: k for k, v in self._context.items()}

    def __len__(self) -> int:
        return len(self._context)

    def __getitem__(self, key: str) -> OntoIri:
        return self._context[key]

    def __setitem__(self, key: str, value: OntoIri) -> None:
        self._context[key] = value
        self._rcontext[value.iri] = key

    def __delitem__(self, key: str) -> None:
        iri = self._context[key].iri
        del self._context[key].iri
        del self._rcontext[iri]

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
        if iri is None:
            if prefix in self.knora_ontologies:
                return
            if prefix in self.base_ontologies:
                return
            if prefix in self.common_ontologies:
                self._context[prefix] = self.common_ontologies[prefix]
        else:
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
        if IriTest.test(prefix):
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
        if not IriTest.test(iri):
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
        if IriTest.test(val):
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

        if not IriTest.test(iri):
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

        if IriTest.test(iri_str):
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


class DateTimeStamp:
    """
    Class to hold and process an xsd:dateTimeStamp
    """

    _dateTimeStamp: str
    _validation_regex = (
        r"^-?([1-9][0-9]{3,}|0[0-9]{3})"
        r"-(0[1-9]|1[0-2])"
        r"-(0[1-9]|[12][0-9]|3[01])"
        r"T(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?|(24:00:00(\.0+)?))"
        r"(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))$"
    )

    def __init__(self, val: Any):
        """
        The constructor works for different inputs:
        - a string
        - an instance of "DateTimeStamp"
        - json-ld construct of the form { "@type": "xsd:dateTimeStamp", "@value": "date-str" }
        :param val: xsd:dateTimeStamp as string, instance of "DateTimeStamp" or json-ld construct
        """
        if isinstance(val, str):
            if not regex.search(self._validation_regex, val):
                raise BaseError(f"Invalid xsd:dateTimeStamp: '{val}'")
            self._dateTimeStamp = val
        elif isinstance(val, DateTimeStamp):
            self._dateTimeStamp = str(val)
        else:
            if val.get("@type") == "xsd:dateTimeStamp" and regex.search(self._validation_regex, str(val.get("@value"))):
                self._dateTimeStamp = val["@value"]
            else:
                raise BaseError(f"Invalid xsd:dateTimeStamp: '{val}'")

    def __eq__(self, other: Union[str, "DateTimeStamp"]) -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp == other._dateTimeStamp

    def __lt__(self, other: "DateTimeStamp") -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp < other._dateTimeStamp

    def __le__(self, other: "DateTimeStamp") -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp <= other._dateTimeStamp

    def __gt__(self, other: "DateTimeStamp") -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp > other._dateTimeStamp

    def __ge__(self, other: "DateTimeStamp") -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp >= other._dateTimeStamp

    def __ne__(self, other: DateTimeStamp) -> bool:
        if isinstance(other, str):
            other = DateTimeStamp(other)
        return self._dateTimeStamp != other._dateTimeStamp

    def __str__(self: "DateTimeStamp") -> str:
        return self._dateTimeStamp

    def toJsonObj(self) -> dict[str, str]:
        return {"@type": "xsd:dateTimeStamp", "@value": self._dateTimeStamp}


class WithId:  # pylint: disable=too-few-public-methods
    """
    Class helper to get json-ld "@id" thingies
    """

    _tmp: str = None

    def __init__(self, obj: Optional[dict[str, str]]):
        if obj is None:
            return
        self._tmp = obj.get("@id")

    def str(self) -> Optional[str]:
        return self._tmp
