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
    DATETIME = 1  # TODO: change in ontology. should be `date`
    STRING_OR_URL = 2
    PLACE = 3
    PERSON_OR_ORGANIZATION = 4
    GRANT = 5
    DATA_MANAGEMENT_PLAN = 6
    URL = 7



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
                                    "This is a test project. All properties have been used to test these. You will just describe your project briefly.",
                                    Datatype.STRING,
                                    Cardinality.ONE)
        self.keywords = Property("Keywords",
                                 "Keywords and tags",
                                 "mathematics, science, history of science, history of mathematics. Use the plus sign to have a new field for each key word.",
                                 Datatype.STRING,
                                 Cardinality.ONE_TO_UNBOUND)  # TODO: implement plus button in GUI to add keywords

        self.discipline = Property("Discipline",
                                   "Discipline and research fields from UNESCO nomenclature: https://skos.um.es/unesco6/?l=en or from http://www.snf.ch/SiteCollectionDocuments/allg_disziplinenliste.pdf",
                                   "http://skos.um.es/unesco6/11",
                                   Datatype.STRING_OR_URL,
                                   Cardinality.ONE_TO_UNBOUND)
        # TODO: Start date
        self.startDate = Property("Start Date",
                                  "The date when the project started, e. g. when funding was granted.",
                                  "2000-07-26T21:32:52",
                                  Datatype.DATETIME,
                                  Cardinality.ONE)

        # TODO: End date
        self.endDate = Property("End Date",
                                "The date when the project was finished, e. g. when the last changes to the project data where completed.",
                                "2000-07-26T21:32:52",
                                Datatype.DATETIME,
                                Cardinality.ONE)

        self.temporalCoverage = Property("Temporal coverage",
                            "Temporal coverage of the project from http://perio.do/en/ or https://chronontology.dainst.org/",
                            "http://chronontology.dainst.org/period/Ef9SyESSafJ1",
                            Datatype.STRING_OR_URL,
                            Cardinality.ONE_TO_UNBOUND)

        self.spacialCoverage = Property("Spacial coverage",
                            "Spatial coverage of the project from Geonames URL: https://www.geonames.org/ and or from Pleiades URL: https://pleiades.stoa.org/places",
                            "https://www.geonames.org/6255148/europe.html",
                            Datatype.PLACE,
                            Cardinality.ONE_TO_UNBOUND)

        self.funder = Property("Funder",
                            "Funding person or institution of the project",
                            "",
                            Datatype.PERSON_OR_ORGANIZATION,
                            Cardinality.ONE_TO_UNBOUND)

        self.grant = Property("Grant",
                            "Grant of the project",
                            "",
                            Datatype.GRANT)

        self.url = Property("URL",
                            "Landing page or Website of the project. We recommend DSP Landing Page",
                            "https://test.dasch.swiss/",
                            Datatype.URL,
                            Cardinality.ONE_TO_TWO)

        self.shortcode = Property("Shortcode",
                            "Internal shortcode of the project",
                            "0000",
                            Datatype.STRING,
                            Cardinality.ONE)

        self.alternateName = Property("Alternate Name",
                            "Alternative name of the project, e.g. in case of an overly long official name",
                            "Another Title",
                            Datatype.STRING)

        self.dataManagementPlan = Property("Data Management Plan",
                            "Data Management Plan of the project",
                            "",
                            Datatype.DATA_MANAGEMENT_PLAN,
                            Cardinality.ZERO_OR_ONE)

        self.publication = Property("Publication",
                            "Publications produced during the lifetime of the project",
                            "Doe, J. (2000). A Publication.",
                            Datatype.STRING)

        self.contactPoint = Property("Contact Point",
                            "Contact information",
                            "",
                            Datatype.PERSON_OR_ORGANIZATION,
                            Cardinality.ZERO_OR_ONE)

    def get_properties(self):
        return [
            self.name,
            self.description,
            self.keywords,
            self.discipline,
            self.startDate,
            self.endDate,
            self.temporalCoverage,
            self.spacialCoverage,
            self.funder,
            self.grant,
            self.url,
            self.shortcode,
            self.alternateName,
            self.dataManagementPlan,
            self.publication,
            self.contactPoint
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

    def __init__(self, name: str, description: str, example: str, datatype: Datatype.STRING,
                 cardinality=Cardinality.UNBOUND, value=None):
        self.name = name
        self.description = description
        self.example = example
        self.datatype = datatype
        self.cardinality = cardinality
        self.value = value
