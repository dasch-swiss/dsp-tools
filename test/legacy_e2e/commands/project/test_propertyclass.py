import pytest

from dsp_tools.commands.project.models.ontology import Ontology
from dsp_tools.commands.project.models.propertyclass import PropertyClass
from dsp_tools.models.langstring import LangString
from dsp_tools.models.langstring import Languages
from dsp_tools.utils.authentication_client_live import AuthenticationClientLive
from dsp_tools.utils.connection_live import ConnectionLive


def test_PropertyClass_create() -> None:
    auth = AuthenticationClientLive("http://0.0.0.0:3333", "root@example.com", "test")
    con = ConnectionLive("http://0.0.0.0:3333", auth)

    # Create a test ontology
    onto = Ontology(
        con=con,
        project="http://rdfh.ch/projects/0001",
        name="onto-1",
        label="onto-label",
    ).create()
    assert onto.iri is not None
    last_modification_date = onto.lastModificationDate

    # create new property class
    prop_name = "MyPropClassName"
    prop_label = LangString({Languages.DE: "MyPropClassLabel"})
    prop_comment = LangString({Languages.DE: "This is a property class for testing"})
    last_modification_date, property_class = PropertyClass(
        con=con,
        context=onto.context,
        name=prop_name,
        ontology_id=onto.iri,
        rdf_object="TextValue",
        label=prop_label,
        comment=prop_comment,
    ).create(last_modification_date)

    assert property_class.iri is not None
    assert property_class.name == prop_name
    assert property_class.label["de"] == prop_label["de"]
    assert property_class.comment["de"] == prop_comment["de"]


if __name__ == "__main__":
    pytest.main([__file__])
