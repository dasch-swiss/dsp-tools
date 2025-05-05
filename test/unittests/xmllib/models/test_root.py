from lxml import etree

from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.licenses.recommended import LicenseRecommended
from dsp_tools.xmllib.models.res import Resource
from dsp_tools.xmllib.models.root import XMLRoot
from dsp_tools.xmllib.models.root import _make_authorship_lookup
from dsp_tools.xmllib.models.root import _serialise_authorship


def test_root_add_resources() -> None:
    xml_root = XMLRoot.create_new("0000", "test")

    # add_resource
    region_res = RegionResource.create_new("regionID", "label", "id1")
    region_res.add_rectangle((0.1, 0.1), (0.2, 0.2))
    xml_root.add_resource(region_res)
    assert len(xml_root.resources) == 1

    # add_resource_multiple
    many_resources = [Resource.create_new("id1", ":Restype", "label"), Resource.create_new("id2", ":Restype", "label")]
    xml_root.add_resource_multiple(many_resources)
    assert len(xml_root.resources) == 3

    xml_root.add_resource_multiple([])
    assert len(xml_root.resources) == 3

    # add_resource_optional
    no_resource = None
    xml_root.add_resource_optional(no_resource)
    assert len(xml_root.resources) == 3

    serialised = xml_root.serialise()
    region = list(serialised.iterdescendants(tag="{https://dasch.swiss/schema}region"))
    assert len(region) == 1
    general_resources = list(serialised.iterdescendants(tag="{https://dasch.swiss/schema}resource"))
    assert len(general_resources) == 2


def test_make_authorship_lookup() -> None:
    res1 = Resource.create_new("id1", ":Restype", "label").add_file(
        "file.jpg", LicenseRecommended.DSP.UNKNOWN, "copy", ["auth", "auth1"]
    )
    res2 = Resource.create_new("id2", ":Restype", "label").add_file(
        "file.jpg", LicenseRecommended.DSP.UNKNOWN, "copy", ["auth2"]
    )
    res3 = Resource.create_new("id2", ":Restype", "label").add_file(
        "file.jpg", LicenseRecommended.DSP.UNKNOWN, "copy", ["auth2"]
    )
    region_res = RegionResource.create_new("regionID", "label", "id1")
    result = _make_authorship_lookup([res1, res2, res3, region_res])
    assert set(result.lookup.keys()) == {("auth", "auth1"), tuple(["auth2"])}


def test_serialise_authorship() -> None:
    lookup = {("auth", "auth1"): "authorship_1", tuple(["auth2"]): "authorship_2"}
    expected = [
        b'<authorship xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'id="authorship_1"><author>auth</author><author>auth1</author></authorship>',
        b'<authorship xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'id="authorship_2"><author>auth2</author></authorship>',
    ]
    serialised = _serialise_authorship(lookup)
    result = sorted([etree.tostring(x) for x in serialised])
    assert len(result) == len(expected)
    for res, ex in zip(result, expected):
        assert res == ex
