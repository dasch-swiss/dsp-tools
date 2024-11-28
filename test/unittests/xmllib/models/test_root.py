from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.dsp_base_resources import AnnotationResource
from dsp_tools.xmllib.models.resource import Resource
from dsp_tools.xmllib.models.root import XMLRoot


def test_root() -> None:
    xml_root = XMLRoot.create_new("0000", "test")

    # add_resource
    anno_res = AnnotationResource("annoID", "label", "id1", ["comment"], Permissions.OPEN)
    anno_res.add_comment("comment2")
    xml_root.add_resource(anno_res)
    assert len(xml_root.resources) == 1

    # add_resource_multiple
    many_resources = []
    res1 = Resource.create_new("id1", ":Restype", "label")
    res1.add_bool(":boolProp", True)
    many_resources.append(res1)
    res2 = Resource.create_new("id2", ":Restype", "label")
    res2.add_color(":colorProp", "#5b24bf")
    many_resources.append(res2)
    xml_root.add_resource_multiple(many_resources)
    assert len(xml_root.resources) == 3

    xml_root.add_resource_multiple([])
    assert len(xml_root.resources) == 3

    # add_resource_optional
    no_resource = None
    xml_root.add_resource_optional(no_resource)
    assert len(xml_root.resources) == 3

    serialised = xml_root.serialise()
    annotation = list(serialised.iterdescendants(tag="{https://dasch.swiss/schema}annotation"))
    assert len(annotation) == 1
    general_resources = list(serialised.iterdescendants(tag="{https://dasch.swiss/schema}resource"))
    assert len(general_resources) == 2
