import unittest
from jsonschema import validate
import json

from knora import Knora, Sipi
from models.project import Project
from models.langstring import Languages, LangStringParam, LangString
from models.connection import Connection, Error
from models.ontology import Ontology
from models.propertyclass import PropertyClass
from models.resourceclass import ResourceClass


class TestCreateOntology(unittest.TestCase):

    # @unittest.skip("not implemented")
    def test_create_ontology(self):
        server = "http://0.0.0.0:3333"
        sipi = "http://0.0.0.0:1024"
        email = "root@example.com"
        password = "test"
        projectcode = "00FE"
        ontoname = "KPT"

        with open("knora-schema.json") as s:
            schema = json.load(s)

        with open("doc-test-onto.json") as f:
            ontology = json.load(f)

        validate(ontology, schema)
        print("Ontology is syntactically correct and passed validation!")

        con = Connection(server)
        con.login(email, password)

        project = Project(
            con=con,
            shortcode=ontology["project"]["shortcode"],
            shortname=ontology["project"]["shortname"],
            longname=ontology["project"]["longname"],
            description=LangString(ontology["project"].get("descriptions")),
            keywords=set(ontology["project"].get("keywords")),
            selfjoin=False,
            status=True
        ).create()

        ontologies = ontology["project"]["ontologies"]
        for ontology in ontologies:
            print(ontology)
            last_modification_date, newontology = Ontology(
                con=con,
                project=project,
                label=ontology["label"],
                name=ontology["name"]
            ).create()
            newontology.print()

            #
            # First we create the empty resource classes
            #
            resclasses = ontology["resources"]
            newresclasses: Dict[str, ResourceClass] = {}
            for resclass in resclasses:
                resname = resclass.get("name")
                super_classes = resclass.get("super")
                if isinstance(super_classes, str):
                    super_classes = [super_classes]
                reslabel = LangString(resclass.get("labels"))
                rescomment = resclass.get("comment")
                if rescomment is not None:
                    rescomment = LangString(rescomment)
                try:
                    last_modification_date, newresclass = ResourceClass(
                        con=con,
                        context=newontology.context,
                        ontology_id=newontology.id,
                        name=resname,
                        superclasses=super_classes,
                        label=reslabel,
                        comment=rescomment
                    ).create(last_modification_date)
                except Error as err:
                    print("Creating resource class failed: " + err.message)
                    exit(105)
                newresclasses[newresclass.id] = newresclass
                if args.verbose is not None:
                    newresclass.print()

            #
            # Then we create the property classes
            #
            propclasses = ontology["properties"]
            newpropclasses: Dict[str, ResourceClass] = {}
            for propclass in propclasses:
                propname = propclass.get("name")
                proplabel = LangString(propclass.get("labels"))
                #
                # get the super-property/ies if defined. Valid forms are:
                #   - "prefix:superproperty" : fully qualified name of property in another ontology. The prefix has to
                #     be defined in the prefixes part.
                #   - "superproperty" : Use of super-property defined in the knora-api ontology
                #  if omitted, automatically "knora-api:hasValue" is assumed
                #
                if propclass.get("super") is not None:
                    super_props = list(map(lambda a: a if ':' in a else "knora-api:" + a, propclass["super"]))
                else:
                    super_props = ["knora-api:hasValue"]
                #
                # now we get the "object" if defined. Valid forms are:
                #  - "prefix:object_name" : fully qualified object. The prefix has to be defined in the prefixes part.
                #  - ":object_name" : The object is defined in the current ontology.
                #  - "object_name" : The object is defined in "knora-api"
                #
                if propclass.get("object") is not None:
                    tmp = propclass["object"].split(':')
                    if len(tmp) > 1:
                        if tmp[0]:
                            object = propclass["object"] # fully qualified name
                        else:
                            object = newontology.name + ':' + tmp[1]
                    else:
                        object = "knora-api:" + propclass["object"]
                else:
                    object = None

                if propclass.get("subject") is not None:
                    subject = propclass["subject"]
                else:
                    subject = None
                gui_element = propclass.get("gui_element")
                gui_attributes = propclass.get("gui_attributes")
                if gui_attributes is not None and gui_attributes.get("hlist") is not None:
                    gui_attributes['hlist'] = "<" + listrootnodes[gui_attributes['hlist']]["id"] + ">"
                propcomment = propclass.get("comment")
                if propcomment is not None:
                    propcomment = LangString(propcomment)
                else:
                    propcomment = "no comment given"
                try:
                    last_modification_date, newpropclass = PropertyClass(
                        con=con,
                        context=newontology.context,
                        label=proplabel,
                        name=propname,
                        ontology_id=newontology.id,
                        superproperties=super_props,
                        object=object,
                        subject=subject,
                        gui_element="salsah-gui:" + gui_element,
                        gui_attributes=gui_attributes,
                        comment=propcomment
                    ).create(last_modification_date)
                except Error as err:
                    print("Creating property class failed: " + err.message)
                    exit(105)
                newpropclasses[newpropclass.id] = newpropclass
                if args.verbose is not None:
                    newpropclass.print()

            #
            # Add cardinalities
            #
            switcher = {
                "1": Cardinality.C_1,
                "0-1": Cardinality.C_0_1,
                "0-n": Cardinality.C_0_n,
                "1-n": Cardinality.C_1_n
            }
            for resclass in resclasses:
                for cardinfo in resclass["cardinalities"]:
                    rc = newresclasses.get(newontology.id + '#' + resclass["name"])
                    cardinality = switcher[cardinfo["cardinality"]]
                    tmp = cardinfo["propname"].split(':')
                    if len(tmp) > 1:
                        if tmp[0]:
                            propid = cardinfo["propname"] # fully qualified name
                        else:
                            propid = newontology.name + ':' + tmp[1]
                    else:
                        propid = "knora-api:" + cardinfo["propname"]
                    last_modification_date = rc.addProperty(propid, cardinality, last_modification_date)

        pass

if __name__ == "__main__":
    print("goes here")
    unittest.main()
else:
    print("goes elswhere")
