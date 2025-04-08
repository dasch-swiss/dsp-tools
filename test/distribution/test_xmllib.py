from dsp_tools.xmllib import LicenseRecommended
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.res import Resource
from dsp_tools.xmllib.models.root import XMLRoot
from dsp_tools.xmllib.value_checkers import is_bool_like
from dsp_tools.xmllib.value_converters import convert_to_bool


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
        my_res.add_bool("my_prop", convert_to_bool("0"))
    my_res.add_file("my_file", LicenseRecommended.CC.BY, "copy", ["auth"])
    region = RegionResource.create_new("res_id", "label", "region_of")
    root.add_resource(region)
    root.add_resource(my_res)
