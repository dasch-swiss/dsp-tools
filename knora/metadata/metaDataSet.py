from enum import Enum

"""
The Classes defined here aim to represent a metadata-set, closely following the metadata ontology.
"""


class Cardinality(Enum):
    """
    A set of cardinalities that may be used for properties.
    """
    UNBOUND = 0
    ONE = 1
    ZERO_OR_ONE = 2
    ONE_TO_UNBOUND = 3
    ONE_TO_TWO = 4


class Datatype(Enum):
    """
    A set of cardinalities that may be used for properties.
    """
    STRING = 0

class MetaDataSet:
    """ Representation of a data set.

    This class represents a data set of project metadata.
    
    It holds the following properties:
    - index: the index of the dataset in the UI (list item).
      Note: in some case, we'll need to make sure this stays correct
    - name: the repo/project name.
      Typically the name of the folder that was selected.
    - path: the full path of the folder that was selected.
    - files: a list of relevant files in the folder
    - project: a `metaDataSet.Project` representation of the actual metadata (as specified by the ontology).

    At a later stage, this class should be able to return a representation of its data in form of an RDF graph.
    """
    
    @property
    def index(self):
        return self.__index
    @index.setter
    def index(self, i: int):
        self.__index = i

    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def path(self):
        return self.__path
    @path.setter
    def path(self, path: str):
        self.__path = path

    @property
    def files(self):
        return self.__files
    @files.setter
    def files(self, files: list):
        self.__files = files

    def __init__(self, index: int, name: str, path: str):
        self.index = index
        self.name = name
        self.path = path
        self.files = []
        self.project = Project(name)

    def __str__(self):
        return str({
            "index": self.index,
            "name": self.name,
            "path": self.path,
            "files": self.files,
            "metadata": [
                self.project
            ]
        })
        
    # TODO: add a "convert_to_rdf()" method or something like this


class Project():
    """
    Project shape.

    Corresponds to `dsp-repo:Project` in our ontology.
    """

    # name = None
    # description = None
    
    def __init__(self, name):
        self.name = Property("Name", 
                             "The name of the Project", 
                             "Test Project",
                             Datatype.STRING, 
                             Cardinality.ONE,
                             name)
        self.description = Property("Description",
                                    "Description of the Project",
                                    "",  # TODO: add example
                                    Datatype.STRING, 
                                    Cardinality.ONE)
        self.keywords = Property("Keywords",
                                "Keywords and tags",
                                "",  # TODO: add example
                                Datatype.STRING,
                                Cardinality.ONE_TO_UNBOUND)
        self.discipline = Property("Discipline",
                                "Discipline and research fields from UNESCO nomenclature: https://skos.um.es/unesco6/?l=en or from http://www.snf.ch/SiteCollectionDocuments/allg_disziplinenliste.pdf",
                                "",  # TODO: add example
                                "xsd:string / sh:IRI", # TODO: check if that's correct!
                                Cardinality.ONE_TO_UNBOUND)
        # TODO: Start date
        # TODO: End date
        # TODO: Temporal Coverage
        # TODO: Spacial Coverage
        # TODO: Funder
        # TODO: Grant
        # etc.
        self.url = Property("URL",
                            "Landing page or Website of the project. We recommend DSP Landing Page",
                            "",  # TODO: add example
                            "xsd:string / sh:IRI",
                            Cardinality.ONE_TO_TWO)

    def get_properties(self):
        return [
            self.name,
            self.description,
            self.keywords,
            self.discipline,
            # TODO: more
            self.url
        ]

# TODO: dsp-repo:Dataset
# TODO: dsp-repo:Person
# TODO: dsp-repo:Organization
# TODO: dsp-repo:Grant (?)
# TODO: dsp-repo:DataManagementPlan


class Property():
    """
    General representation of a property.

    Corresponds to `sh:property`
    """

    # name = None
    # description = None
    # datatype = None
    # cardinality = None

    def __init__(self, name: str, description: str, example: str, datatype: Datatype.STRING, cardinality=Cardinality.UNBOUND, value=None):
        self.name = name
        self.description = description
        self.example = example
        self.datatype = datatype
        self.cardinality = cardinality
        self.value = value
