import re
import sys
from dataclasses import dataclass
from enum import Enum, unique
from traceback import format_exc
from typing import NewType, List, Dict, Optional, Any, Tuple, Union, Pattern

from pystrict import strict


#
# here we do some data typing that should help
#


@dataclass
class OntoInfo:
    """
    A small class thats holds an ontology IRI. The variable "hashtag" is True, if "#" is used s separate elements,
    False if the element name is just appended
    """
    iri: str
    hashtag: bool


ContextType = NewType("ContextType", Dict[str, OntoInfo])


def LINE() -> int:
    return sys._getframe(1).f_lineno


@strict
class IriTest:
    __iri_regexp = re.compile("^(http)s?://([\\w\\.\\-~]+)?(:\\d{,6})?(/[\\w\\-~]+)*(#[\\w\\-~]*)?")

    @classmethod
    def test(cls, val: str) -> bool:
        m = cls.__iri_regexp.match(val)
        return m.span()[1] == len(val) if m else False


@strict
class BaseError(Exception):
    """
    A basic error class
    """
    _message: str

    def __init__(self, message: str) -> None:
        """
        Constructor for error message
        :param message: error message string
        """
        super().__init__()
        self._message = message

    def __str__(self) -> str:
        """
        Convert to string
        :return: stringyfied error message
        """
        return "ERROR: " + self._message + "!\n\n" + format_exc()

    @property
    def message(self) -> str:
        return self._message


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


@strict
class ContextIterator:
    _context: 'Context'
    _prefixes: List[str]
    _index: int

    def __init__(self, context: 'Context'):
        self._context = context
        self._prefixes = [x for x in self._context.context]
        self._index = 0

    def __next__(self) -> Tuple[Optional[str], Optional[OntoInfo]]:
        if len(self._context.context) == 0 and self._index == 0:
            return None, None
        elif self._index < len(self._context.context):
            tmp = self._prefixes[self._index]
            self._index += 1
            return tmp, self._context.context[tmp]
        else:
            raise StopIteration


@strict
class Context:
    """
    This class holds a JSON-LD context with the ontology IRI's and the associated prefixes
    """
    _context: ContextType
    _rcontext: Dict[str, str]
    _exp: Pattern[str]

    common_ontologies  = ContextType({
        "foaf": OntoInfo("http://xmlns.com/foaf/0.1/", False),
        "dc": OntoInfo("http://purl.org/dc/elements/1.1/", False),
        "dcterms": OntoInfo("http://purl.org/dc/terms/", False),
        "dcmi": OntoInfo("http://purl.org/dc/dcmitype/", False),
        "skos": OntoInfo("http://www.w3.org/2004/02/skos/core", True),
        "bibtex": OntoInfo("http://purl.org/net/nknouf/ns/bibtex", True),
        "bibo": OntoInfo("http://purl.org/ontology/bibo/", False),
        "cidoc": OntoInfo("http://purl.org/NET/cidoc-crm/core", True)
    })

    knora_ontologies = ContextType({
        "knora-api": OntoInfo("http://api.knora.org/ontology/knora-api/v2", True),
        "salsah-gui": OntoInfo("http://api.knora.org/ontology/salsah-gui/v2", True)
    })

    base_ontologies = ContextType({
        "rdf": OntoInfo("http://www.w3.org/1999/02/22-rdf-syntax-ns", True),
        "rdfs": OntoInfo("http://www.w3.org/2000/01/rdf-schema", True),
        "owl": OntoInfo("http://www.w3.org/2002/07/owl", True),
        "xsd": OntoInfo("http://www.w3.org/2001/XMLSchema", True)
    })

    def __is_iri(self, val: str) -> bool:
        """
        Test if string has a valid IRI pattern

        :param val: Input string
        :return: True, if val corresponds to IRI pattern
        """

        m = self._exp.match(val)
        return m.span()[1] == len(val) if m else False

    def __init__(self, context: Optional[Dict[str, str]] = None):
        """
        THe Constructor of the Context. It takes one optional parameter which as a dict of
        prefix - ontology-iri pairs. If the hashtag "#" is used to append element name, the
        ontology-iri *must* end with "#"!
        :param context: A dict of prefix - ontology-iri pairs
        """
        # regexp to test for a complete IRI (including fragment identifier)
        self._exp = re.compile("^(http)s?://([\\w\\.\\-~]+)?(:\\d{,6})?(/[\\w\\-~]+)*(#[\\w\\-~]*)?")
        self._context = ContextType({})
        
        # add ontologies from context, if any
        if context:
            for prefix, onto in context.items():
                self._context[prefix] = OntoInfo(onto.removesuffix('#'), onto.endswith('#'))
        
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

    def __getitem__(self, key: str) -> OntoInfo:
        return self._context[key]

    def __setitem__(self, key: str, value: OntoInfo) -> None:
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

    @property
    def rcontext(self) -> Dict[str, str]:
        return self._rcontext

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
                raise BaseError("The prefix '{}' is not known!".format(prefix))
        else:
            if iri.endswith("#"):
                iri = iri[:-1]
                self._context[prefix] = OntoInfo(iri, True)
            else:
                self._context[prefix] = OntoInfo(iri, False)
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
                tmp = iri.split('/')
                if tmp[-1] == "v2":
                    #
                    # we have a knora ontology name "http://server/ontology/shortcode/shortname/v2"
                    self._context[tmp[-2]] = OntoInfo(iri, True)  # add to list of prefixes used
                    self._rcontext[iri] = tmp[-2]
                else:
                    raise BaseError("Iri cannot be resolved to a well-known prefix!")
        return result

    def get_qualified_iri(self, val: Optional[str]) -> Optional[str]:
        """
        We will return the full qualified IRI, if it is not yet a full qualified IRI. If
        the IRI is already fully qualified, the we just return it.

        :param val: The input short form
        :return: the fully qualified IRI
        """
        if val is None:
            return None
        # if self.__is_iri(val):
        if IriTest.test(val):
            return val
        tmp = val.split(':')
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
                raise BaseError("Ontology not known! Cannot generate full qualified IRI")
        if iri_info.hashtag:
            return iri_info.iri + '#' + tmp[1]
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
        #
        # check if the iri already has the form "prefix:name"
        #
        m = re.match("([\\w-]+):([\\w-]+)", iri)
        if m and m.span()[1] == len(iri):
            return iri
        # if not self.__is_iri(iri):
        if not IriTest.test(iri):
            raise BaseError("String does not conform to IRI patter: " + iri)

        splitpoint = iri.find('#')
        if splitpoint == -1:
            splitpoint = iri.rfind('/')
            ontopart = iri[:splitpoint + 1]
            element = iri[splitpoint + 1:]
        else:
            ontopart = iri[:splitpoint]
            element = iri[splitpoint + 1:]
        prefix = self._rcontext.get(ontopart)
        if prefix is None:
            entrylist = list(filter(lambda x: x[1].iri == ontopart, self.common_ontologies.items()))
            if len(entrylist) == 1:
                entry = entrylist[0]
                self._context[entry[0]] = entry[1]  # add to list of prefixes used
                self._rcontext[entry[1].iri] = entry[0]
                prefix = entry[0]
            else:
                raise BaseError(
                    "Ontology {} not known! Cannot generate full qualified IRI: prefix={}".format(iri, prefix))
        return prefix + ':' + element

    def reduce_iri(self, iristr: str, ontoname: Optional[str] = None) -> str:
        """
        Reduce an IRI to the form that is used within the definition json file. It expects
        the context object to have entries (prefixes)  for all IRI's
        - if it's an external IRI, it returns: "prefix:name"
        - if it's in the same ontology, it returns ":name"
        - if it's a system ontoloy ("knora-api" or "salsah-gui") it returns "name"
        :param iristr:
        :return:
        """
        rdf = self.prefix_from_iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = self.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = self.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        xsd = self.prefix_from_iri("http://www.w3.org/2001/XMLSchema#")
        knora_api = self.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = self.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")

        if IriTest.test(iristr):
            iristr = self.get_prefixed_iri(iristr)
        tmp = iristr.split(':')
        if tmp[0] == knora_api or tmp[0] == salsah_gui:
            return tmp[1]
        elif ontoname is not None and tmp[0] == ontoname:
            return ':' + tmp[1]
        else:
            return iristr

    def toJsonObj(self) -> Dict[str, str]:
        """
        Return a python object that can be jsonfied...
        :return: Object to be jsonfied
        """
        return {prefix: oinfo.iri + '#' if oinfo.hashtag else oinfo.iri
                for prefix, oinfo in self._context.items()}

    def get_externals_used(self) -> Dict[str, str]:
        exclude = ["rdf", "rdfs", "owl", "xsd", "knora-api", "salsah-gui"]
        return {prefix: onto.iri for prefix, onto in self._context.items() if prefix not in exclude}

    def print(self) -> None:
        for a in self._context.items():
            print(a[0] + ': "' + a[1].iri + '"')


class LastModificationDate:
    """
    Class to hold and process the last modification date of a ontology
    """
    _last_modification_date: str

    def __init__(self, val: Any):
        """
        The constructor works for different inputs:
        - a string holding the modification date
        - an instance of "LastModificationDate"
        - json-ld construct of the form { "@type": "xsd:dateTimeStamp", "@value": "date-str" }
        :param val: datetimestamp as string, instance of "LastModificationDate" or json-ld construct
        """
        if isinstance(val, str):
            self._last_modification_date = val
        elif isinstance(val, LastModificationDate):
            self._last_modification_date = str(val)
        else:
            if val.get("@type") is not None and val.get("@type") == "xsd:dateTimeStamp":
                self._last_modification_date = val["@value"]
            else:
                raise BaseError("Invalid LastModificationDate")

    def __eq__(self, other: Union[str, 'LastModificationDate']) -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date == other._last_modification_date

    def __lt__(self, other: 'LastModificationDate') -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date < other._last_modification_date

    def __le__(self, other: 'LastModificationDate') -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date <= other._last_modification_date

    def __gt__(self, other: 'LastModificationDate') -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date > other._last_modification_date

    def __ge__(self, other: 'LastModificationDate') -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date >= other._last_modification_date

    def __ne__(self, other: 'LastModificationDate') -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date != other._last_modification_date

    def __str__(self: 'LastModificationDate') -> Union[None, str]:
        return self._last_modification_date

    def toJsonObj(self):
        return {
            "@type": "xsd:dateTimeStamp",
            "@value": self._last_modification_date
        }


class WithId:
    """
    Class helper to get json-ld "@id" thingies
    """
    _tmp: str = None

    def __init__(self, obj: Optional[Dict[str, str]]):
        if obj is None:
            return
        self._tmp = obj.get('@id')

    def str(self) -> Optional[str]:
        return self._tmp
