from dsp_tools.xmllib.models.dsp_base_resources import AnnotationResource
from dsp_tools.xmllib.models.resource import Resource
from dsp_tools.xmllib.models.root import XMLRoot
from dsp_tools.xmllib.value_checkers import is_bool_like
from dsp_tools.xmllib.value_converters import convert_to_bool_string


def test_xmllib() -> None:
    """
    This does NOT test the xmllib.
    This only tests if all dependencies used in the xmllib are shipped in the distribution.
    For this purpose, it is enough to import all modules of the xmllib.
    Indirect imports are okay, too, i.e. modules that are imported by modules that are imported here.
    """
    root = XMLRoot("0000", "my_onto")
    my_res = Resource.create_new("my_res", "restype", "label")
    if is_bool_like("0"):
        my_res.add_bool("my_prop", convert_to_bool_string("0"))
    my_res.add_file("my_file")
    annotation = AnnotationResource.create_new("res_id", "label", "annotation_of", ["comment1", "comment2"])
    root.add_resource(annotation)
    root.add_resource(my_res)
