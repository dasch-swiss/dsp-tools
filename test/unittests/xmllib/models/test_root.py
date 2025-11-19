# mypy: disable-error-code="no-untyped-def,comparison-overlap"
import warnings

import pytest
import regex
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.internal.constants import DASCH_SCHEMA
from dsp_tools.xmllib.internal.type_aliases import AnyResource
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.licenses.recommended import LicenseRecommended
from dsp_tools.xmllib.models.permissions import Permissions
from dsp_tools.xmllib.models.res import Resource
from dsp_tools.xmllib.models.root import XMLRoot
from dsp_tools.xmllib.models.root import _make_authorship_lookup
from dsp_tools.xmllib.models.root import _serialise_authorship


@pytest.fixture
def resource_1() -> Resource:
    return Resource.create_new("id_1", ":ResType", "lbl")


class TestAddResource:
    def test_ok(self, resource_1):
        root = XMLRoot.create_new("0000", "test")
        with warnings.catch_warnings(record=True) as caught_warnings:
            root = root.add_resource(resource_1)
        assert len(caught_warnings) == 0
        assert len(root.resources) == 1
        assert root._res_id_to_type_lookup == {"id_1": [":ResType"]}

    def test_optional_none(self):
        root = XMLRoot.create_new("0000", "test")
        with warnings.catch_warnings(record=True) as caught_warnings:
            root = root.add_resource_optional(None)
        assert len(caught_warnings) == 0
        assert len(root.resources) == 0
        assert not root._res_id_to_type_lookup

    def test_optional_with_resource(self, resource_1):
        root = XMLRoot.create_new("0000", "test")
        with warnings.catch_warnings(record=True) as caught_warnings:
            root = root.add_resource_optional(resource_1)
        assert len(caught_warnings) == 0
        assert len(root.resources) == 1
        assert root._res_id_to_type_lookup == {"id_1": [":ResType"]}

    def test_multiple(self, resource_1):
        root = XMLRoot.create_new("0000", "test")
        resource_2 = Resource.create_new("id_2", ":ResType2", "lbl")
        with warnings.catch_warnings(record=True) as caught_warnings:
            root = root.add_resource_multiple([resource_1, resource_2])
        assert len(caught_warnings) == 0
        assert len(root.resources) == 2
        assert root._res_id_to_type_lookup == {"id_1": [":ResType"], "id_2": [":ResType2"]}

    def test_multiple_empty(self):
        root = XMLRoot.create_new("0000", "test")
        with warnings.catch_warnings(record=True) as caught_warnings:
            root = root.add_resource_multiple([])
        assert len(caught_warnings) == 0
        assert len(root.resources) == 0
        assert not root._res_id_to_type_lookup

    def test_duplicate_id_warnings(self, resource_1):
        root = XMLRoot.create_new("0000", "test")
        root = root.add_resource(resource_1)
        res_duplicate_id = VideoSegmentResource.create_new("id_1", "lbl", "segment_of", 1, 2)
        msg = regex.escape(
            "Resource ID 'id_1' | Field 'Resource ID' | The ID for this resource of type 'VideoSegmentResource' "
            "is already used by resource(s) of the following type(s): ':ResType'."
        )
        with pytest.warns(XmllibInputWarning, match=msg):
            root = root.add_resource(res_duplicate_id)
        assert len(root.resources) == 2
        assert root._res_id_to_type_lookup == {"id_1": [":ResType", "VideoSegmentResource"]}

    def test_duplicate_id_warnings_with_multiple(self, resource_1):
        root = XMLRoot.create_new("0000", "test")
        res_duplicate_id = Resource.create_new("id_1", ":ResType2", "lbl")
        msg = regex.escape(
            "Resource ID 'id_1' | Field 'Resource ID' | The ID for this resource of type ':ResType2' "
            "is already used by resource(s) of the following type(s): ':ResType'."
        )
        with pytest.warns(XmllibInputWarning, match=msg):
            root = root.add_resource_multiple([resource_1, res_duplicate_id])
        assert len(root.resources) == 2
        assert root._res_id_to_type_lookup == {"id_1": [":ResType", ":ResType2"]}


class TestSerialise:
    def test_regular_resource(self):
        xml_root = XMLRoot.create_new("0000", "test")
        xml_root.add_resource(
            Resource.create_new(
                "res_id",
                ":Restype",
                "lbl",
            ).add_bool(":boolProp", True, comment="cmnt")
        )
        serialised = xml_root.serialise()
        found = list(serialised.iterdescendants(tag=f"{DASCH_SCHEMA}resource"))
        assert len(found) == 1
        resource = found[0]
        res_attribs = {"label": "lbl", "restype": ":Restype", "id": "res_id"}
        assert resource.attrib == res_attribs
        value_list = list(resource.iterchildren())
        assert len(value_list) == 1
        bool_prop = value_list[0]
        assert bool_prop.tag == f"{DASCH_SCHEMA}boolean-prop"
        assert bool_prop.attrib == {"name": ":boolProp"}
        bool_prop_values = list(bool_prop.iterchildren())
        assert len(bool_prop_values) == 1
        prop_val = bool_prop_values[0]
        assert prop_val.tag == f"{DASCH_SCHEMA}boolean"
        assert prop_val.text == "true"
        assert prop_val.attrib == {"comment": "cmnt"}

    def test_region(self):
        xml_root = XMLRoot.create_new("0000", "test")
        xml_root.add_resource(
            RegionResource.create_new(
                "region",
                "lbl",
                "region_of_val",
                Permissions.PRIVATE,
            ).add_rectangle((0.1, 0.1), (0.2, 0.2))
        )
        serialised = xml_root.serialise()
        found = list(serialised.iterdescendants(tag=f"{DASCH_SCHEMA}region"))
        assert len(found) == 1
        resource = found[0]
        res_attribs = {"label": "lbl", "id": "region", "permissions": "private"}
        assert resource.attrib == res_attribs
        assert len(resource) == 3
        # Check color
        all_colors = list(resource.iterchildren(tag=f"{DASCH_SCHEMA}color-prop"))
        assert len(all_colors) == 1
        color_prop = all_colors[0]
        assert color_prop.attrib == {"name": "hasColor"}
        color_child = next(color_prop.iterchildren())
        assert color_child.text == "#5b24bf"
        assert color_child.attrib == {"permissions": "private"}
        # Check is region of
        all_resptrs = list(resource.iterchildren(tag=f"{DASCH_SCHEMA}resptr-prop"))
        assert len(all_resptrs) == 1
        resptr_prop = all_resptrs[0]
        assert resptr_prop.attrib == {"name": "isRegionOf"}
        resptr_child = next(resptr_prop.iterchildren())
        assert resptr_child.text == "region_of_val"
        assert resptr_child.attrib == {"permissions": "private"}
        # Check geometry
        all_geo = list(resource.iterchildren(tag=f"{DASCH_SCHEMA}geometry-prop"))
        assert len(all_geo) == 1
        geo_prop = all_geo[0]
        assert geo_prop.attrib == {"name": "hasGeometry"}
        geo_child = next(geo_prop.iterchildren())
        assert geo_child.text
        assert len(geo_child.text) > 0
        assert geo_child.attrib == {"permissions": "private"}

    def test_link_resource(self):
        xml_root = XMLRoot.create_new("0000", "test")
        xml_root.add_resource(
            LinkResource.create_new(
                "link_id",
                "lbl",
                ["link1", "link2"],
            ).add_comment("cmnt", Permissions.PRIVATE)
        )
        serialised = xml_root.serialise()
        found = list(serialised.iterdescendants(tag=f"{DASCH_SCHEMA}link"))
        assert len(found) == 1
        resource = found[0]
        res_attribs = {"label": "lbl", "id": "link_id"}
        assert resource.attrib == res_attribs
        vals = list(resource.iterchildren())
        assert len(vals) == 2
        # link tos
        all_resptrs = list(resource.iterchildren(tag=f"{DASCH_SCHEMA}resptr-prop"))
        assert len(all_resptrs) == 1
        resptr = all_resptrs[0]
        assert resptr.attrib == {"name": "hasLinkTo"}
        for v in resptr.iterchildren():
            assert v.tag == f"{DASCH_SCHEMA}resptr"
            assert v.text in ["link1", "link2"]
            assert not v.attrib
        # comment
        all_text = list(resource.iterchildren(tag=f"{DASCH_SCHEMA}text-prop"))
        assert len(all_text) == 1
        text_prop = all_text[0]
        assert text_prop.attrib == {"name": "hasComment"}
        text_child = next(text_prop.iterchildren())
        assert text_child.text == "cmnt"
        assert text_child.attrib == {"permissions": "private", "encoding": "xml"}

    def test_audio_segment(self):
        xml_root = XMLRoot.create_new("0000", "test")
        xml_root.add_resource(
            AudioSegmentResource.create_new("audio_id", "lbl", "segment_of", 1, 2)
            .add_title("title")
            .add_comment("cmnt")
            .add_description("desc")
            .add_keyword("keywrd")
            .add_relates_to("relates_to")
        )
        serialised = xml_root.serialise()
        found = list(serialised.iterdescendants(tag=f"{DASCH_SCHEMA}audio-segment"))
        assert len(found) == 1
        resource = found[0]
        res_attribs = {"label": "lbl", "id": "audio_id"}
        assert resource.attrib == res_attribs
        assert len(resource) == 7
        segment_of = next(resource.iter(tag=f"{DASCH_SCHEMA}isSegmentOf"))
        assert not segment_of.attrib
        assert segment_of.text == "segment_of"
        bounds = next(resource.iter(tag=f"{DASCH_SCHEMA}hasSegmentBounds"))
        assert not bounds.text
        assert bounds.attrib == {"segment_start": "1", "segment_end": "2"}
        title = next(resource.iter(tag=f"{DASCH_SCHEMA}hasTitle"))
        assert not title.attrib
        assert title.text == "title"
        comment = next(resource.iter(tag=f"{DASCH_SCHEMA}hasComment"))
        assert not comment.attrib
        assert comment.text == "cmnt"
        description = next(resource.iter(tag=f"{DASCH_SCHEMA}hasDescription"))
        assert not description.attrib
        assert description.text == "desc"
        keywrd = next(resource.iter(tag=f"{DASCH_SCHEMA}hasKeyword"))
        assert not keywrd.attrib
        assert keywrd.text == "keywrd"
        relates_to = next(resource.iter(tag=f"{DASCH_SCHEMA}relatesTo"))
        assert not relates_to.attrib
        assert relates_to.text == "relates_to"

    def test_video_segment_with_permissions(self):
        xml_root = XMLRoot.create_new("0000", "test")
        xml_root.add_resource(
            VideoSegmentResource.create_new(
                "video_id",
                "lbl",
                "segment_of",
                1,
                2,
                permissions=Permissions.PRIVATE,
            )
        )
        serialised = xml_root.serialise()
        found = list(serialised.iterdescendants(tag=f"{DASCH_SCHEMA}video-segment"))
        assert len(found) == 1
        resource = found[0]
        res_attribs = {"label": "lbl", "id": "video_id", "permissions": "private"}
        assert resource.attrib == res_attribs
        assert len(resource) == 2
        segment_of = next(resource.iter(tag=f"{DASCH_SCHEMA}isSegmentOf"))
        assert segment_of.attrib == {"permissions": "private"}
        assert segment_of.text == "segment_of"
        bounds = next(resource.iter(tag=f"{DASCH_SCHEMA}hasSegmentBounds"))
        assert not bounds.text
        assert bounds.attrib == {"segment_start": "1", "segment_end": "2", "permissions": "private"}


class TestSerialiseDeprecatedPermissions:
    def test_resource_attributes(self) -> None:
        xml_root = XMLRoot.create_new("0000", "test")
        with warnings.catch_warnings(record=True):
            resources = [
                Resource.create_new("r1", ":typ", "lbl", Permissions.PUBLIC),
                Resource.create_new("r2", ":typ", "lbl", Permissions.PRIVATE),
                Resource.create_new("r3", ":typ", "lbl", Permissions.LIMITED_VIEW),
                Resource.create_new("r4", ":typ", "lbl", Permissions.OPEN),
                Resource.create_new("r5", ":typ", "lbl", Permissions.RESTRICTED),
                Resource.create_new("r6", ":typ", "lbl", Permissions.RESTRICTED_VIEW),
            ]
            xml = xml_root.add_resource_multiple(resources).serialise()
        res_attributes = [perm for x in xml if (perm := x.attrib.get("permissions"))]
        expected = ["public", "private", "limited_view", "open", "restricted", "restricted-view"]
        assert res_attributes == expected

    def test_only_new_permissions(self) -> None:
        xml_root = XMLRoot.create_new("0000", "test")
        spec = Permissions.PROJECT_SPECIFIC_PERMISSIONS
        publ = Permissions.PUBLIC
        priv = Permissions.PRIVATE
        lmtd = Permissions.LIMITED_VIEW
        with warnings.catch_warnings(record=True) as catched_warnings:
            resources: list[AnyResource] = [
                Resource.create_new("r1", ":typ", "lbl").add_bool(":prp", True),
                Resource.create_new("r2", ":typ", "lbl", spec).add_bool(":prp", True, spec),
                Resource.create_new("r3", ":typ", "lbl", publ).add_bool(":prp", True, publ),
                Resource.create_new("r4", ":typ", "lbl", priv).add_bool(":prp", True, priv),
                Resource.create_new("r5", ":typ", "lbl", lmtd).add_bool(":prp", True, lmtd),
                RegionResource.create_new("r6", "lbl", "tg").add_circle((1, 1), (1, 1)).add_comment("c"),
                RegionResource.create_new("r7", "lbl", "tg", spec).add_circle((1, 1), (1, 1)).add_comment("c", spec),
                LinkResource.create_new("r8", "lbl", ["tg"]).add_comment("c"),
                LinkResource.create_new("r9", "lbl", ["tg"], publ).add_comment("c", publ),
                AudioSegmentResource.create_new("r10", "lbl", "tg", 1, 2).add_comment("c"),
                AudioSegmentResource.create_new("r11", "lbl", "tg", 1, 2, priv).add_comment("c", priv),
                VideoSegmentResource.create_new("r12", "lbl", "tg", 1, 2).add_comment("c"),
                VideoSegmentResource.create_new("r13", "lbl", "tg", 1, 2, lmtd).add_comment("c", lmtd),
            ]
            xml = xml_root.add_resource_multiple(resources).serialise()
        assert len(catched_warnings) == 0
        serialised_permission_header_ids = [x.attrib["id"] for x in xml if str(x.tag).endswith("permissions")]
        assert unordered(serialised_permission_header_ids) == ["public", "private", "limited_view"]

    def test_old_and_new_permissions(self) -> None:
        xml_root = XMLRoot.create_new("0000", "test")
        _publ = Permissions.PUBLIC
        _open = Permissions.OPEN
        with warnings.catch_warnings(record=True) as catched_warnings:
            xml_root.add_resource(Resource.create_new("r1", ":typ", "lbl", _publ).add_bool(":prp", True, _open))
            xml = xml_root.serialise()
        assert len(catched_warnings) == 1
        msg = str(catched_warnings[0].message)
        assert "Your data contains old permissions. Please migrate to the new ones" in msg
        serialised_permission_header_ids = [x.attrib["id"] for x in xml if str(x.tag).endswith("permissions")]
        expected = ["public", "private", "limited_view", "open", "restricted", "restricted-view"]
        assert unordered(serialised_permission_header_ids) == expected

    def test_only_old_permissions(self) -> None:
        xml_root = XMLRoot.create_new("0000", "test")
        _open = Permissions.OPEN
        _rstr = Permissions.RESTRICTED
        _view = Permissions.RESTRICTED_VIEW
        resources: list[AnyResource] = [
            Resource.create_new("r1", ":typ", "lbl", _open).add_bool(":prp", True, _open),
            Resource.create_new("r2", ":typ", "lbl", _rstr).add_bool(":prp", True, _rstr),
            Resource.create_new("r3", ":typ", "lbl", _view).add_bool(":prp", True, _view),
            RegionResource.create_new("r4", "lbl", "tg", _open).add_circle((1, 1), (1, 1)).add_comment("c", _open),
            LinkResource.create_new("r5", "lbl", ["tg"], _rstr).add_comment("c", _rstr),
            AudioSegmentResource.create_new("r6", "lbl", "tg", 1, 2, _view).add_comment("c", _view),
            VideoSegmentResource.create_new("r7", "lbl", "tg", 1, 2, _view).add_comment("c", _view),
        ]
        for res in resources:
            with warnings.catch_warnings(record=True) as catched_warnings:
                xml = xml_root.add_resource(res).serialise()
            assert len(catched_warnings) == 1
            msg = str(catched_warnings[0].message)
            assert "Your data contains old permissions. Please migrate to the new ones" in msg
            serialised_permission_header_ids = [x.attrib["id"] for x in xml if str(x.tag).endswith("permissions")]
            assert unordered(serialised_permission_header_ids) == ["open", "restricted", "restricted-view"]


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
    region = list(serialised.iterdescendants(tag=f"{DASCH_SCHEMA}region"))
    assert len(region) == 1
    general_resources = list(serialised.iterdescendants(tag=f"{DASCH_SCHEMA}resource"))
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
    res_none = Resource.create_new("id2", ":Restype", "label").add_file(
        "file.jpg",
    )
    region_res = RegionResource.create_new("regionID", "label", "id1")
    result = _make_authorship_lookup([res1, res2, res3, region_res, res_none])
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
