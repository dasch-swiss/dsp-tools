from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.dsp_base_resources import AnnotationResource
from dsp_tools.xmllib.models.resource import Resource
from dsp_tools.xmllib.models.root import XMLRoot


def test_root() -> None:
    root = XMLRoot.create_new("0000", "test")

    # add_resource
    anno_res = AnnotationResource("annoID", "label", "id1", ["comment"], Permissions.OPEN)
    anno_res.add_comment("comment2")
    root.add_resource(anno_res)
    assert len(root.resources) == 1

    # add_resource_multiple
    many_resources = []
    res1 = Resource.create_new("id1", ":Restype", "label")
    res1.add_bool(":boolProp", True)
    many_resources.append(res1)
    res2 = Resource.create_new("id2", ":Restype", "label")
    res2.add_color(":colorProp", "#87s3sb")
    many_resources.append(res2)
    root.add_resource_multiple(many_resources)
    assert len(root.resources) == 3

    root.add_resource_multiple([])
    assert len(root.resources) == 3

    # add_resource_optional
    no_resource = None
    root.add_resource_optional(no_resource)
    assert len(root.resources) == 3
